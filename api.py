import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi import FastAPI
from fastapi import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

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


@app.post("/analyze")
async def analyze(job_description: dict):
    jd_text = job_description.get("job_description", "")
    results = vectorstore.similarity_search(jd_text, k=10)

    if not results:
        return {
            "best_resume_id": "unknown",
            "explanation": "No resumes found matching the job description.",
            "resumes": []
        }

    # Count docs per resume_id
    resume_counts = {}
    for doc in results:
        rid = doc.metadata.get("resume_id", "unknown")
        resume_counts[rid] = resume_counts.get(rid, 0) + 1

    # Pick best resume_id with most hits
    best_resume_id = max(resume_counts, key=resume_counts.get)

    # Filter retriever to best resume
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
    You are comparing multiple candidate resumes for this job description:

    {jd_text}

    The current best-matched resume has id '{best_resume_id}' and has the most relevant content chunks.

    Please explain why this resume is the most aligned with the job description.
    Be specific, mention matching skills, technologies, experiences, and how they relate to job responsibilities or qualifications.
    Avoid generic statements — base it only on resume content.
    """

    analysis_result = analysis_chain.invoke({"query": prompt})

    explanation = analysis_result.get("result", "No explanation available.")

    return {
        "best_resume_id": best_resume_id,
        "explanation": explanation,
        "resumes": [doc.metadata for doc in results]
    }
