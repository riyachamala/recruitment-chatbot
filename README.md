# 🤖 RAG-Based Resume Chatbot

An intelligent chatbot that analyzes resumes against job descriptions, provides quantitative and qualitative analysis, and allows interactive Q&A about candidates.

## ✨ Features

### 🔍 **Smart Resume Analysis**
- **Quantitative Metrics**: Similarity scores, skill matching ratios, years of experience extraction
- **Composite Scoring**: Weighted algorithm combining multiple factors for accurate ranking
- **Skills Detection**: Automatic identification of technical skills and technologies
- **Experience Parsing**: Extracts years of experience from resume content

### 📊 **Comprehensive Ranking System**
- Resume rankings with detailed score breakdowns
- Skill match percentages against job requirements
- Experience level comparisons
- Project and achievement counting

### 💬 **Interactive Chat Interface**
- Ask questions about specific candidates
- Compare multiple resumes
- Get detailed explanations of rankings
- Modern, responsive UI with real-time responses

### 🛠️ **Technical Stack**
- **Frontend**: Next.js 14 + TypeScript + React
- **Backend**: FastAPI + Python
- **AI/ML**: LangChain + Groq LLM + HuggingFace Embeddings
- **Vector Store**: Pinecone for semantic search
- **PDF Processing**: PyMuPDF for resume parsing

---

## 🚀 Quick Start

### 1. **Clone and Install**
```bash
git clone <your-repo-url>
cd resume-chatbot
```

### 2. **Environment Setup**
```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration section)
```

### 3. **Install Dependencies**

**Python Backend:**
```bash
pip3 install -r requirements.txt
```

**Frontend:**
```bash
npm install
```

### 4. **Setup and Initialize**
```bash
# Run the setup script to initialize everything
python3 setup_project.py
```

### 5. **Start the Application**

**Terminal 1 - Backend:**
```bash
python3 start_backend.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

**Open**: http://localhost:3000

---

## ⚙️ Configuration

### Required Environment Variables (`.env`)

```env
# Pinecone Vector Database
PINECONE_API_KEY=your_pinecone_api_key_here
INDEX_NAME=resume-chatbot-index

# Groq AI (for LLM)
GROQ_API_KEY=your_groq_api_key_here

# Optional: OpenAI (alternative to Groq)
OPENAI_API_KEY=your_openai_api_key_here
```

### API Key Setup:
1. **Pinecone**: Sign up at [pinecone.io](https://pinecone.io)
2. **Groq**: Get API key from [console.groq.com](https://console.groq.com)

---

## 📁 Project Structure

```
resume-chatbot/
├── app/                     # Next.js app directory
│   ├── page.tsx            # Main page component
│   ├── layout.tsx          # App layout
│   └── globals.css         # Global styles
├── components/             # React components
│   └── Chat.tsx           # Main chat interface
├── resumes/               # Resume PDF storage
│   ├── resume_candidate1.pdf
│   └── resume_candidate2.pdf
├── api.py                 # FastAPI backend
├── ingestion.py           # Resume processing script
├── start_backend.py       # Backend startup script
├── setup_project.py       # Project initialization
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
└── .env.example          # Environment template
```

---

## 📋 Usage Guide

### 1. **Adding Resumes**
- Place PDF resume files in the `resumes/` folder
- Run `python3 ingestion.py` to process and index them
- The system will chunk and embed resume content

### 2. **Using the Chatbot**

**Step 1**: Paste a job description
```
Looking for a Senior Python Developer with 5+ years experience in 
Django, React, AWS, and machine learning. Must have experience 
building scalable web applications and working with databases.
```

**Step 2**: Review the analysis
- See quantitative metrics (scores, skill matches, experience)
- Review resume rankings with detailed breakdowns
- Read AI-generated qualitative analysis

**Step 3**: Ask follow-up questions
```
- "What specific Python frameworks has the top candidate used?"
- "Compare the machine learning experience between candidates"
- "Who has the most AWS experience?"
- "Show me projects related to web applications"
```

### 3. **Analysis Features**

The system provides:
- **Composite Score**: Overall ranking (0-1 scale)
- **Similarity Score**: Semantic similarity to job description
- **Skill Match Ratio**: Percentage of required skills found
- **Experience Years**: Extracted years of experience
- **Matching Skills**: List of relevant technologies/skills
- **Rankings**: All candidates ranked with detailed metrics

---

## 🔧 Advanced Usage

### Manual Resume Processing
```bash
# Re-process all resumes
python3 ingestion.py

# Check Pinecone index stats
python3 -c "from ingestion import *; print(index.describe_index_stats())"
```

### API Endpoints
- `POST /analyze` - Analyze resumes against job description
- `POST /chat` - Interactive chat with the system
- `POST /reset_chat` - Reset conversation history
- `GET /health` - Health check

### Customization
- Modify `extract_skills_and_keywords()` in `api.py` to add new skills
- Adjust scoring weights in the composite score calculation
- Update UI colors and styling in `Chat.tsx`

---

## 🧪 Example Interactions

### Job Description Analysis
```
Input: "Looking for a React developer with Node.js and AWS experience"

Output:
✅ Analysis Complete - 3 resumes analyzed
🏆 Top Ranked Resume: John Doe
📊 Quantitative Metrics:
• Composite Score: 0.847/1.0
• Skill Match Ratio: 85.7%
• Years of Experience: 6 years
• Matching Skills: react, node.js, aws, javascript
📈 Resume Rankings:
1. John Doe (Score: 0.847) - Skills Match: 85.7% | Experience: 6 yrs
2. Jane Smith (Score: 0.723) - Skills Match: 71.4% | Experience: 4 yrs
```

### Follow-up Questions
```
User: "What AWS services has John worked with?"
Bot: "Based on John's resume, he has experience with EC2, S3, Lambda, 
and RDS. He built a serverless application using Lambda and API Gateway..."

User: "Compare the React experience between all candidates"
Bot: "Here's the React experience comparison:
- John Doe: 4 years, built 5+ production apps, worked with Redux...
- Jane Smith: 3 years, focused on component libraries..."
```

---

## 🛠️ Troubleshooting

### Common Issues

**Backend won't start:**
- Check if all dependencies are installed: `pip3 install -r requirements.txt`
- Verify `.env` file has required API keys
- Ensure Pinecone index exists

**No resumes found:**
- Check `resumes/` folder has PDF files
- Run `python3 ingestion.py` to process resumes
- Verify Pinecone connection and index

**Frontend errors:**
- Run `npm install` to install dependencies
- Check if backend is running on port 8000
- Verify CORS settings in `api.py`

**Chat responses are poor:**
- Verify Groq API key is valid
- Check if resumes were properly ingested
- Try different job description phrasing

---

## 🔄 Development

### Adding New Features
1. **New Skills**: Update `tech_skills` list in `api.py`
2. **Scoring Algorithm**: Modify composite score calculation
3. **UI Components**: Enhance `Chat.tsx` interface
4. **API Endpoints**: Add new routes in `api.py`

### Testing
```bash
# Test backend API
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Python developer with Django experience"}'

# Check health
curl http://localhost:8000/health
```

---

## 📄 License

MIT License - Feel free to use and modify for your projects.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

---

## 🙏 Acknowledgments

- **LangChain** for the RAG framework
- **Pinecone** for vector storage
- **Groq** for fast LLM inference
- **Next.js** for the frontend framework