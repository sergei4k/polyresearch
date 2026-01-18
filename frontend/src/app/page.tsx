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
  Loader2,
  SquareEqual
} from "lucide-react";

interface Profile {
  wallet: string;
  profit: number;
  trades: number;
  trade_gain: number;
  activity_gain: number;
  activity_count: number;
}

export default function Home() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedMarket, setSelectedMarket] = useState("Trending");
  const [hours, setHours] = useState(1);
  const [moneyGain, setMoneyGain] = useState(0);
  const [moneyGainCondition, setMoneyGainCondition] = useState<"reset" | "more" | "less" | "equal">("reset");
  const [moneyLost, setMoneyLost] = useState(0);
  const [moneyLostCondition, setMoneyLostCondition] = useState<"reset" | "more" | "less" | "equal">("reset");
  const [totalMoneySpent, setTotalMoneySpent] = useState(0);
  const [totalMoneySpentCondition, setTotalMoneySpentCondition] = useState<"reset" | "more" | "less" | "equal">("reset");
  const [tradesCondition, setTradesCondition] = useState<"reset" | "more" | "less" | "equal">("reset");
  const [tradesCount, setTradesCount] = useState(0);
  const [userNameVisibility, setUserNameVisibility] = useState<"hidden" | "public">("public");
  const [accountAgeDays, setAccountAgeDays] = useState(0);
  const [accountAgeCondition, setAccountAgeCondition] = useState<"reset" | "more" | "less" | "equal">("reset");
  const [isApplying, setIsApplying] = useState(false);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [error, setError] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleApply = async () => {
    setIsApplying(true);
    setError(null);
    try {
      const response = await fetch("/api/filter", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          market: selectedMarket,
          hours,
          money_gain: {
            condition: moneyGainCondition,
            amount: moneyGain
          },
          money_lost: {
            condition: moneyLostCondition,
            amount: moneyLost
          },
          total_money_spent: {
            condition: totalMoneySpentCondition,
            amount: totalMoneySpent
          },
          trades: {
            condition: tradesCondition,
            amount: tradesCount
          },
          account_age: {
            condition: accountAgeCondition,
            amount: accountAgeDays
          },
          userNameVisibility,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to apply filters");
      }

      const data = await response.json();
      console.log("Filters applied:", data);

      if (data.status === 'success' && data.profiles) {
        setProfiles(data.profiles);
      } else if (data.error) {
        setError(data.error);
      }

    } catch (error) {
      console.error("Error applying filters:", error);
      setError("Failed to fetch profiles. Make sure the backend is running.");
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
        <section className="col-span-7 flex flex-col p-8 overflow-hidden">
          {error && (
            <div className="mb-4 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500">
              {error}
            </div>
          )}

          {profiles.length > 0 ? (
            <div className="flex-1 overflow-auto">
              <div className="mb-4">
                <h2 className="text-2xl font-bold mb-2">Top 10 Profiles</h2>
                <p className="text-sm text-muted-foreground">
                  Showing {profiles.length} profiles based on your filters
                </p>
              </div>

              <div className="rounded-lg border border-border overflow-hidden">
                <table className="w-full">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        Rank
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        Wallet Address
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        Profit
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        Trades
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        Trade Gain
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        Activity Gain
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {profiles.map((profile, index) => (
                      <tr key={profile.wallet} className="hover:bg-muted/50 transition-colors">
                        <td className="px-4 py-3 text-sm font-medium">
                          #{index + 1}
                        </td>
                        <td className="px-4 py-3 text-sm font-mono">
                          {profile.wallet.slice(0, 6)}...{profile.wallet.slice(-4)}
                        </td>
                        <td className="px-4 py-3 text-sm text-right font-bold text-green-500">
                          ${profile.profit.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-sm text-right">
                          {profile.trades}
                        </td>
                        <td className="px-4 py-3 text-sm text-right">
                          ${profile.trade_gain.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-sm text-right">
                          ${profile.activity_gain.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <TrendingUp className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">No Results Yet</h3>
                <p className="text-sm text-muted-foreground">
                  Set your filters and click Apply to see top profiles
                </p>
              </div>
            </div>
          )}
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
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">TIMEFRAME IN HOURS</span>
              <span className="text-sm font-bold text-primary">{hours}h</span>
            </div>
            <input
              type="range"
              min="1"
              max="24"
              value={hours}
              onChange={(e) => setHours(parseInt(e.target.value))}
              className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-primary [&::-moz-range-thumb]:border-0"
            />
          </div>

          <div className="space-y-4">
            {/* Money Filters */}
            {[
              { 
                label: "Money Gain", 
                value: moneyGain, 
                setValue: setMoneyGain,
                condition: moneyGainCondition,
                setCondition: setMoneyGainCondition
              },
              { 
                label: "Money Lost", 
                value: moneyLost, 
                setValue: setMoneyLost,
                condition: moneyLostCondition,
                setCondition: setMoneyLostCondition
              },
              { 
                label: "Total Money Spent", 
                value: totalMoneySpent, 
                setValue: setTotalMoneySpent,
                condition: totalMoneySpentCondition,
                setCondition: setTotalMoneySpentCondition
              },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between">
                <div className="flex flex-col gap-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{item.label}</span>
                  <div className="flex items-center bg-muted rounded-md p-0.5">
                    {(['reset', 'more', 'less', 'equal'] as const).map((mode) => (
                      <button
                        key={mode}
                        onClick={() => item.setCondition(mode)}
                        className={`
                          px-2 py-1 text-[10px] uppercase font-bold rounded-sm transition-all flex items-center justify-center
                          ${item.condition === mode 
                            ? 'bg-background text-foreground shadow-sm' 
                            : 'text-muted-foreground hover:text-foreground'
                          }
                        `}
                      >
                        {mode === 'equal' ? <SquareEqual className="h-3 w-3" /> : mode}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="flex items-center justify-between rounded-md border border-border mt-auto min-w-[140px]">
                  <button 
                    onClick={() => {
                      if (item.condition === 'reset') {
                        item.setCondition('more');
                        item.setValue(0);
                      } else {
                        item.setValue(Math.max(0, item.value - 100));
                      }
                    }}
                    className="p-3 text-muted-foreground transition-colors hover:text-foreground"
                  >
                    <Minus className="h-4 w-4" />
                  </button>
                  <div className="flex items-center justify-center px-1">
                    <input
                      type="text"
                      value={item.condition === 'reset' ? "--" : item.value}
                      readOnly={item.condition === 'reset'}
                      onClick={() => {
                        if (item.condition === 'reset') {
                          item.setCondition('more');
                          item.setValue(0);
                        }
                      }}
                      onChange={(e) => {
                        if (item.condition === 'reset') {
                          item.setCondition('more');
                        }
                        const val = parseInt(e.target.value);
                        if (!isNaN(val)) {
                          item.setValue(val);
                        }
                      }}
                      style={{ width: `${Math.max(3, item.condition === 'reset' ? 2 : item.value.toString().length)}ch` }}
                      className="bg-transparent text-center text-sm font-mono text-foreground focus:outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none cursor-pointer"
                    />
                    <span className="text-sm text-muted-foreground ml-1">$</span>
                  </div>
                  <button 
                    onClick={() => {
                      if (item.condition === 'reset') {
                        item.setCondition('more');
                        item.setValue(0);
                      } else {
                        item.setValue(item.value + 100);
                      }
                    }}
                    className="p-3 text-muted-foreground transition-colors hover:text-foreground"
                  >
                    <Plus className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="space-y-4 mt-4">
            <div className="flex items-center justify-between">
              <div className="flex flex-col gap-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">TRADES DONE</span>
                <div className="flex items-center bg-muted rounded-md p-0.5">
                  {(['reset', 'more', 'less', 'equal'] as const).map((mode) => (
                    <button
                      key={mode}
                      onClick={() => setTradesCondition(mode)}
                      className={`
                        px-2 py-1 text-[10px] uppercase font-bold rounded-sm transition-all flex items-center justify-center
                        ${tradesCondition === mode 
                          ? 'bg-background text-foreground shadow-sm' 
                          : 'text-muted-foreground hover:text-foreground'
                        }
                      `}
                    >
                      {mode === 'equal' ? <SquareEqual className="h-3 w-3" /> : mode}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex items-center justify-between rounded-md border border-border mt-auto min-w-[140px]">
                <button 
                  onClick={() => {
                    if (tradesCondition === 'reset') {
                      setTradesCondition('more');
                      setTradesCount(0);
                    } else {
                      setTradesCount(Math.max(0, tradesCount - 1));
                    }
                  }}
                  className="p-3 text-muted-foreground transition-colors hover:text-foreground"
                >
                  <Minus className="h-4 w-4" />
                </button>
                <div className="flex items-center justify-center px-1">
                  <input
                    type="text"
                    value={tradesCondition === 'reset' ? "--" : tradesCount}
                    readOnly={tradesCondition === 'reset'}
                    onClick={() => {
                        if (tradesCondition === 'reset') {
                          setTradesCondition('more');
                          setTradesCount(0);
                        }
                      }}
                    onChange={(e) => {
                        if (tradesCondition === 'reset') {
                          setTradesCondition('more');
                        }
                        const val = parseInt(e.target.value);
                        if (!isNaN(val)) {
                          setTradesCount(val);
                        }
                      }}
                    style={{ width: `${Math.max(3, tradesCondition === 'reset' ? 2 : tradesCount.toString().length)}ch` }}
                    className="bg-transparent text-center text-sm font-mono text-foreground focus:outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none cursor-pointer"
                  />
                </div>
                <button 
                  onClick={() => {
                    if (tradesCondition === 'reset') {
                      setTradesCondition('more');
                      setTradesCount(0);
                    } else {
                      setTradesCount(tradesCount + 1);
                    }
                  }}
                  className="p-3 text-muted-foreground transition-colors hover:text-foreground"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-4 mt-4">
            <div className="flex items-center justify-between">
              <div className="flex flex-col gap-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">MAX ACCOUNT AGE (DAYS)</span>
                <div className="flex items-center bg-muted rounded-md p-0.5">
                  {(['reset', 'more', 'less', 'equal'] as const).map((mode) => (
                    <button
                      key={mode}
                      onClick={() => setAccountAgeCondition(mode)}
                      className={`
                        px-2 py-1 text-[10px] uppercase font-bold rounded-sm transition-all flex items-center justify-center
                        ${accountAgeCondition === mode 
                          ? 'bg-background text-foreground shadow-sm' 
                          : 'text-muted-foreground hover:text-foreground'
                        }
                      `}
                    >
                      {mode === 'equal' ? <SquareEqual className="h-3 w-3" /> : mode}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex items-center justify-between rounded-md border border-border mt-auto min-w-[140px]">
                <button 
                  onClick={() => {
                    if (accountAgeCondition === 'reset') {
                      setAccountAgeCondition('more');
                      setAccountAgeDays(0);
                    } else {
                      setAccountAgeDays(Math.max(0, accountAgeDays - 1));
                    }
                  }}
                  className="p-3 text-muted-foreground transition-colors hover:text-foreground"
                >
                  <Minus className="h-4 w-4" />
                </button>
                <div className="flex items-center justify-center px-1">
                  <input 
                    type={accountAgeCondition === 'reset' ? "text" : "number"}
                    value={accountAgeCondition === 'reset' ? "--" : accountAgeDays}
                    onClick={() => {
                        if (accountAgeCondition === 'reset') {
                          setAccountAgeCondition('more');
                          setAccountAgeDays(0);
                        }
                      }}
                    onChange={(e) => {
                        if (accountAgeCondition === 'reset') {
                          setAccountAgeCondition('more');
                        }
                        setAccountAgeDays(parseInt(e.target.value) || 0);
                      }}
                    style={{ width: `${Math.max(3, accountAgeCondition === 'reset' ? 2 : accountAgeDays.toString().length)}ch` }}
                    className="bg-transparent text-center text-sm font-mono text-foreground focus:outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none cursor-pointer"
                  />
                  <span className="text-sm text-muted-foreground ml-1">d</span>
                </div>
                <button 
                  onClick={() => {
                    if (accountAgeCondition === 'reset') {
                      setAccountAgeCondition('more');
                      setAccountAgeDays(0);
                    } else {
                      setAccountAgeDays(accountAgeDays + 1);
                    }
                  }}
                  className="p-3 text-muted-foreground transition-colors hover:text-foreground"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>
            </div>
            {/* <p className="text-xs text-muted-foreground">Set to 0 to include all accounts</p> */} 
          </div>

          <div className="space-y-4 mt-4">
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
