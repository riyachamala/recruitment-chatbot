'use client';

import React, { useState, useRef, useEffect } from "react";

interface AnalysisResult {
  best_resume_id: string;
  best_resume_name: string;
  explanation: string;
  quantitative_analysis: {
    composite_score: number;
    similarity_score: number;
    skill_match_ratio: number;
    years_experience: number;
    matching_skills: string[];
    total_skills_found: number;
  };
  resume_rankings: Array<{
    rank: number;
    resume_id: string;
    resume_name: string;
    composite_score: number;
    similarity_score: number;
    skill_match_ratio: number;
    years_experience: number;
    matching_skills: string[];
    total_skills: number;
  }>;
  total_resumes_analyzed: number;
}

export default function Chat() {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const [jobDescriptionSubmitted, setJobDescriptionSubmitted] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const inputRef = useRef<HTMLTextAreaElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const formatSkills = (skills: string[]) => {
    return skills.length > 0 ? skills.join(", ") : "None identified";
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    if (!jobDescriptionSubmitted) {
      // Step 1: submit job description
      setMessages((prev) => [...prev, `you: ${input}`, `bot: analyzing resumes...`]);

      try {
        const response = await fetch("http://localhost:8000/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ job_description: input }),
        });

        const data: AnalysisResult = await response.json();
        console.log("Analyze response:", data);
        setAnalysisResult(data);

        const quantAnalysis = data.quantitative_analysis;
        const rankings = data.resume_rankings;

        // Create detailed analysis message
        const analysisMessage = `✅ **Analysis Complete - ${data.total_resumes_analyzed} resumes analyzed**

🏆 **Top Ranked Resume: ${data.best_resume_name}**

📊 **Quantitative Metrics:**
• Composite Score: ${quantAnalysis.composite_score}/1.0
• Similarity Score: ${quantAnalysis.similarity_score}
• Skill Match Ratio: ${formatPercentage(quantAnalysis.skill_match_ratio)}
• Years of Experience: ${quantAnalysis.years_experience} years
• Matching Skills: ${formatSkills(quantAnalysis.matching_skills)}
• Total Skills Found: ${quantAnalysis.total_skills_found}

📈 **Resume Rankings:**
${rankings.map(resume => 
  `${resume.rank}. ${resume.resume_name} (Score: ${resume.composite_score})\n   Skills Match: ${formatPercentage(resume.skill_match_ratio)} | Experience: ${resume.years_experience} yrs`
).join('\n')}`;

        const explanationMessage = `📝 **Detailed Analysis:**\n${data.explanation}`;

        setMessages((prev) => [
          ...prev.slice(0, -1),
          `bot: ${analysisMessage}`,
          `bot: ${explanationMessage}`,
          `bot: ✅ You can now ask questions about any resume, rankings, or request specific comparisons.`,
        ]);

        setJobDescriptionSubmitted(true);
      } catch (error) {
        setMessages((prev) => [
          ...prev.slice(0, -1),
          `bot: ❌ Error analyzing resumes. Please make sure the backend is running.`,
        ]);
      }

      setInput("");
      return;
    }

    // Step 2: Chat mode — ask follow-up questions
    setMessages((prev) => [...prev, `you: ${input}`, `bot: thinking...`]);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      });

      const data = await response.json();
      const answer = data?.answer || "❌ No response from backend.";

      setMessages((prev) => [
        ...prev.slice(0, -1),
        `bot: ${answer}`,
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev.slice(0, -1),
        `bot: ❌ Error talking to backend.`,
      ]);
    }

    setInput("");
  };

  const resetChat = async () => {
    try {
      await fetch("http://localhost:8000/reset_chat", { method: "POST" });
      setMessages([]);
      setJobDescriptionSubmitted(false);
      setAnalysisResult(null);
      setInput("");
    } catch (error) {
      console.error("Error resetting chat:", error);
    }
  };

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = inputRef.current.scrollHeight + "px";
    }
  }, [input]);

  return (
    <div
      style={{
        maxWidth: 800,
        margin: "30px auto",
        padding: 20,
        backgroundColor: "#f5f7fa",
        borderRadius: 16,
        boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
        display: "flex",
        flexDirection: "column",
        height: "85vh",
      }}
    >
      {/* Header */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: 16,
        padding: "0 8px"
      }}>
        <h1 style={{
          fontSize: 24,
          fontWeight: "bold",
          color: "#2D3748",
          margin: 0
        }}>
          Resume Chatbot 📄
        </h1>
        {jobDescriptionSubmitted && (
          <button
            onClick={resetChat}
            style={{
              backgroundColor: "#EF4444",
              color: "white",
              border: "none",
              padding: "8px 16px",
              borderRadius: 8,
              fontSize: 14,
              cursor: "pointer",
              fontWeight: "500"
            }}
          >
            New Analysis
          </button>
        )}
      </div>

      <div
        style={{
          flexGrow: 1,
          overflowY: "auto",
          padding: "10px 20px",
          backgroundColor: "#fff",
          borderRadius: 16,
          boxShadow: "inset 0 0 5px rgba(0,0,0,0.05)",
          display: "flex",
          flexDirection: "column",
          gap: 24,
        }}
      >
        {messages.length === 0 && (
          <div style={{
            textAlign: "center",
            color: "#6B7280",
            fontSize: 16,
            padding: "40px 20px"
          }}>
            Welcome! Paste a job description to analyze and rank resumes, then ask questions about the candidates.
          </div>
        )}

        {messages.map((msg, i) => {
          const isUser = msg.startsWith("you:");
          const text = msg.replace(/^you: /, "").replace(/^bot: /, "");

          return (
            <div
              key={i}
              style={{
                display: "flex",
                flexDirection: isUser ? "row-reverse" : "row",
                alignItems: "flex-start",
                gap: 12,
                marginBottom: 24,
              }}
            >
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: "50%",
                  backgroundColor: isUser ? "#4F46E5" : "#10B981",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#fff",
                  fontWeight: "bold",
                  userSelect: "none",
                  flexShrink: 0,
                  fontSize: 16,
                  textTransform: "uppercase",
                }}
              >
                {isUser ? "U" : "🤖"}
              </div>
              <div
                style={{
                  maxWidth: "80%",
                  padding: "12px 16px",
                  borderRadius: 20,
                  backgroundColor: isUser ? "#4F46E5" : "#F3F4F6",
                  color: isUser ? "#fff" : "#1F2937",
                  fontSize: 15,
                  lineHeight: 1.5,
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                  boxShadow: isUser
                    ? "0 1px 4px rgba(79, 70, 229, 0.6)"
                    : "0 1px 4px rgba(0, 0, 0, 0.1)",
                  fontFamily: "system-ui, -apple-system, sans-serif",
                }}
              >
                {text}
              </div>
            </div>
          );
        })}
        <div ref={chatEndRef} />
      </div>

      <form
        onSubmit={handleSubmit}
        style={{
          marginTop: 12,
          display: "flex",
          gap: 12,
          alignItems: "flex-end",
        }}
      >
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            jobDescriptionSubmitted
              ? "Ask about rankings, specific candidates, skills comparison..."
              : "Paste a job description to analyze and rank resumes..."
          }
          rows={1}
          style={{
            flexGrow: 1,
            resize: "none",
            borderRadius: 20,
            border: "1px solid #ddd",
            padding: "12px 18px",
            fontSize: 16,
            fontFamily: "inherit",
            outline: "none",
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
            maxHeight: 120,
            overflowY: "auto",
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <button
          type="submit"
          style={{
            backgroundColor: "#10B981",
            border: "none",
            color: "#fff",
            padding: "12px 20px",
            fontSize: 16,
            fontWeight: "bold",
            borderRadius: 20,
            cursor: "pointer",
            boxShadow: "0 2px 10px rgba(16, 185, 129, 0.3)",
            userSelect: "none",
            transition: "background-color 0.3s",
          }}
          onMouseOver={(e) =>
            (e.currentTarget.style.backgroundColor = "#059669")
          }
          onMouseOut={(e) =>
            (e.currentTarget.style.backgroundColor = "#10B981")
          }
        >
          {jobDescriptionSubmitted ? "Ask" : "Analyze"}
        </button>
      </form>
    </div>
  );
}
