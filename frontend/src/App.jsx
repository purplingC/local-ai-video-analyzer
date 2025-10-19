import React, { useState, useEffect, useRef } from "react";
const API = "http://127.0.0.1:8000";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const chatRef = useRef(null);

  // Load previous chat
  useEffect(() => {
    const saved = localStorage.getItem("chat_history");
    if (saved) setMessages(JSON.parse(saved));
    fetchHistory();
  }, []);

  // Scroll and persist
  useEffect(() => {
    if (chatRef.current)
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    localStorage.setItem("chat_history", JSON.stringify(messages));
  }, [messages]);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API}/history`);
      const data = await res.json();
      setMessages(data.messages || []);
      localStorage.setItem("chat_history", JSON.stringify(data.messages));
    } catch {
      console.warn("Offline mode: using local cache only.");
    }
  };

  const addMessage = (role, text) => {
    const msg = { role, text, timestamp: new Date().toISOString() };
    setMessages((prev) => {
      const updated = [...prev, msg];
      localStorage.setItem("chat_history", JSON.stringify(updated));
      return updated;
    });
  };

  // Upload video
  const handleUpload = async () => {
    if (!file) return alert("Select a video first.");
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${API}/upload`, { method: "POST", body: form });
    const data = await res.json();
    if (res.ok) {
      setFileName(data.file_name);
      addMessage("assistant", `Uploaded ${data.file_name}`);
    } else addMessage("assistant", "Upload failed.");
  };

  // Handle user query
  const handleQuery = async () => {
    if (!input.trim()) return;
    const lower = input.trim().toLowerCase();
    addMessage("user", input);

    // Smart shortcut detection for follow-up answers (e.g. "pdf", "pptx", "both")
    if (["pdf", "ppt", "pptx", "powerpoint", "both"].some((word) => lower.includes(word))) {
      if (lower.includes("pdf") && !lower.includes("ppt")) {
        addMessage("assistant", "Generating PDF report...");
        await generate("pdf");
      } else if (lower.includes("ppt") || lower.includes("powerpoint")) {
        addMessage("assistant", "Generating PowerPoint report...");
        await generate("pptx");
      } else if (lower.includes("both")) {
        addMessage("assistant", "Generating both PDF and PowerPoint reports...");
        await generate("pdf");
        await generate("pptx");
      }
      setInput("");
      return;
    }

    try {
      const res = await fetch(`${API}/clarify?query=${encodeURIComponent(input)}`, {
        method: "POST",
      });
      const data = await res.json();

      if (data.decision === "transcribe") {
        addMessage("assistant", data.message);
        await transcribe();
      } else if (data.decision === "detect") {
        addMessage("assistant", data.message);
        await analyze();
      } else if (data.decision === "generate_pdf") {
        addMessage("assistant", data.message);
        await generate("pdf");
      } else if (data.decision === "generate_pptx") {
        addMessage("assistant", data.message);
        await generate("pptx");
      } else if (data.decision === "generate_both") {
        addMessage("assistant", data.message);
        await generate("pdf");
        await generate("pptx");
      } else if (data.decision === "ask_generate_format") {
        // Ask once for format
        addMessage("assistant", data.message);
      } else {
        // Fallback
        addMessage("assistant", data.message || "I'm not sure what you meant.");
      }
    } catch (err) {
      console.error(err);
      addMessage("assistant", "Clarify request failed (offline mode).");
    }
    setInput("");
  };

  const transcribe = async () => {
    if (!fileName) return alert("Upload a video first.");
    addMessage("user", "Transcribing...");
    const res = await fetch(`${API}/transcribe?file_name=${fileName}`, { method: "POST" });
    const data = await res.json();
    addMessage("assistant", data.transcript || "No transcript.");
  };

  const analyze = async () => {
    if (!fileName) return alert("Upload a video first.");
    addMessage("user", "Detecting objects...");
    const res = await fetch(`${API}/detect?file_name=${fileName}`, { method: "POST" });
    const data = await res.json();
    addMessage("assistant", JSON.stringify(data.objects || []));
  };

  const generate = async (type = "pdf") => {
    if (!fileName) return alert("Upload a video first.");
    addMessage("user", `Generating ${type.toUpperCase()} report...`);
    const res = await fetch(`${API}/generate?file_name=${fileName}&report_type=${type}`, { method: "POST" });
    const data = await res.json();
    if (data.report_path)
      addMessage("assistant", `Report ready: ${data.report_path}`);
    else addMessage("assistant", "Report generation failed.");
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        background: "#0f0f0f",
        color: "#fff",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-start",
        padding: "20px",
        boxSizing: "border-box",
      }}
    >
      <h1 style={{ color: "#a27bff", textAlign: "center", marginBottom: "10px" }}>
        🎬 Local AI Video Analyzer
      </h1>

      {/* Upload Section */}
      <div style={{ marginBottom: 15, textAlign: "center" }}>
        <input
          type="file"
          accept="video/mp4"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button onClick={handleUpload} style={{ marginLeft: 8 }}>
          Upload
        </button>
        <div style={{ marginTop: 5, fontSize: 14 }}>
          File: {fileName || "none"}
        </div>
      </div>

      {/* Chatbox */}
      <div
        style={{
          background: "#1b1b1b",
          borderRadius: 10,
          width: "90%",
          maxWidth: 900,
          padding: 15,
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
      >
        <h3 style={{ color: "#a27bff", textAlign: "left", margin: "0 0 8px 5px" }}>
          💬 Chatbox
        </h3>

        <div
          ref={chatRef}
          style={{
            flexGrow: 1,
            overflowY: "auto",
            border: "1px solid #333",
            borderRadius: 6,
            padding: 10,
            background: "#121212",
          }}
        >
          {messages
            .filter((m) => m.role !== "system")
            .map((m, i) => {
              const match = m.text.match(/artifacts[\\/](.+\.(pdf|pptx))/i);
              const fileName = match ? match[1] : null;
              const downloadLink = fileName ? `${API}/download/${fileName}` : null;

              return (
                <div key={i} style={{ marginBottom: 8 }}>
                  <b style={{ color: "#a27bff" }}>{m.role}</b>:{" "}
                  {downloadLink ? (
                    <a
                      href={downloadLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: "#a27bff", textDecoration: "underline" }}
                    >
                      Click here to open {fileName.endsWith("pdf") ? "PDF" : "PPTX"} report
                    </a>
                  ) : (
                    m.text
                  )}
                </div>
              );
            })}
        </div>

        {/* Input Row */}
        <div
          style={{
            marginTop: 10,
            display: "flex",
            width: "100%",
            gap: "8px",
          }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask something (e.g., Generate report)"
            style={{
              flex: 1,
              padding: "8px 10px",
              borderRadius: 6,
              border: "1px solid #444",
              background: "#0f0f0f",
              color: "#fff",
              fontSize: "14px",
            }}
            onKeyDown={(e) => e.key === "Enter" && handleQuery()}
          />
          <button
            onClick={handleQuery}
            style={{
              background: "#a27bff",
              border: "none",
              color: "white",
              fontWeight: "bold",
              borderRadius: 6,
              padding: "8px 16px",
              cursor: "pointer",
              fontSize: "14px",
              flexShrink: 0,
            }}
          >
            Enter
          </button>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ marginTop: 15 }}>
        <button onClick={transcribe}>Transcribe</button>
        <button onClick={analyze}>Detect Objects</button>
        <button onClick={() => generate("pdf")}>Generate PDF</button>
        <button onClick={() => generate("pptx")}>Generate PPT</button>
      </div>
    </div>
  );
}
