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
  Eye,
  Minus,
  Plus,
  Loader2,
  ExternalLink,
  X,
  Info
} from "lucide-react";
import { TrendingBar } from "@/components/TrendingBar";
import { ProfitChart } from "@/components/ProfitChart";
import { AIAnalysis } from "@/components/AIAnalysis";

interface Profile {
  wallet: string;
  handle: string;
  profit: number;
  trades: number;
}

export default function Home() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedMarket, setSelectedMarket] = useState("Trending");
  const [hours, setHours] = useState(1);
  const [moneyGain, setMoneyGain] = useState(0);
  const [moneyGainCondition, setMoneyGainCondition] = useState<"reset" | "more" | "less">("reset");
  const [moneyLost, setMoneyLost] = useState(0);
  const [moneyLostCondition, setMoneyLostCondition] = useState<"reset" | "more" | "less">("reset");
  const [totalMoneySpent, setTotalMoneySpent] = useState(0);
  const [totalMoneySpentCondition, setTotalMoneySpentCondition] = useState<"reset" | "more" | "less">("reset");
  const [tradesCondition, setTradesCondition] = useState<"reset" | "more" | "less">("reset");
  const [tradesCount, setTradesCount] = useState(0);
  const [userNameVisibility, setUserNameVisibility] = useState<"reset" | "public" | "hidden">("reset");
  const [accountAgeDays, setAccountAgeDays] = useState(0);
  const [accountAgeCondition, setAccountAgeCondition] = useState<"reset" | "more" | "less">("reset");
  const [isApplying, setIsApplying] = useState(false);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selectedProfiles, setSelectedProfiles] = useState<Profile[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isInfoOpen, setIsInfoOpen] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<number>(0);
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
        setLastUpdated(Date.now());
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

  // Auto-apply filters on initial load
  useEffect(() => {
    handleApply();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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

  // Auto-refresh when market filter changes
  const isFirstRender = useRef(true);
  useEffect(() => {
    // Skip the first render to avoid fetching on initial load
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    
    // Clear current profiles and fetch new data when market changes
    setProfiles([]);
    handleApply();
  }, [selectedMarket]);

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

  const formatK = (num: number) => {
    if (Math.abs(num) >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  return (
    <div className="flex h-screen w-full flex-col bg-background text-foreground font-sans overflow-hidden">
      {/* Header */}
      <header className="flex h-14 min-h-[3.5rem] max-h-[3.5rem] items-center justify-between border-b border-border px-4 py-2 shrink-0 overflow-hidden">
        <div className="flex items-center gap-8 flex-1 overflow-hidden">
          <div className="flex items-center gap-2 flex-none">
            <Eye className="h-5 w-5 text-primary" />
            <div className="flex flex-col">
              <span className="text-xl font-serif leading-none tracking-tight">PolyWatcher</span>
            </div>
          </div>

          <TrendingBar />
        </div>




        <div className="flex items-center gap-4 flex-none pl-4">
          
        </div>
      </header>

      {/* Main Content */}
      <main className="grid flex-1 grid-cols-12 divide-x divide-border overflow-hidden">
        {/* Left Sidebar - Data Source & Stats */}
        <aside className="col-span-2 flex flex-col gap-6 p-4">



          {/* Top Profits Section */}
          {profiles.length > 0 && (
            <div className="rounded-xl border border-border overflow-hidden mb-6">
               <div className="bg-muted/50 px-4 py-2 border-b border-border">
                 <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                   Top Profits
                 </span>
               </div>
               <div className="divide-y divide-border">
                 {[...profiles].sort((a, b) => b.profit - a.profit).slice(0, 3).map((profile) => (
                   <div key={`top-${profile.wallet}`} className="group flex items-center justify-between p-3 hover:bg-muted/20 transition-colors">
                     <div className="flex items-center gap-2 overflow-hidden">
                        <button
                          onClick={() => {
                            if (!selectedProfiles.find(p => p.wallet === profile.wallet)) {
                                setSelectedProfiles([...selectedProfiles, profile]);
                            }
                          }}
                          className="p-1 hover:bg-muted rounded-full transition-all text-muted-foreground hover:text-green-500"
                          title="Add to Watchlist"
                        >
                          <Plus className="h-3 w-3" />
                        </button>
                        <a
                          href={`https://polygonscan.com/address/${profile.wallet}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-mono text-sm text-foreground hover:text-primary hover:underline truncate"
                        >
                           {profile.handle || `${profile.wallet.slice(0, 6)}...`}
                        </a>
                     </div>
                     <span className="font-mono text-sm font-bold text-green-500 whitespace-nowrap">
                       ${formatK(profile.profit)}
                     </span>
                   </div>
                 ))}
               </div>
            </div>
          )}

          {selectedProfiles.length > 0 && (
            <div className="rounded-xl border border-border overflow-hidden">
               <div className="bg-muted/50 px-4 py-2 border-b border-border">
                 <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                   Selected Wallets
                 </span>
               </div>
               <div className="divide-y divide-border">
                 {selectedProfiles.map((profile) => (
                   <div key={profile.wallet} className="group flex items-center justify-between p-3 hover:bg-muted/20 transition-colors">
                     <div className="flex items-center gap-2 overflow-hidden">
                        <button
                          onClick={() => {
                            setSelectedProfiles(selectedProfiles.filter(p => p.wallet !== profile.wallet));
                          }}
                          className="opacity-0 group-hover:opacity-100 p-1 hover:bg-muted rounded-full transition-all"
                        >
                          <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                        </button>
                        <a
                          href={`https://polygonscan.com/address/${profile.wallet}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-mono text-sm text-muted-foreground hover:text-primary hover:underline truncate"
                        >
                           {profile.handle}
                        </a>
                     </div>
                     <span className="font-mono text-sm font-bold text-primary whitespace-nowrap">
                       ${formatK(profile.profit)}
                     </span>
                   </div>
                 ))}
               </div>
            </div>
          )}
          <div className="mt-auto space-y-4">
            <div className="p-3">
              <p className="text-base text-foreground/80 italic leading-relaxed">
                "The quieter you are, the more you can hear"
              </p>
              <span className="block text-lg mt-2 text-muted-foreground">— Ram Dass</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-1 cursor-pointer hover:opacity-80 transition-opacity">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Account</span>
              </div>
              <button
                onClick={() => setIsInfoOpen(true)}
                className="p-2 rounded-full hover:bg-muted transition-colors"
                title="About PolyWatcher"
              >
                <Info className="h-4 w-4 text-muted-foreground" />
              </button>
            </div>
          </div>
        </aside>

        {/* Info Popup */}
        {isInfoOpen && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setIsInfoOpen(false)}>
            <div 
              className="bg-card border border-border rounded-xl p-6 max-w-md mx-4 shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Eye className="h-5 w-5 text-primary" />
                  <h2 className="text-xl font-serif font-bold">PolyWatcher</h2>
                </div>
                <button
                  onClick={() => setIsInfoOpen(false)}
                  className="p-1 rounded-full hover:bg-muted transition-colors"
                >
                  <X className="h-4 w-4 text-muted-foreground" />
                </button>
              </div>
              <div className="space-y-3 text-md text-muted-foreground">
                <p>
                  Insider trading creates an unfair advantage based on information that you do not have.
                </p>
                <p>
                  <strong className="text-foreground">PolyWatcher</strong> helps you discover and track the most profitable traders on Polymarket.
                </p>
                <p>
                  Filter by market category, timeframe, profit thresholds, and more to find wallets worth following.
                </p>
                <p>
                  Use the filters on the right to narrow down results, then click on wallets to add them to your watchlist.
                </p>
                <div className="pt-3 border-t border-border mt-4">
                  <p className="text-xs text-muted-foreground/60">
                    Data sourced from Polymarket's public API. Not financial advice.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Center Panel - Main Features */}
        <section className="col-span-7 flex flex-col p-8 overflow-hidden">
          {error && (
            <div className="mb-4 p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive">
              {error}
            </div>
          )}

          {profiles.length > 0 ? (
            <div className="flex-1 overflow-auto no-scrollbar">
              <div className="mb-6 grid grid-cols-2 gap-8">
                <ProfitChart profiles={profiles} />
                <div className="flex flex-col justify-center">
                   <AIAnalysis profiles={profiles.slice(0, 10)} lastUpdated={lastUpdated} />
                </div>
              </div>
              <div className="mb-4">
                <h2 className="text-2xl font-serif mb-2">Top Profiles</h2>
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
                      <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        Handle
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        Profit
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        Trades
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {profiles.map((profile, index) => (
                      <tr key={profile.wallet} className="bg-muted/10 hover:bg-muted/20 transition-colors">
                        <td 
                          className="px-4 py-3 text-sm font-medium cursor-pointer relative group/rank w-[60px]"
                          onClick={() => {
                            if (!selectedProfiles.find(p => p.wallet === profile.wallet)) {
                              setSelectedProfiles([...selectedProfiles, profile]);
                            }
                          }}
                        >
                          <span className="group-hover/rank:opacity-0 transition-opacity">#{index + 1}</span>
                          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover/rank:opacity-100 transition-opacity">
                            <Plus className="h-4 w-4 text-primary" />
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm font-mono">
                          <a
                            href={`https://polygonscan.com/address/${profile.wallet}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-primary hover:underline transition-colors"
                          >
                            {profile.wallet.slice(0, 6)}...{profile.wallet.slice(-4)}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </td>
                        <td className="px-4 py-3 text-sm truncate max-w-[200px]" title={profile.handle}>
                          {profile.handle.length > 20 ? `${profile.handle.slice(0, 20)}...` : profile.handle}
                        </td>
                        <td className="px-4 py-3 text-sm text-right font-bold text-primary">
                          ${profile.profit.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-sm text-right">
                          {profile.trades}
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
                <h3 className="text-xl font-serif mb-2">No Results Yet</h3>
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
                  <div className="flex items-center bg-muted rounded-md p-0.5 w-fit">
                    {(['more', 'less'] as const).map((mode) => (
                      <button
                        key={mode}
                        onClick={() => {
                          if (item.condition === mode) {
                            item.setCondition('reset');
                          } else {
                            item.setCondition(mode);
                          }
                        }}
                        className={`
                          px-2 py-1 text-[10px] uppercase font-bold rounded-sm transition-all flex items-center justify-center
                          ${item.condition === mode 
                            ? 'bg-background text-foreground shadow-sm' 
                            : 'text-muted-foreground hover:text-foreground'
                          }
                        `}
                      >
                        {mode}
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
                <div className="flex items-center bg-muted rounded-md p-0.5 w-fit">
                  {(['more', 'less'] as const).map((mode) => (
                    <button
                      key={mode}
                      onClick={() => {
                        if (tradesCondition === mode) {
                          setTradesCondition('reset');
                        } else {
                          setTradesCondition(mode);
                        }
                      }}
                      className={`
                        px-2 py-1 text-[10px] uppercase font-bold rounded-sm transition-all flex items-center justify-center
                        ${tradesCondition === mode 
                          ? 'bg-background text-foreground shadow-sm' 
                          : 'text-muted-foreground hover:text-foreground'
                        }
                      `}
                    >
                      {mode}
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
                <div className="flex items-center bg-muted rounded-md p-0.5 w-fit">
                  {(['more', 'less'] as const).map((mode) => (
                    <button
                      key={mode}
                      onClick={() => {
                         if (accountAgeCondition === mode) {
                          setAccountAgeCondition('reset');
                        } else {
                          setAccountAgeCondition(mode);
                        }
                      }}
                      className={`
                        px-2 py-1 text-[10px] uppercase font-bold rounded-sm transition-all flex items-center justify-center
                        ${accountAgeCondition === mode 
                          ? 'bg-background text-foreground shadow-sm' 
                          : 'text-muted-foreground hover:text-foreground'
                        }
                      `}
                    >
                      {mode}
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
            <div className="flex flex-col gap-2 w-fit">
              <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">USER NAME</span>
              <div className="flex items-center bg-muted rounded-md p-0.5 w-fit">
                {(['public', 'hidden'] as const).map((mode) => (
                  <button
                    key={mode}
                    onClick={() => {
                        if (userNameVisibility === mode) {
                          setUserNameVisibility('reset');
                        } else {
                          setUserNameVisibility(mode);
                        }
                    }}
                    className={`
                      px-2 py-1 text-[10px] uppercase font-bold rounded-sm transition-all flex items-center justify-center
                      ${userNameVisibility === mode 
                        ? 'bg-background text-foreground shadow-sm' 
                        : 'text-muted-foreground hover:text-foreground'
                      }
                    `}
                  >
                    {mode}
                  </button>
                ))}
              </div>
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
