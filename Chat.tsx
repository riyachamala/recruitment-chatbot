'use client';

import React, { useState, useRef, useEffect } from "react";

export default function Chat() {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const [jobDescriptionSubmitted, setJobDescriptionSubmitted] = useState(false);

  const inputRef = useRef<HTMLTextAreaElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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

        const data = await response.json();
        console.log("Analyze response:", data);

        const bestResumeName = data.resumes?.[0]?.name || "unknown";
        const explanation = data.explanation || "No explanation provided.";

        setMessages((prev) => [
          ...prev.slice(0, -1),
          `bot: ✅ Most relevant resume:\n📄 ${bestResumeName}`,
          `bot: 📊 Reason for selection:\n${explanation}`,
          `bot: ✅ You can now ask questions about the resume content.`,
        ]);

        setJobDescriptionSubmitted(true);
      } catch (error) {
        setMessages((prev) => [
          ...prev.slice(0, -1),
          `bot: ❌ Error analyzing resumes.`,
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

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = inputRef.current.scrollHeight + "px";
    }
  }, [input]);

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "30px auto",
        padding: 20,
        backgroundColor: "#f5f7fa",
        borderRadius: 16,
        boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
        display: "flex",
        flexDirection: "column",
        height: "80vh",
      }}
    >
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
                  backgroundColor: isUser ? "#4F46E5" : "#D8B4FE",
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
                {isUser ? "u" : "c"}
              </div>
              <div
                style={{
                  maxWidth: "75%",
                  padding: "12px 16px",
                  borderRadius: 20,
                  backgroundColor: isUser ? "#4F46E5" : "#EDE9FE",
                  color: isUser ? "#fff" : "#3B2E5A",
                  fontSize: 15,
                  lineHeight: 1.4,
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                  boxShadow: isUser
                    ? "0 1px 4px rgba(79, 70, 229, 0.6)"
                    : "0 1px 4px rgba(192, 185, 242, 0.6)",
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
              ? "Ask questions about the resume..."
              : "Paste a job description to compare resumes..."
          }
          rows={1}
          style={{
            flexGrow: 1,
            resize: "none",
            borderRadius: 20,
            border: "1px solid #ddd",
            padding: "10px 16px",
            fontSize: 16,
            fontFamily: "inherit",
            outline: "none",
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
            maxHeight: 150,
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
            backgroundColor: "#4F46E5",
            border: "none",
            color: "#fff",
            padding: "12px 20px",
            fontSize: 16,
            fontWeight: "bold",
            borderRadius: 20,
            cursor: "pointer",
            boxShadow: "0 2px 10px rgba(79, 70, 229, 0.7)",
            userSelect: "none",
            transition: "background-color 0.3s",
          }}
          onMouseOver={(e) =>
            (e.currentTarget.style.backgroundColor = "#4338ca")
          }
          onMouseOut={(e) =>
            (e.currentTarget.style.backgroundColor = "#4F46E5")
          }
        >
          send
        </button>
      </form>
    </div>
  );
}
