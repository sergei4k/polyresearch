import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
    try {
        const { profiles } = await req.json();

        if (!profiles || !Array.isArray(profiles)) {
            return NextResponse.json(
                { message: "Invalid profiles data" },
                { status: 400 }
            );
        }

        const apiKey = process.env.GEMINI_API_KEY;
        if (!apiKey) {
            return NextResponse.json(
                { message: "GEMINI_API_KEY is not configured" },
                { status: 500 }
            );
        }

        const genAI = new GoogleGenerativeAI(apiKey);
        const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash-exp" });

        // Prepare a summary of the data for the prompt
        // We limit to top 10 as per user request context, though profiles generic
        const summary = profiles.map((p: any) =>
            `- ${p.handle || p.wallet}: Profit $${p.profit}, Trades: ${p.trades}, Win Rate (if avail): ${p.win_rate || 'N/A'}`
        ).join("\n");

        const prompt = `
      Analyze the following top crypto trading profiles from a prediction market/trading dashboard.
      
      Important Context: Profit data shown is based on the specific timeframe currently selected by the user (e.g., 1d, 7d, etc.), NOT all-time profit.
      
      Instructions:
      1. **Direct Start:** Do NOT start with "Here is an analysis" or any introductory phrase. Jump straight into the insights.
      2. Use the user's handle. If >15 chars, shorten it (e.g., "0x1234...").
      3. Identify unique trading patterns:
         - High efficiency: Big profit with few trades.
         - Grinders: Many trades, steady profit.
      4. Mention that these profits are specific to the current selected timeframe if relevant to the context of their performance.
      5. Keep it professional and concise (3-4 sentences).

      Profiles Data:
      ${summary}
    `;

        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();

        return NextResponse.json({ analysis: text });
    } catch (error) {
        console.error("AI Analysis Error:", error);
        return NextResponse.json(
            { message: "Failed to generate analysis" },
            { status: 500 }
        );
    }
}
