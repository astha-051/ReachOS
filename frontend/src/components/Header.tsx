import React from "react";
import { Sparkles, Database, Search, ShieldCheck, Zap } from "lucide-react";

interface HeaderProps {
  demoMode?: boolean;
  onRefresh?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ demoMode = true, onRefresh }) => {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-gray-800/80 bg-gray-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Logo & Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-cyan-500 to-emerald-400 p-0.5 shadow-lg shadow-indigo-500/20">
            <div className="w-full h-full bg-gray-950 rounded-[10px] flex items-center justify-center">
              <Zap className="w-5 h-5 text-cyan-400 fill-cyan-400/20" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xl tracking-tight text-white">ReachOS</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                AI Platform
              </span>
            </div>
            <p className="text-xs text-gray-400 hidden sm:block">B2B Sales Intelligence & Autonomous Outreach</p>
          </div>
        </div>

        {/* AI Tech Stack Badges */}
        <div className="hidden lg:flex items-center space-x-2">
          {/* NVIDIA Nemotron Badge */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 text-xs font-medium shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span>NVIDIA Nemotron</span>
          </div>

          {/* Nebius Token Factory Badge */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-cyan-400 text-xs font-medium">
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <span>Nebius Token Factory</span>
          </div>

          {/* Tavily Web Research Badge */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-purple-950/40 border border-purple-500/30 text-purple-300 text-xs font-medium">
            <Search className="w-3.5 h-3.5 text-purple-400" />
            <span>Tavily Research</span>
          </div>
        </div>

        {/* Status & Controls */}
        <div className="flex items-center space-x-3">
          {demoMode && (
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-medium">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Hackathon Demo Mode</span>
            </div>
          )}

          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-2 rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:border-gray-700 transition"
              title="Refresh Data"
            >
              <Zap className="w-4 h-4" />
            </button>
          )}
        </div>

      </div>
    </header>
  );
};
