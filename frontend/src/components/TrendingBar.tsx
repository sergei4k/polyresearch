"use client";

import { useEffect, useState } from "react";
import { TrendingUp, ArrowUp, ArrowDown } from "lucide-react";

interface Market {
  id: string;
  category: {
    label: string;
  };
  event_title: string;
  question: string;
  yes_price: number;
  no_price: number;
  volume_24h: number;
  url: string;
}

interface TrendingResponse {
  markets: Market[];
  status: string;
}

export function TrendingBar() {
  const [markets, setMarkets] = useState<Market[]>([]);

  useEffect(() => {
    async function fetchTrending() {
      try {
        const res = await fetch("/api/trendings");
        const data: TrendingResponse = await res.json();
        if (data.status === "success") {
          setMarkets(data.markets);
        }
      } catch (error) {
        console.error("Failed to fetch trending markets:", error);
      }
    }

    fetchTrending();
  }, []);

  if (markets.length === 0) return null;

  // Duplicate items for seamless loop
  const displayMarkets = [...markets, ...markets]; // Double is usually enough for screen width coverage

  return (
    <div className="flex-1 flex items-center overflow-hidden h-full mask-linear-fade">
      <div className="flex items-center gap-2 px-4 h-full border-l border-border/50 shrink-0 ml-4">
        <TrendingUp className="w-3 h-3 text-primary animate-pulse" />
        <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground whitespace-nowrap">
          Trending
        </span>
      </div>
      
      <div className="relative flex overflow-hidden w-full group h-full items-center">
        <div className="flex animate-marquee hover:pause whitespace-nowrap items-center">
            {displayMarkets.map((market, i) => (
                <a 
                    key={`${market.id}-${i}`}
                    href={market.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 px-4 hover:bg-muted/30 transition-colors cursor-pointer rounded-md mx-1 py-1"
                >
                    <span className="text-xs font-medium text-foreground/90">
                        {market.event_title}
                    </span>
                    <div className="flex items-center gap-2 text-[10px] font-mono">
                        <span className="text-primary font-bold">Yes {market.yes_price}%</span>
                        <span className="text-muted-foreground">No {market.no_price}%</span>
                    </div>
                </a>
            ))}
        </div>
        <div className="flex absolute top-0 animate-marquee2 hover:pause whitespace-nowrap items-center h-full">
             {displayMarkets.map((market, i) => (
                <a 
                    key={`${market.id}-${i}-duplicate`}
                    href={market.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 px-4 hover:bg-muted/30 transition-colors cursor-pointer rounded-md mx-1 py-1"
                >
                    <span className="text-xs font-medium text-foreground/90">
                        {market.event_title}
                    </span>
                    <div className="flex items-center gap-2 text-[10px] font-mono">
                        <span className="text-primary font-bold">Yes {market.yes_price}%</span>
                        <span className="text-muted-foreground">No {market.no_price}%</span>
                    </div>
                </a>
            ))}
        </div>
      </div>
      
      {/* Styles for marquee animation */}
      <style jsx>{`
        .animate-marquee {
          animation: marquee 10000s linear infinite;
        }
        .animate-marquee2 {
          animation: marquee2 10000s linear infinite;
        }
        .group:hover .animate-marquee,
        .group:hover .animate-marquee2 {
            animation-play-state: paused;
        }
        .mask-linear-fade {
            mask-image: linear-gradient(to right, transparent, black 20px, black 95%, transparent);
        }

        @keyframes marquee {
          0% { transform: translateX(0%); }
          100% { transform: translateX(-100%); }
        }
        @keyframes marquee2 {
          0% { transform: translateX(100%); }
          100% { transform: translateX(0%); }
        }
      `}</style>
    </div>
  );
}
