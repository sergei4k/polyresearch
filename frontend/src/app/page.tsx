"use client";

import { useState, useRef, useEffect } from "react";
import { 
  Terminal, 
  Search, 
  FileText, 
  Shield, 
  User, 
  Play, 
  Clock, 
  TrendingUp, 
  Send,
  ChevronDown,
  Activity,
  Zap,
  LayoutDashboard,
  Minus,
  Plus,
  Loader2
} from "lucide-react";

export default function Home() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedMarket, setSelectedMarket] = useState("Trending");
  const [days, setDays] = useState(1);
  const [moneyGain, setMoneyGain] = useState(0);
  const [moneyLost, setMoneyLost] = useState(0);
  const [totalMoneySpent, setTotalMoneySpent] = useState(0);
  const [tradesCondition, setTradesCondition] = useState<"less" | "more">("less");
  const [tradesCount, setTradesCount] = useState(0);
  const [userNameVisibility, setUserNameVisibility] = useState<"hidden" | "public">("public");
  const [isApplying, setIsApplying] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleApply = async () => {
    setIsApplying(true);
    try {
      const response = await fetch("/api/filter", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          market: selectedMarket,
          days,
          moneyGain,
          moneyLost,
          totalMoneySpent,
          tradesCondition,
          tradesCount,
          userNameVisibility,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to apply filters");
      }

      const data = await response.json();
      console.log("Filters applied:", data);
      
      // Keep the loading state for a bit longer to show the "scrolling" effect if response is too fast
      // or just to let user see feedback.
      // await new Promise(resolve => setTimeout(resolve, 500)); 

    } catch (error) {
      console.error("Error applying filters:", error);
    } finally {
      setIsApplying(false);
    }
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const markets = [
    "Trending",
    "Breaking",
    "New",
    "Politics",
    "Sports",
    "Crypto",
    "Finance",
    "Geopolitics",
    "Earnings",
    "Tech",
    "Culture",
    "World",
    "Economy",
    "Climate & Science",
    "Elections",
    "Mentions"
  ];

  return (
    <div className="flex h-screen w-full flex-col bg-background text-foreground font-sans overflow-hidden">
      {/* Header */}
      <header className="flex h-14 items-center justify-between border-b border-border px-4 py-2">
        <div className="flex items-center gap-8 flex-1 overflow-hidden">
          <div className="flex items-center gap-2 flex-none">
            <LayoutDashboard className="h-4 w-4 text-primary" />
            <div className="flex flex-col">
              <span className="text-lg font-medium leading-none tracking-tight">PolyResearch</span>
            </div>
          </div>


        </div>

        <div className="flex items-center gap-4 flex-none pl-4">
          
        </div>
      </header>

      {/* Main Content */}
      <main className="grid flex-1 grid-cols-12 divide-x divide-border overflow-hidden">
        {/* Left Sidebar - Data Source & Stats */}
        <aside className="col-span-2 flex flex-col gap-6 p-4">


          <div className="rounded-xl border border-border p-4 shadow-sm">
            <div className="flex items-center justify-between py-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
                <span className="text-primary">$</span> Exposure
              </span>
              <span className="font-mono text-sm font-bold">$17,880</span>
            </div>
            <div className="mt-2 flex items-center justify-between border-t border-border pt-3">
              <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
                <Activity className="h-3 w-3 text-red-500" /> PNL
              </span>
              <span className="font-mono text-sm font-bold text-red-500">-$779</span>
            </div>
          </div>
        </aside>

        {/* Center Panel - Main Features */}
        <section className="col-span-7 flex flex-col items-center justify-center p-8">
          
        </section>

        {/* Right Sidebar - Market Navigation */}
        <aside className="col-span-3 flex flex-col border-l border-border h-full overflow-hidden">
          <div className="flex-1 overflow-y-auto p-6">
            <div className="space-y-2 mb-8 relative" ref={dropdownRef}>
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Market Name</span>
            <button 
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex w-full items-center justify-between rounded-lg border border-border px-3 py-2 text-sm font-medium shadow-sm transition-colors hover:border-primary/50"
            >
              {selectedMarket}
              <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
            </button>
            
            {isDropdownOpen && (
              <div className="absolute top-full left-0 mt-2 w-full rounded-lg border border-border bg-card shadow-lg z-10 max-h-64 overflow-y-auto">
                <div className="p-1">
                  {markets.map((market) => (
                    <button
                      key={market}
                      onClick={() => {
                        setSelectedMarket(market);
                        setIsDropdownOpen(false);
                      }}
                      className="flex w-full items-center rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground text-left"
                    >
                      {market}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-4 mb-8">
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">TIMEFRAME IN DAYS</span>
            <div className="flex items-center justify-between gap-1">
              {[1, 2, 3, 4, 5, 6, 7].map((d) => (
                <button
                  key={d}
                  onClick={() => setDays(d)}
                  className={`flex h-8 w-full items-center justify-center rounded-md text-xs font-bold transition-colors ${
                    days === d
                      ? "bg-primary text-primary-foreground" 
                      : "bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground"
                  }`}
                >
                  {d}d
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            {[
              { label: "Money Gain", value: moneyGain, setValue: setMoneyGain },
              { label: "Money Lost", value: moneyLost, setValue: setMoneyLost },
              { label: "Total Money Spent", value: totalMoneySpent, setValue: setTotalMoneySpent },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between">
                <span className="text-sm font-medium">{item.label}</span>
                <div className="flex items-center rounded-md border border-border">
                  <button 
                    onClick={() => item.setValue(Math.max(0, item.value - 1))}
                    className="p-2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <Minus className="h-3 w-3" />
                  </button>
                  <div className="flex items-center justify-center px-1">
                    <input 
                      type="number"
                      value={item.value}
                      onChange={(e) => item.setValue(parseInt(e.target.value) || 0)}
                      style={{ width: `${Math.max(3, item.value.toString().length)}ch` }}
                      className="bg-transparent text-center text-sm font-mono text-foreground focus:outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                    />
                    <span className="text-sm text-muted-foreground ml-1">$</span>
                  </div>
                  <button 
                    onClick={() => item.setValue(item.value + 1)}
                    className="p-2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <Plus className="h-3 w-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="space-y-4 mt-8">
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">TRADES DONE</span>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button 
                  onClick={() => setTradesCondition(tradesCondition === "less" ? "more" : "less")}
                  className="text-sm font-medium hover:text-primary transition-colors min-w-[3.5rem] text-center border border-border rounded-md px-2 py-1"
                >
                  {tradesCondition === "less" ? "< less" : "> more"}
                </button>
                <span className="text-sm text-muted-foreground">than</span>
              </div>
              <div className="flex items-center rounded-md border border-border">
                <button 
                  onClick={() => setTradesCount(Math.max(0, tradesCount - 1))}
                  className="p-2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  <Minus className="h-3 w-3" />
                </button>
                <div className="flex items-center justify-center px-1">
                  <input 
                    type="number"
                    value={tradesCount}
                    onChange={(e) => setTradesCount(parseInt(e.target.value) || 0)}
                    style={{ width: `${Math.max(3, tradesCount.toString().length)}ch` }}
                    className="bg-transparent text-center text-sm font-mono text-foreground focus:outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                  />
                </div>
                <button 
                  onClick={() => setTradesCount(tradesCount + 1)}
                  className="p-2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  <Plus className="h-3 w-3" />
                </button>
              </div>
              </div>
          </div>

          <div className="space-y-4 mt-8">
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">USER NAME</span>
            <div className="flex items-center">
              <button 
                onClick={() => setUserNameVisibility(userNameVisibility === "hidden" ? "public" : "hidden")}
                className="text-sm font-medium hover:text-primary transition-colors min-w-[5rem] text-center border border-border rounded-md px-2 py-1"
              >
                {userNameVisibility === "hidden" ? "hidden" : "public"}
              </button>
            </div>
          </div>
          </div>

          <div className="p-6 border-t border-border">
            <button 
              onClick={handleApply}
              disabled={isApplying}
              className="w-full rounded-md bg-primary py-2 text-sm font-bold text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isApplying ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                "Apply"
              )}
            </button>
          </div>
        </aside>
      </main>
    </div>
  );
}
