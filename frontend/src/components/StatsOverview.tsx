import React from "react";
import { Users, SearchCheck, Flame, CheckCircle2, Send, MessageSquareHeart } from "lucide-react";
import { DashboardStats } from "../lib/api";

interface StatsOverviewProps {
  stats?: DashboardStats | null;
  isLoading?: boolean;
}

export const StatsOverview: React.FC<StatsOverviewProps> = ({ stats, isLoading }) => {
  const cards = [
    {
      title: "Total Leads",
      value: stats?.total_leads ?? 0,
      icon: Users,
      color: "from-blue-500/20 to-indigo-500/20 text-blue-400 border-blue-500/30",
      description: "Imported & validated"
    },
    {
      title: "Tavily Researched",
      value: stats?.research_completed ?? 0,
      icon: SearchCheck,
      color: "from-purple-500/20 to-pink-500/20 text-purple-400 border-purple-500/30",
      description: "Deep web intelligence"
    },
    {
      title: "High Priority",
      value: stats?.high_priority_leads ?? 0,
      icon: Flame,
      color: "from-amber-500/20 to-orange-500/20 text-amber-400 border-amber-500/30",
      description: "Nemotron score >= 80"
    },
    {
      title: "Outreach Approved",
      value: stats?.emails_approved ?? 0,
      icon: CheckCircle2,
      color: "from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-500/30",
      description: "Human-in-the-loop verified"
    },
    {
      title: "Emails Sent",
      value: stats?.emails_sent ?? 0,
      icon: Send,
      color: "from-cyan-500/20 to-blue-500/20 text-cyan-400 border-cyan-500/30",
      description: "Resend / Mock Provider"
    },
    {
      title: "Interested Replies",
      value: stats?.interested_replies ?? 0,
      icon: MessageSquareHeart,
      color: "from-rose-500/20 to-pink-500/20 text-rose-400 border-rose-500/30",
      description: "Meeting intent detected"
    }
  ];

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 my-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-28 rounded-xl bg-gray-900/60 border border-gray-800 animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 my-6">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`p-4 rounded-xl glass-panel bg-gradient-to-br ${card.color} border transition-all duration-200 hover:scale-[1.02]`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-gray-300">{card.title}</span>
              <Icon className="w-4 h-4 opacity-80" />
            </div>
            <div className="text-2xl font-black tracking-tight text-white mb-1">
              {card.value}
            </div>
            <p className="text-[11px] text-gray-400">{card.description}</p>
          </div>
        );
      })}
    </div>
  );
};
