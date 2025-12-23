import { Role } from "../types"

const API_URL = process.env.BACKEND_URL || "http://localhost:8000";

const ROLE_TO_PERMISSION: Record<Role, string> = {
    finance: "Finance_Team",
    marketing: "Marketing_Team",
    hr: "HR_Team",
    engineering: "Engineering_Department",
    general: "Employee_Level",
}

export const fetchSessions = async (
    prompt: string,
    role: Role,
    onChunk: (text: string) => void
) => {
    try {
        const response = await fetch(`${API_URL}/rag/query`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                role: ROLE_TO_PERMISSION[role],
                query: prompt,
            }),
        });

        if (!response.ok) {
            throw new Error(`API ERROR: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();

        // Stream the answer text
        onChunk(data.answer);

        // Return full response with sources
        return {
            answer: data.answer,
            sources: data.sources || []
        };
    } catch (error) {
        console.error("Error fetching from backend:", error);
        throw error;
    }
};