import React from 'react';
import ReactMarkdown from 'react-markdown';
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChatMessage } from '@/types/chat';
import { DataTable } from './DataTable';
import { Bot, User } from 'lucide-react';

interface MessageBubbleProps {
    message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
    const isUser = message.role === 'user';

    return (
        <div className={cn("flex w-full mb-6", isUser ? "justify-end" : "justify-start")}>
            <div className={cn("flex max-w-[85%] gap-2", isUser ? "flex-row-reverse" : "flex-row")}>
                <Avatar className="h-8 w-8 mt-1 border border-slate-700">
                    <AvatarFallback className={cn("text-xs", isUser ? "bg-blue-600 text-white" : "bg-emerald-600 text-white")}>
                        {isUser ? <User size={14} /> : <Bot size={14} />}
                    </AvatarFallback>
                </Avatar>

                <div className="flex flex-col gap-2">
                    <div className={cn(
                        "p-4 rounded-2xl text-sm leading-relaxed shadow-sm",
                        isUser
                            ? "bg-blue-600 text-white rounded-tr-none"
                            : "bg-slate-800 text-slate-100 border border-slate-700 rounded-tl-none min-w-[300px]"
                    )}>
                        {isUser ? (
                            <p className="whitespace-pre-wrap">{message.content}</p>
                        ) : (
                            <div className="markdown-content">
                                <ReactMarkdown>{message.content}</ReactMarkdown>
                            </div>
                        )}
                    </div>

                    {!isUser && message.data && (
                        <div className="w-full max-w-4xl">
                            <DataTable data={message.data} />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
