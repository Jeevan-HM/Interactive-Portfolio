import { NextRequest, NextResponse } from "next/server";
import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from "fs/promises";
import path from "path";

const apiKey = process.env.GOOGLE_API_KEY;
const genAI = new GoogleGenerativeAI(apiKey || "");

async function loadBioFiles() {
    const bioDir = path.join(process.cwd(), "public/bio");
    let content = "";
    try {
        const files = await fs.readdir(bioDir);
        for (const file of files) {
            if (file.endsWith(".txt")) {
                const fileContent = await fs.readFile(path.join(bioDir, file), "utf-8");
                content += fileContent + "\n\n";
            }
        }
    } catch (error) {
        console.warn("Could not load bio files", error);
    }
    return content;
}

export async function POST(req: NextRequest) {
    try {
        if (!apiKey || apiKey === "") {
            return NextResponse.json({
                answer: "Hi there! I'm J.A.I.D. 👋<br/><br/>I am currently <b>offline</b> because my Google Gemini API Key has not been configured in the environment variables yet.<br/><br/>Please set <code>GOOGLE_API_KEY</code> to enable my AI capabilities!"
            }, { status: 200 });
        }
        const body = await req.json();
        const { message } = body;

        const bioContent = await loadBioFiles();

        const prompt = `
      You are J.A.I.D. (Jeevan's Artificial Intelligence Delegate), an AI assistant dedicated to helping people learn about Jeevan Hebbal Manjunath.

      # Role and Objective
          - Provide users with accurate, enticing, engaging, and interactive information about Jeevan Hebbal Manjunath.
          - Make conversations feel lively and dynamic - you're not a boring encyclopedia, you're an enthusiastic guide!
          - Use personality, emojis (when appropriate), and conversational language to keep users interested.
          - Be concise but captivating - every response should make users want to learn more.

      # Chat Window Constraints
          - The chat window is small. Avoid large titles, oversized headings, or wide tables. Use short, concise headings (prefer h4), and keep all content compact and readable.
          - Avoid long lines or wide blocks of text. Use lists and short paragraphs for clarity.

      # Personality and Engagement
          - Be warm, friendly, and conversational - not robotic or monotonous.
          - Use varied sentence structures and expressive language.
          - Add emojis.

      # Instructions
          - Use only the supplied context to respond accurately to inquiries about Jeevan.
          - Answer concisely.

      # Output Format
          - Always return your response as valid HTML without markdown wrapped formatting like \`\`\`html. Use appropriate HTML tags for lists, headings, bold, italics, and code blocks so that the output is visually appealing and ready to be rendered directly in a web interface.
          
      **Context about Jeevan:**
      ${bioContent}

      **User Input:**
      ${message}
    `;

        const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });
        const result = await model.generateContent(prompt);
        let text = result.response.text();

        text = text.replace(/^```html/i, "").replace(/```$/i, "").trim();

        return NextResponse.json({ answer: text });
    } catch (err: any) {
        return NextResponse.json({ error: err.message, answer: "I'm having trouble connecting right now." }, { status: 500 });
    }
}
