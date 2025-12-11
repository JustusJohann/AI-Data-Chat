"use client";

import React, { useState, useRef, useEffect } from "react";
import { Send, Database, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";
import { MessageBubble } from "@/components/MessageBubble";
import { ChatMessage } from "@/types/chat";

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          thread_id: threadId
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();

      // Update thread ID from response
      if (data.thread_id) {
        setThreadId(data.thread_id);
      }

      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: data.answer,
        data: data.data,
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-100 items-center justify-center p-4">
      <Card className="w-full max-w-5xl h-[90vh] flex flex-col bg-slate-900 border-slate-800 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center gap-3 bg-slate-900/50 backdrop-blur-md sticky top-0 z-10 shrink-0">
          <div className="h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Database className="text-white" size={20} />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white">Natural Language Data Analyst</h1>
            <p className="text-xs text-indigo-400 font-medium">PostgreSQL • LangGraph • MCP</p>
          </div>
        </div>

        {/* Chat Area - Added min-h-0 to allow flex child to shrink properly */}
        <div className="flex-1 min-h-0 relative">
          <ScrollArea className="h-full w-full p-4" ref={scrollAreaRef}>
            <div className="max-w-4xl mx-auto py-4">
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-[50vh] text-slate-500 gap-4">
                  <Database size={64} className="opacity-20" />
                  <p className="text-center max-w-sm">
                    Ask me anything about your database. I can analyze schemas and run SQL queries to find answers.
                  </p>
                  <div className="flex gap-2 flex-wrap justify-center mt-4">
                    {["Show me all tables", "Count rows in orders", "Who are the top customers?"].map(q => (
                      <Button
                        key={q}
                        variant="outline"
                        className="bg-slate-800 border-slate-700 hover:bg-slate-700 text-xs"
                        onClick={() => setInput(q)}
                      >
                        {q}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((msg, idx) => (
                <MessageBubble key={idx} message={msg} />
              ))}

              {isLoading && (
                <div className="flex w-full mb-6 justify-start">
                  <div className="flex flex-row gap-2 max-w-[85%]">
                    <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center">
                      <Loader2 className="animate-spin text-indigo-400" size={14} />
                    </div>
                    <div className="flex flex-col gap-2">
                      <div className="p-4 rounded-2xl rounded-tl-none bg-slate-800 border border-slate-700 text-slate-400 text-sm shadow-sm flex items-center gap-2">
                        <span className="animate-pulse">Thinking & Analyzing...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {/* Spacer to prevent content being hidden under the absolute positioned gradient or scroll bottom */}
              <div className="h-4" />
            </div>
          </ScrollArea>
        </div>

        {/* Input Area */}
        <div className="p-4 bg-slate-900 border-t border-slate-800 shrink-0">
          <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your data..."
              className="bg-slate-950 border-slate-800 text-slate-100 placeholder:text-slate-600 py-6 pl-6 pr-14 rounded-full focus-visible:ring-indigo-500/50 shadow-inner"
            />
            <Button
              type="submit"
              disabled={!input.trim() || isLoading}
              size="icon"
              className="absolute right-2 top-1.5 h-9 w-9 rounded-full bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-600/20 transition-all"
            >
              <Send className="text-white" size={16} />
            </Button>
          </form>
          <div className="text-center mt-2">
            <span className="text-[10px] text-slate-600 uppercase tracking-wider font-semibold">AI Agent Powered</span>
          </div>
        </div>
      </Card>
    </div>
  );
}
