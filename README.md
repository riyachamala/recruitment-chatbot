# Resume Matching System

A semantic resume matching system that uses vector embeddings to find the best candidates for job descriptions.

## Features

- **PDF Resume Parsing**: Extracts text from PDF resumes
- **Vector Embeddings**: Uses sentence transformers to create semantic embeddings
- **Pinecone Vector Database**: Stores and searches resume embeddings efficiently
- **Semantic Matching**: Finds candidates based on semantic similarity rather than just keyword matching
- **Command-Line Interface**: Easy-to-use CLI for uploading resumes and querying matches

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Pinecone API key (optional - a default key is provided for testing):
```bash
export PINECONE_API_KEY="your-api-key-here"
```

## Usage

### Upload Resumes

Upload all PDF resumes from a folder:

```bash
python stateful-bot.py upload resumes/
```

This will:
- Read all PDF files in the specified folder
- Extract text and chunk it into smaller pieces
- Generate vector embeddings using the all-MiniLM-L6-v2 model
- Store vectors in Pinecone with resume metadata

### Find Matching Resumes

Search for candidates that match a job description:

```bash
python stateful-bot.py query "Software Engineer with React experience"
```

This will:
- Convert the job description to a vector embedding
- Search the Pinecone index for similar resume chunks
- Aggregate scores by resume and rank candidates
- Display analysis and recommendations

## Example Output

```
Finding best resumes for job: Software Engineer with React experience

=== Resume Analysis for Job: Software Engineer with React experience ===

Top matching resumes:
1. resume_riya: Similarity Score 0.3868
   → Weak match
2. resume_abhi: Similarity Score 0.3847
   → Weak match

🏆 Best Candidate: resume_riya (Score: 0.3868)

Recommendations:
- Limited alignment with job requirements
- May need to expand search criteria or consider skill training
```

## Technical Details

- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Chunk Size**: 200 words per chunk
- **Vector Database**: Pinecone serverless index
- **Similarity Metric**: Cosine similarity
- **PDF Processing**: pypdf library

## Architecture

1. **PDF Processing**: Extracts text from PDF resumes
2. **Text Chunking**: Splits text into manageable chunks
3. **Embedding Generation**: Creates vector representations using sentence transformers
4. **Vector Storage**: Stores embeddings in Pinecone with metadata
5. **Semantic Search**: Finds similar candidates using vector similarity
6. **Score Aggregation**: Combines chunk-level scores for resume-level ranking

The system provides semantic matching that goes beyond keyword matching, helping find candidates with relevant skills even if they don't use the exact same terminology as the job description.