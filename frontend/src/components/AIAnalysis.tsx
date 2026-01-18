"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

interface Profile {
  wallet: string;
  handle: string;
  profit: number;
  trades: number;
}

interface AIAnalysisProps {
  profiles: Profile[];
  lastUpdated: number;
}

export function AIAnalysis({ profiles, lastUpdated }: AIAnalysisProps) {
  const [analysis, setAnalysis] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    async function fetchAnalysis() {
      if (profiles.length === 0 || lastUpdated === 0) return;

      setLoading(true);
      try {
        const res = await fetch("/api/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ profiles }),
        });

        if (res.ok) {
          const data = await res.json();
          setAnalysis(data.analysis);
        } else {
          console.error("Failed to fetch analysis");
          setAnalysis("Unable to generate analysis at this time.");
        }
      } catch (error) {
        console.error("Error fetching analysis:", error);
        setAnalysis("An error occurred while generating insights.");
      } finally {
        setLoading(false);
      }
    }

    fetchAnalysis();
  }, [lastUpdated]);

  return (
    <div className="space-y-4">
      <h3 className="font-serif text-xl font-bold text-green-500">
        AI Analysis
      </h3>
      
      <div className="min-h-[80px] text-gray-100 text-sm leading-relaxed transition-opacity duration-500">
        {loading ? (
          <div className="flex items-center gap-2 text-purple-400 animate-pulse">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Generating insights...</span>
          </div>
        ) : (
          <p className="whitespace-pre-wrap">{analysis}</p>
        )}
      </div>
    </div>
  );
}
