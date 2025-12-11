export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    data?: any; // Raw JSON data for tables
    timestamp: number;
}
