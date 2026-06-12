"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { MessageSquare } from "lucide-react";
import { MEDICAL_DISCLAIMER, friendlyErrorMessage } from "@curedesk/shared";
import { api } from "@/lib/api";
import Ping from "./Ping";

export default function Chatbot() {
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput("");
    const history = [...messages, { role: "user" as const, content: userMsg }];
    setMessages(history);
    setLoading(true);

    try {
      const res = await api.chat({ message: userMsg, history: messages });
      setMessages([...history, { role: "assistant", content: res.reply }]);
    } catch (err) {
      setMessages([
        ...history,
        {
          role: "assistant",
          content: friendlyErrorMessage(err, "I couldn't generate a response. Please try again."),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chatbot-container">
      <div className="absolute -top-2 -right-2">
        <Ping />
      </div>
      <button type="button" onClick={() => setIsChatbotOpen(true)} className="chatbot-text">
        <span className="font-black">
          <MessageSquare />
        </span>
      </button>

      {mounted &&
        isChatbotOpen &&
        createPortal(
          <div className="fixed bottom-16 right-3 z-[100] w-96 max-w-[calc(100vw-1.5rem)] bg-white shadow-lg rounded-lg p-4 border-[3px] border-black">
            <div className="chat-header flex justify-between items-center border-b pb-2 mb-2">
              <h2 className="text-2xl font-bold">Chatbot</h2>
              <button type="button" onClick={() => setIsChatbotOpen(false)} className="text-lg text-gray-500">
                Close
              </button>
            </div>

            <p className="text-xs text-gray-500 mb-2">{MEDICAL_DISCLAIMER}</p>

            <div className="chat-body h-64 overflow-y-auto">
              <div className="messages space-y-2">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`message p-2 rounded-lg text-sm ${
                      message.role === "user" ? "bg-primary text-white" : "bg-gray-200 text-black"
                    }`}
                  >
                    <p>{message.content}</p>
                  </div>
                ))}
                {loading && <p className="text-sm text-gray-400">Thinking...</p>}
              </div>
            </div>

            <form onSubmit={handleSubmit} className="chat-input-form flex mt-4">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask me anything..."
                className="search-input flex-grow border rounded-lg p-2 mr-2"
              />
              <button type="submit" className="submit-btn bg-primary text-white rounded-lg px-4">
                Send
              </button>
            </form>
          </div>,
          document.body,
        )}
    </div>
  );
}
