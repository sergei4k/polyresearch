
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
    try {
        const body = await request.json();

        let data;
        try {
            // Forward request to Python backend
            const response = await fetch('http://127.0.0.1:5002/api/filter_markets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
            });

            if (!response.ok) {
                throw new Error(`Backend responded with ${response.status}`);
            }

            data = await response.json();
        } catch (backendError) {
            console.warn("Backend unavailable, using mock data:", backendError);
            // Mock response data
            data = {
                message: "Filters applied successfully (Mock Data)",
                filtersReceived: body,
                results: [
                    { id: 1, name: "Result A", score: 98 },
                    { id: 2, name: "Result B", score: 85 },
                ]
            };
        }

        return NextResponse.json(data);

    } catch (error) {
        console.error("Error processing filter request:", error);
        return NextResponse.json(
            { error: "Failed to process filters" },
            { status: 500 }
        );
    }
}
