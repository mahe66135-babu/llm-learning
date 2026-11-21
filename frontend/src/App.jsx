import { useState, useEffect } from "react";  
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

function cleanMarkdown(content) {
  return content
    .replace(/\\\r?\n/g, "\n")
    .replace(/(?<!\*)\*\*(.+?)\*\*(?!\*)/g, "**$1** ");
}

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(
  () => localStorage.getItem("chat_session_id")
);
useEffect(() => {
  const loadChatHistory = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/chat/${encodeURIComponent(sessionId)}/history`
      );

      if (!response.ok) {
        if (response.status === 404) {
          localStorage.removeItem("chat_session_id");
          setSessionId(null);
        }
        return;
      }

      const data = await response.json();

      setMessages(data.messages);
    } catch (error) {
      console.error("Failed to restore chat history:", error);
    }
  };

  loadChatHistory();
}, [sessionId]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const userMessage = input.trim();

    if (!userMessage || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: userMessage },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "API request failed");
      }

      setSessionId(data.session_id);
      localStorage.setItem("chat_session_id", data.session_id);

      setMessages((previous) => [
        ...previous,
        { role: "assistant", content: data.response },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: `**Error:** ${error.message}. Please check your backend server.`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearConversation = async () => {
    if (loading) return;

    try {
      if (sessionId) {
        const response = await fetch(
          `http://127.0.0.1:8000/chat/${encodeURIComponent(sessionId)}`,
          { method: "DELETE" }
        );

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || "Unable to clear conversation");
        }
      }

      setMessages([]);
      setSessionId(null);
      localStorage.removeItem("chat_session_id");
      setInput("");
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>AI Customer Support</h1> <br></br>
        <p>Ask questions and continue your conversation with AI.</p>
        <button
          className="clear-button"
          onClick={handleClearConversation}
          disabled={loading}
        >
          Clear Conversation
        </button>
      </header>

      <main className="chat-container">
        <section className="messages">
          {messages.length === 0 && (
            <div className="welcome">
              <h2>Welcome!</h2>
              <p>How can I help you today?</p>
            </div>
          )}

          {messages.map((message, index) => (
  <div
    key={index}
    className={`message ${message.role}`}
  >
    <div className="message-content">
      {message.role === "assistant" ? (
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
  {cleanMarkdown(message.content)}
</ReactMarkdown>
      ) : (
        message.content
      )}
    </div>

    {message.timestamp && (
      <div className="message-timestamp">
        {new Date(message.timestamp).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit"
        })}
      </div>
    )}
  </div>
))}

          {loading && (
            <div className="message assistant">
              <strong>AI Assistant</strong>
              <p>Thinking...</p>
            </div>
          )}
        </section>

        <form className="chat-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Type your message..."
            disabled={loading}
          />

          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? "Sending..." : "Send"}
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;
