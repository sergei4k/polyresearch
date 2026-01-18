
import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:5000';

export async function POST(request: Request) {
    try {
        const body = await request.json();

        console.log("Forwarding filter request to backend:", body);

        // Forward request to Flask backend
        const backendResponse = await fetch(`${BACKEND_URL}/api/filter_markets`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!backendResponse.ok) {
            throw new Error(`Backend responded with status: ${backendResponse.status}`);
        }

        const data = await backendResponse.json();

        console.log("Received response from backend:", data);

        return NextResponse.json(data);

    } catch (error) {
        console.error("Error processing filter request:", error);
        return NextResponse.json(
            {
                error: "Failed to process filters",
                details: error instanceof Error ? error.message : 'Unknown error'
            },
            { status: 500 }
        );
    }
}
