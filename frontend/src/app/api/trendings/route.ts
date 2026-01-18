import { NextResponse } from 'next/server';

export async function GET() {
    try {
        const res = await fetch('http://127.0.0.1:5000/api/trendings', {
            next: { revalidate: 60 } // Cache for 60 seconds
        });

        if (!res.ok) {
            throw new Error('Failed to fetch from backend');
        }

        const data = await res.json();

        // Transform backend event-based structure to flat market list
        const markets = [];
        if (data.status === 'success' && Array.isArray(data.events)) {
            for (const event of data.events) {
                if (Array.isArray(event.markets)) {
                    for (const market of event.markets) {
                        markets.push({
                            id: market.id,
                            category: {
                                label: event.category || 'Trending'
                            },
                            event_title: event.title,
                            question: market.question,
                            yes_price: market.yes_price,
                            no_price: market.no_price,
                            volume_24h: event.volume_24h,
                            url: event.url
                        });
                    }
                }
            }
        }

        return NextResponse.json({
            status: 'success',
            count: markets.length,
            markets: markets
        });
    } catch (error) {
        console.error('Error in trendings API route:', error);
        return NextResponse.json({
            status: 'error',
            message: 'Failed to fetch trending markets',
            markets: []
        }, { status: 500 });
    }
}
