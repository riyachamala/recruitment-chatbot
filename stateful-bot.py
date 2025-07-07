import os
import time
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA

# start timing
start_time = time.time()

# load all api keys from .env file
load_dotenv()

# initialize the embedding model (using huggingface to replace openai's embedding model)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# establish connection from the vector reps (embeddings) to the pinecone index
vectorstore = PineconeVectorStore(
    index_name=os.environ["INDEX_NAME"],
    embedding=embeddings
)

# initialize the groq llm
chat = ChatGroq(
    model_name="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=1,
    verbose=True
)

# step 1: prompt user for job description
print("\npaste the job description so i can evaluate resumes for relevance:")
job_description = input("> ").strip()

# step 2: search all resumes using the job description
jd_results = vectorstore.similarity_search_with_score(job_description, k=10)

# step 3: group chunks by resume_id and collect scores
resume_scores = {}
resume_names = {}

for doc, score in jd_results:
    resume_id = doc.metadata.get("resume_id", "unknown")
    resume_name = doc.metadata.get("name", "unknown")
    if resume_id not in resume_scores:
        resume_scores[resume_id] = []
        resume_names[resume_id] = resume_name
    resume_scores[resume_id].append(score)

# step 4: calculate average similarity score for each resume
avg_scores = {
    rid: sum(scores) / len(scores)
    for rid, scores in resume_scores.items()
}

# Pinecone similarity: lower = better
sorted_resumes = sorted(avg_scores.items(), key=lambda x: x[1])
best_resume_id, best_score = sorted_resumes[0]
best_resume_name = resume_names[best_resume_id]

# step 5: create filtered retriever to focus on the best resume only (for analysis only)
filtered_retriever = vectorstore.as_retriever(
    search_kwargs={"k": 10, "filter": {"resume_id": best_resume_id}}
)

# step 6: set up the analysis system (retrieval + llm)
analysis_chain = RetrievalQA.from_chain_type(
    llm=chat,
    retriever=filtered_retriever,
    return_source_documents=False
)

# step 7: create prompt to explain why this resume was selected
analysis_prompt = f"""
Based on the following job description, compare all retrieved resumes and identify the one that best aligns.

{job_description}

You have access to partial content chunks for each resume. Use only the information provided.

Which resume is most aligned with the job description? Be specific about matching skills, experience, technologies, and explain why this candidate is best suited.

be specific, mention matching skills, technologies, experiences, and how they relate to job responsibilities or qualifications.

avoid generic statements — base it only on resume content.
"""

# step 8: run the analysis and print results
analysis_result = analysis_chain.invoke({"query": analysis_prompt})

# step 9: output summary and explanation
print(f"\n✅ most relevant resume: {best_resume_name} ({best_resume_id})")
print("\n📊 reason for selection:\n")
print(analysis_result["result"])

print("\n📈 Resume Scores:")
for rid, score in sorted_resumes:
    print(f"• {resume_names.get(rid, 'unknown')} ({rid}): Avg Score = {score:.4f}")

# step 10: set up retriever over ALL resumes (no filter) for ongoing chat interaction
full_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# step 11: set up conversational retrieval qa chain (without filter, to access all resumes)
chat_qa = RetrievalQA.from_chain_type(
    llm=chat,
    retriever=full_retriever,
    return_source_documents=False
)

# step 12: start chat loop
print("\n\nYou can now ask questions about any resume content across all candidates.")
print("(Press enter on empty line to exit.)\n")

chat_history = []

while True:
    user_input = input("> ").strip()
    if not user_input:
        break

    result = chat_qa.invoke({"query": user_input})
    answer = result.get("result") or "sorry, no answer available."
    print(f"\nBot: {answer}\n")

end_time = time.time()
elapsed_time = end_time - start_time
print(f"\n⏱️ resume comparison and chat session completed in {elapsed_time:.2f} seconds.")
