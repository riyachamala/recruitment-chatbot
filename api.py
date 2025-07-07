import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi import FastAPI
from fastapi import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Dict, Any
import re
from collections import Counter

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import ConversationalRetrievalChain
from langchain.chains import RetrievalQA

# load all API keys from .env file
load_dotenv()

app = FastAPI() # initialize FastAPI to wrap chatbot

# CORS middleware to support FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize the embedding model (using HuggingFace to replace OpenAI's embedding model)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# establish connection from the vector reps (embeddings) to the Pinecone index
vectorstore = PineconeVectorStore(
    index_name=os.environ["INDEX_NAME"],
    embedding=embeddings
)

# Initialize the groq LLM
chat = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=1, # this indicates that the response will be straightforward, with little to no response creativity
    verbose=True
)

# set up the actual retrieval system (this particular one allows for some form of memory)
qa = ConversationalRetrievalChain.from_llm(
    llm=chat,
    retriever=vectorstore.as_retriever()
)

# create a memory bank to create "stateful" conversations
chat_history = []

# create a question class to define the requests
class Question(BaseModel):
    question: str # define that question type is STR

# define the chat dataflow
@app.post("/chat")
def chat_endpoint(q: Question):
    global chat_history
    res = qa.invoke({
        "question": q.question,
        "chat_history": chat_history
    })

    chat_history.append((res["question"], res["answer"]))

    return {"answer": res["answer"]}


def extract_skills_and_keywords(text: str, jd_text: str) -> Dict[str, Any]:
    """Extract quantitative metrics from resume text"""
    # Common technical skills
    tech_skills = [
        'python', 'javascript', 'java', 'react', 'angular', 'vue', 'node.js',
        'sql', 'postgresql', 'mysql', 'mongodb', 'aws', 'azure', 'gcp',
        'docker', 'kubernetes', 'jenkins', 'git', 'tensorflow', 'pytorch',
        'machine learning', 'data science', 'api', 'rest', 'graphql'
    ]
    
    # Extract years of experience
    exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
    exp_matches = re.findall(exp_pattern, text.lower())
    years_experience = max([int(x) for x in exp_matches]) if exp_matches else 0
    
    # Count technical skills mentioned
    text_lower = text.lower()
    jd_lower = jd_text.lower()
    
    skills_found = [skill for skill in tech_skills if skill in text_lower]
    jd_skills = [skill for skill in tech_skills if skill in jd_lower]
    matching_skills = [skill for skill in skills_found if skill in jd_skills]
    
    # Count education mentions
    education_keywords = ['degree', 'bachelor', 'master', 'phd', 'university', 'college']
    education_count = sum(1 for keyword in education_keywords if keyword in text_lower)
    
    # Count project mentions
    project_keywords = ['project', 'built', 'developed', 'created', 'implemented']
    project_mentions = sum(1 for keyword in project_keywords if keyword in text_lower)
    
    return {
        'years_experience': years_experience,
        'skills_found': skills_found,
        'matching_skills': matching_skills,
        'skill_match_ratio': len(matching_skills) / len(jd_skills) if jd_skills else 0,
        'education_mentions': education_count,
        'project_mentions': project_mentions,
        'total_skills': len(skills_found)
    }


@app.post("/analyze")
async def analyze(job_description: dict):
    jd_text = job_description.get("job_description", "")
    
    # Get similarity search results with scores
    jd_results = vectorstore.similarity_search_with_score(jd_text, k=15)

    if not jd_results:
        return {
            "best_resume_id": "unknown",
            "explanation": "No resumes found matching the job description.",
            "resumes": [],
            "quantitative_analysis": {},
            "resume_rankings": []
        }

    # Group chunks by resume_id and collect scores
    resume_scores = {}
    resume_names = {}
    resume_contents = {}

    for doc, score in jd_results:
        resume_id = doc.metadata.get("resume_id", "unknown")
        resume_name = doc.metadata.get("resume_name", "unknown")
        
        if resume_id not in resume_scores:
            resume_scores[resume_id] = []
            resume_names[resume_id] = resume_name
            resume_contents[resume_id] = []
        
        resume_scores[resume_id].append(score)
        resume_contents[resume_id].append(doc.page_content)

    # Calculate metrics for each resume
    resume_analysis = {}
    for resume_id in resume_scores:
        avg_score = sum(resume_scores[resume_id]) / len(resume_scores[resume_id])
        full_content = " ".join(resume_contents[resume_id])
        
        # Extract quantitative metrics
        metrics = extract_skills_and_keywords(full_content, jd_text)
        
        resume_analysis[resume_id] = {
            'resume_name': resume_names[resume_id],
            'avg_similarity_score': avg_score,
            'chunk_count': len(resume_scores[resume_id]),
            'metrics': metrics,
            'composite_score': (
                (1 - avg_score) * 0.4 +  # Lower similarity score is better
                metrics['skill_match_ratio'] * 0.3 +
                min(metrics['years_experience'] / 10, 1) * 0.2 +  # Cap at 10 years
                min(metrics['project_mentions'] / 5, 1) * 0.1  # Cap at 5 projects
            )
        }

    # Sort by composite score (higher is better)
    sorted_resumes = sorted(
        resume_analysis.items(), 
        key=lambda x: x[1]['composite_score'], 
        reverse=True
    )
    
    best_resume_id = sorted_resumes[0][0]
    best_analysis = sorted_resumes[0][1]

    # Filter retriever to best resume for detailed analysis
    filtered_retriever = vectorstore.as_retriever(
        search_kwargs={"k": 10, "filter": {"resume_id": best_resume_id}}
    )

    # Create analysis chain with LLM and filtered retriever
    analysis_chain = RetrievalQA.from_chain_type(
        llm=chat,
        retriever=filtered_retriever,
        return_source_documents=False
    )

    prompt = f"""
    You are analyzing the top-ranked resume for this job description:

    {jd_text}

    The resume belongs to {best_analysis['resume_name']} and scored highest based on:
    - Similarity Score: {best_analysis['avg_similarity_score']:.4f}
    - Skill Match Ratio: {best_analysis['metrics']['skill_match_ratio']:.2%}
    - Years of Experience: {best_analysis['metrics']['years_experience']}
    - Matching Skills: {', '.join(best_analysis['metrics']['matching_skills'])}

    Please provide a detailed analysis explaining:
    1. Why this resume is the best match for the role
    2. Specific skills, technologies, and experiences that align with the job requirements
    3. Any potential concerns or areas where the candidate might need development
    4. Overall assessment of fit for the position

    Be specific and reference actual content from the resume.
    """

    analysis_result = analysis_chain.invoke({"query": prompt})
    explanation = analysis_result.get("result", "No explanation available.")

    # Prepare ranking data
    resume_rankings = []
    for i, (resume_id, analysis) in enumerate(sorted_resumes):
        resume_rankings.append({
            "rank": i + 1,
            "resume_id": resume_id,
            "resume_name": analysis['resume_name'],
            "composite_score": round(analysis['composite_score'], 3),
            "similarity_score": round(analysis['avg_similarity_score'], 4),
            "skill_match_ratio": round(analysis['metrics']['skill_match_ratio'], 3),
            "years_experience": analysis['metrics']['years_experience'],
            "matching_skills": analysis['metrics']['matching_skills'][:5],  # Top 5
            "total_skills": analysis['metrics']['total_skills']
        })

    return {
        "best_resume_id": best_resume_id,
        "best_resume_name": best_analysis['resume_name'],
        "explanation": explanation,
        "quantitative_analysis": {
            "composite_score": round(best_analysis['composite_score'], 3),
            "similarity_score": round(best_analysis['avg_similarity_score'], 4),
            "skill_match_ratio": round(best_analysis['metrics']['skill_match_ratio'], 3),
            "years_experience": best_analysis['metrics']['years_experience'],
            "matching_skills": best_analysis['metrics']['matching_skills'],
            "total_skills_found": best_analysis['metrics']['total_skills']
        },
        "resume_rankings": resume_rankings,
        "total_resumes_analyzed": len(resume_analysis)
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Resume Chatbot API is running"}


@app.post("/reset_chat")
def reset_chat():
    """Reset chat history for a new conversation"""
    global chat_history
    chat_history = []
    return {"message": "Chat history reset successfully"}
