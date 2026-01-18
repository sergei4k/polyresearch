
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const {
            market,
            days,
            moneyGain,
            moneyLost,
            totalMoneySpent,
            tradesCondition,
            tradesCount,
            userNameVisibility,

        } = body;

        // Simulate backend processing
        console.log("Received filter request:", {
            market,
            days,
            moneyGain,
            moneyLost,
            totalMoneySpent,
            tradesCondition,
            tradesCount,
            userNameVisibility,

        });

        // Mock response data
        const mockData = {
            message: "Filters applied successfully",
            filtersReceived: body,
            results: [
                { id: 1, name: "Result A", score: 98 },
                { id: 2, name: "Result B", score: 85 },
            ]
        };

        // Simulate network delay if needed, but for now we return immediately as requested "scrolling" happens on frontend
        return NextResponse.json(mockData);

    } catch (error) {
        console.error("Error processing filter request:", error);
        return NextResponse.json(
            { error: "Failed to process filters" },
            { status: 500 }
        );
    }
}
