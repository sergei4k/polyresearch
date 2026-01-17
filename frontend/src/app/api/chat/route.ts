import { NextResponse } from "next/server";

export async function POST(req: Request) {
    try {
        const { message } = await req.json();

        // THIS IS THE BACKEND.
        // You can call OpenAI, Anthropic, or your own Python backend here.

        // Example:
        // const response = await callMyModel(message);

        // For now, we just mock a response.
        const mockResponse = `I received your message: "${message}". This response comes from the API route.`;

        // Simulate network delay
        await new Promise((resolve) => setTimeout(resolve, 500));

        return NextResponse.json({ response: mockResponse });
    } catch (error) {
        console.error("Error in chat API:", error);
        return NextResponse.json(
            { error: "Failed to process message" },
            { status: 500 }
        );
    }
}
