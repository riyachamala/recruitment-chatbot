import os
from pinecone.grpc import PineconeGRPC as Pinecone #using pinecone as database
from pinecone import ServerlessSpec
from pypdf import PdfReader #to read pdfs
from sentence_transformers import SentenceTransformer #creates dense vector embeddings of text
from operator import itemgetter
from collections import defaultdict #not exactly necessary, just for default dict
import sys #command line

#all globals

API_KEY    = os.getenv("PINECONE_API_KEY", "pcsk_4xUFTa_3wZP7CHeqt9jhU3KzVqj7DkscmHLssttNub8nmJdy4Py2YZPcstrayYkAcBrfhu")
INDEX_NAME = "resume-match-384"
NAMESPACE  = "resumes"
DIMENSION  = 384
MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 200
TOP_K      = 2
ALL_PDFS = []


#instantiate: one index with different resume-ids as metadata and under one namespace
pc = Pinecone(api_key=API_KEY)
if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
    pc.create_index(
      name=INDEX_NAME,
      dimension=DIMENSION,
      metric="cosine",
      spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index    = pc.Index(INDEX_NAME)
embedder = SentenceTransformer(MODEL_NAME)

def read_pdf_text(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

# all chunks share same resume id
def chunk_text(text, size=CHUNK_SIZE):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]

#uploading all resumes that are stored in a folder through chunking and then embedding into vectors
def upsert_resumes_from_folder(folder):
    for fname in os.listdir(folder):
        if not fname.lower().endswith(".pdf"):
            continue
        thing  = os.path.splitext(fname)[0]
        full = os.path.join(folder, fname)
        text = read_pdf_text(full)
        ALL_PDFS.append(text)
        chunks = chunk_text(text)
        if not chunks:
            continue
        vecs = embedder.encode(chunks).tolist()
        upserts = [
            (f"{thing}_chunk_{i}", v, {"resume_id": thing})
            for i, v in enumerate(vecs)
        ]
        index.upsert(vectors=upserts, namespace=NAMESPACE)
        print(f"Indexed {len(chunks)} chunks for '{thing}'")

#
def find_best_resume_for_job(job_desc, top_k=TOP_K, filter_meta=None):
    #convert to embedding vector
    q_vec = embedder.encode(job_desc).tolist()
    #query the pinecone index with job embedding to find top_k most similar
    resp = index.query(
        vector=q_vec,
        namespace=NAMESPACE,
        top_k=top_k,
        include_metadata=True,
        filter=filter_meta
    )
    #aggregate similarity scores from all matching chunks that are organized by resumeid
    scores = defaultdict(list) #cosine similarity is just geometric intrep of dot product -- how close the two vectors are
    for m in resp['matches']:
        resume_id = m['metadata']['resume_id']
        scores[resume_id].append(m['score'])
    #get best resume by computing mean scores
    resume_scores = {rid: sum(scrs)/len(scrs) for rid, scrs in scores.items()}
    # Sort by average score, descending
    ranked = sorted(resume_scores.items(), key=itemgetter(1), reverse=True)
    return ranked #list of (resume_id, avg_score) tuples

def analyze_resume_match(job_description, resume_rankings):
    """Simple analysis function to replace the autogen conversation for now"""
    print(f"\n=== Resume Analysis for Job: {job_description} ===")
    
    if not resume_rankings:
        print("No matching resumes found.")
        return
    
    print(f"\nTop matching resumes:")
    for i, (resume_id, score) in enumerate(resume_rankings[:3], 1):
        print(f"{i}. {resume_id}: Similarity Score {score:.4f}")
        
        # Provide some basic analysis
        if score > 0.8:
            match_quality = "Excellent match"
        elif score > 0.7:
            match_quality = "Good match"
        elif score > 0.6:
            match_quality = "Fair match"
        else:
            match_quality = "Weak match"
            
        print(f"   → {match_quality}")
    
    best_resume = resume_rankings[0]
    print(f"\n🏆 Best Candidate: {best_resume[0]} (Score: {best_resume[1]:.4f})")
    
    print(f"\nRecommendations:")
    if best_resume[1] > 0.75:
        print("- This candidate shows strong alignment with the job requirements")
        print("- Consider moving forward with initial screening")
    elif best_resume[1] > 0.6:
        print("- This candidate has some relevant skills but may need skill development")
        print("- Consider for further evaluation based on other criteria")
    else:
        print("- Limited alignment with job requirements")
        print("- May need to expand search criteria or consider skill training")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <command> [arguments]")
        print("Commands:")
        print("  upload <folder_path>  - Upload resumes from folder")
        print("  query <job_description> - Find best matching resumes")
        return

    command = sys.argv[1]

    if command == "upload":
        if len(sys.argv) < 3:
            print("Usage: python script.py upload <folder_path>")
            return
        folder_path = sys.argv[2]
        print(f"Uploading resumes from: {folder_path}")
        upsert_resumes_from_folder(folder_path)
        print("Upload completed!")

    elif command == "query":
        if len(sys.argv) < 3:
            print("Usage: python script.py query '<job_description>'")
            return
        job_description = " ".join(sys.argv[2:])
        print(f"Finding best resumes for job: {job_description}")
        
        rankings = find_best_resume_for_job(job_description)
        
        analyze_resume_match(job_description, rankings)

    else:
        print(f"Unknown command: {command}")
        print("Available commands: upload, query")

if __name__ == "__main__":
    main()
