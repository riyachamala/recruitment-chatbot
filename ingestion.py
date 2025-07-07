import os
import sys
from pinecone import Pinecone
from collections import Counter
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# Load environment variables
load_dotenv()

# force UTF-8 globally in python
sys.stdout.reconfigure(encoding='utf-8')

# Pinecone setup
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index_name = os.environ.get("INDEX_NAME")

# Define resume directory
resume_folder = "resumes"
resume_folder_path = os.path.join(os.getcwd(), resume_folder)

# Document splitter config
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=80,
    separators=["\n\n", "\n", " ", ""]
)

all_chunks = []

# Process each resume PDF
for filename in os.listdir(resume_folder_path):
    if filename.endswith(".pdf"):
        filepath = os.path.join(resume_folder_path, filename)
        print(f"Processing: {filename}")

        resume_id = os.path.splitext(filename)[0]
        resume_name = resume_id.replace("_", " ").title()

        try:
            loader = PyPDFLoader(filepath)
            document = loader.load()

            # Attach metadata to full doc and chunks
            for doc in document:
                doc.metadata["filename"] = filename
                doc.metadata["resume_id"] = resume_id
                doc.metadata["resume_name"] = resume_name

            chunks = text_splitter.split_documents(document)

            for chunk in chunks:
                chunk.metadata["filename"] = filename
                chunk.metadata["resume_id"] = resume_id
                chunk.metadata["resume_name"] = resume_name

            all_chunks.extend(chunks)

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

print(f"\n✅ Created {len(all_chunks)} chunks")

# Summary of chunks per resume
chunk_counter = Counter([(c.metadata["resume_id"], c.metadata["resume_name"]) for c in all_chunks])
print("\n📊 Chunks per resume:")
for (rid, name), count in chunk_counter.items():
    print(f"- {name} ({rid}): {count} chunks")

# Create embeddings + upload to Pinecone
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = PineconeVectorStore.from_documents(
    all_chunks,
    embedding=embeddings,
    index_name=index_name
)

# Validate Pinecone index stats
index = pc.Index(index_name)
stats = index.describe_index_stats()
print("\n📦 Pinecone Index Stats:")
print(stats)
