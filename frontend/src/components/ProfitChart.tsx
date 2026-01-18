"use client";

import { useMemo } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

interface Profile {
  wallet: string;
  handle: string;
  profit: number;
}

interface ProfitChartProps {
  profiles: Profile[];
}

const COLORS = [
  "#10b981", // Emerald 500
  "#3b82f6", // Blue 500
  "#8b5cf6", // Violet 500
  "#ec4899", // Pink 500
  "#f59e0b", // Amber 500
  "#06b6d4", // Cyan 500
  "#84cc16", // Lime 500
  "#d946ef", // Fuchsia 500
  "#f43f5e", // Rose 500
  "#6366f1", // Indigo 500
  "#71717a", // Zinc 500 (Others)
];

export function ProfitChart({ profiles }: ProfitChartProps) {
  const data = useMemo(() => {
    if (!profiles || profiles.length === 0) return [];

    // Sort by profit (descending) just in case
    const sorted = [...profiles].sort((a, b) => b.profit - a.profit);
    
    // Only take positive profits for the chart ideally, or handle logic as requested.
    // Assuming 'most Profit users' implies positive profit. 
    // If mixed, Pie chart usually needs absolute values or just positive. 
    // Let's filter for > 0 to be safe for a "Profit" chart.
    const profitable = sorted.filter(p => p.profit > 0);

    const top10 = profitable.slice(0, 10);
    const others = profitable.slice(10);

    const chartData = top10.map(p => ({
      name: p.handle,
      value: p.profit,
      wallet: p.wallet,
      isOthers: false
    }));

    if (others.length > 0) {
      const othersProfit = others.reduce((acc, curr) => acc + curr.profit, 0);
      chartData.push({
        name: "Others",
        value: othersProfit,
        wallet: "", // No single wallet
        isOthers: true
      });
    }

    return chartData;

  }, [profiles]);

  if (data.length === 0) return null;

  const renderCustomizedLabel = (props: any) => {
    const { cx, cy, midAngle, innerRadius, outerRadius, index, name } = props;
    if (index !== 0) return null;

    const RADIAN = Math.PI / 180;
    const radius = outerRadius + 30; // Distance for transparency line
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    
    // Line start point (on the edge of the pie)
    const xStart = cx + outerRadius * Math.cos(-midAngle * RADIAN);
    const yStart = cy + outerRadius * Math.sin(-midAngle * RADIAN);

    return (
      <g>
        <path d={`M${xStart},${yStart}L${x},${y}`} stroke="white" fill="none" />
        <text 
            x={x} 
            y={y} 
            fill="white" 
            textAnchor={x > cx ? 'start' : 'end'} 
            dominantBaseline="central"
            className="text-xs font-bold"
            dx={x > cx ? 8 : -8} // Padding from line end
        >
          {name}
        </text>
      </g>
    );
  };

  return (
    <div className="h-[300px] w-full flex items-center justify-center relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey="value"
              cursor="pointer"
              stroke="none"
              label={renderCustomizedLabel}
              labelLine={false}
              onClick={(data) => {
                  if (data && !data.isOthers && data.wallet) {
                      window.open(`https://polygonscan.com/address/${data.wallet}`, '_blank');
                  }
              }}
            >
              {data.map((entry, index) => (
                <Cell 
                    key={`cell-${index}`} 
                    fill={entry.isOthers ? COLORS[COLORS.length - 1] : COLORS[index % (COLORS.length - 1)]} 
                    className="hover:opacity-80 transition-opacity outline-none"
                    style={{ outline: 'none' }}
                />
              ))}
            </Pie>
            <Tooltip 
                content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                        <div className="bg-background/95 backdrop-blur-sm border border-border p-3 rounded-lg shadow-lg">
                        <p className="font-bold text-sm mb-1">{data.name}</p>
                        <p className="font-mono text-xs text-primary">
                            ${data.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </p>
                        {!data.isOthers && (
                            <p className="text-[10px] text-muted-foreground mt-1">
                                Click to view on Polygonscan
                            </p>
                        )}
                        </div>
                    );
                    }
                    return null;
                }}
            />
          </PieChart>
        </ResponsiveContainer>
        
        {/* Placeholder for "text on right side later" - maintaining layout space or centering */}
        {/* The user said "on right side, I will put some text later". 
            For now, keeping the chart centered is safest unless requested layout structure changes. 
            Detailed layout might require a flex container around this chart if text is concurrent.
        */}
    </div>
  );
}
