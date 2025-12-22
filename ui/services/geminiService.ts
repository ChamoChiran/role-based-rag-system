
import { GoogleGenAI } from "@google/genai";
import { Role } from "../types";

// Always use const ai = new GoogleGenAI({apiKey: process.env.API_KEY});
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const getSystemInstruction = (role: Role) => {
  const baseInstruction = `You are FinSolve AI, an advanced internal RAG-based assistant for FinSolve Technologies. 
  You respond in a professional, high-end manner suitable for corporate environments.
  Always include simulated "sources" in your response when discussing internal data.
  The current user has ${role} access level. 
  Only share data relevant to the ${role} department. If data is outside their silo, politely decline or suggest contacting the relevant lead.`;

  switch (role) {
    case Role.FINANCE:
      return `${baseInstruction} Focus on P&L, quarterly projections, and budget optimization.`;
    case Role.C_LEVEL:
      return `${baseInstruction} Focus on high-level strategic summaries, KPI dashboards, and multi-departmental synergy. You have full visibility across silos.`;
    case Role.HR:
      return `${baseInstruction} Focus on employee benefits, recruitment pipelines, and workplace policy updates.`;
    case Role.MARKETING:
      return `${baseInstruction} Focus on campaign ROI, brand sentiment analysis, and market share growth.`;
    default:
      return baseInstruction;
  }
};

export const chatWithAI = async (
  prompt: string, 
  role: Role, 
  onChunk: (text: string) => void
) => {
  try {
    const response = await ai.models.generateContentStream({
      model: 'gemini-3-flash-preview',
      contents: prompt,
      config: {
        systemInstruction: getSystemInstruction(role),
        temperature: 0.7,
      },
    });

    let fullText = "";
    for await (const chunk of response) {
      // Use the .text property directly to extract content
      const text = chunk.text;
      if (text) {
        fullText += text;
        onChunk(text);
      }
    }
    return fullText;
  } catch (error) {
    console.error("Gemini API Error:", error);
    throw error;
  }
};
