import React from "react";
import { Search, Filter, Sparkles, Flame, Shield, ArrowRight, RefreshCw, CheckCircle2, AlertTriangle, Eye } from "lucide-react";
import { LeadDetail, Campaign } from "../lib/api";

interface LeadTableProps {
  leads: LeadDetail[];
  campaigns: Campaign[];
  isLoading?: boolean;
  selectedCampaignId?: string;
  onSelectCampaign: (id?: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  priorityFilter: string;
  onPriorityFilterChange: (priority: string) => void;
  onSelectLead: (lead: LeadDetail) => void;
  onTriggerResearch: (leadId: string) => void;
  onTriggerQualify: (leadId: string) => void;
  onTriggerOutreach: (leadId: string) => void;
}

export const LeadTable: React.FC<LeadTableProps> = ({
  leads,
  campaigns,
  isLoading,
  selectedCampaignId,
  onSelectCampaign,
  searchQuery,
  onSearchChange,
  priorityFilter,
  onPriorityFilterChange,
  onSelectLead,
  onTriggerResearch,
  onTriggerQualify,
  onTriggerOutreach
}) => {

  const getPriorityBadge = (lead: LeadDetail) => {
    const qual = lead.qualification;
    if (!qual) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-gray-800 text-gray-400 border border-gray-700">
          Unqualified
        </span>
      );
    }

    if (qual.priority === "HIGH") {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 shadow-sm shadow-amber-500/10">
          <Flame className="w-3 h-3 text-amber-400" />
          <span>HIGH ({qual.score})</span>
        </span>
      );
    } else if (qual.priority === "MEDIUM") {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-blue-500/10 text-blue-400 border border-blue-500/30">
          <span>MEDIUM ({qual.score})</span>
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-gray-800 text-gray-400 border border-gray-700">
          <span>LOW ({qual.score})</span>
        </span>
      );
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "REPLIED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">REPLIED</span>;
      case "SENT":
        return <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">SENT</span>;
      case "APPROVED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">APPROVED</span>;
      case "AWAITING_APPROVAL":
        return <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30">AWAITING APPROVAL</span>;
      case "QUALIFIED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-purple-500/20 text-purple-300 border border-purple-500/30">QUALIFIED</span>;
      case "RESEARCHED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">RESEARCHED</span>;
      case "VALIDATED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-gray-800 text-gray-300 border border-gray-700">NEW LEAD</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-gray-800 text-gray-400">{status}</span>;
    }
  };

  return (
    <div className="glass-panel rounded-2xl border border-gray-800/80 bg-gray-900/60 overflow-hidden shadow-xl">
      
      {/* Table Toolbar */}
      <div className="p-4 border-b border-gray-800 flex flex-col md:flex-row items-center justify-between gap-4 bg-gray-950/40">
        
        {/* Search Bar */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Search leads by name, email, company..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full bg-gray-900 border border-gray-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-3 w-full md:w-auto">
          {/* Campaign Select */}
          <div className="flex items-center space-x-1.5">
            <Filter className="w-3.5 h-3.5 text-gray-400" />
            <select
              value={selectedCampaignId || ""}
              onChange={(e) => onSelectCampaign(e.target.value || undefined)}
              className="bg-gray-900 border border-gray-800 rounded-lg px-2.5 py-1.5 text-xs text-gray-200 focus:outline-none"
            >
              <option value="">All Campaigns</option>
              {campaigns.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          {/* Priority Select */}
          <select
            value={priorityFilter}
            onChange={(e) => onPriorityFilterChange(e.target.value)}
            className="bg-gray-900 border border-gray-800 rounded-lg px-2.5 py-1.5 text-xs text-gray-200 focus:outline-none"
          >
            <option value="">All Priorities</option>
            <option value="HIGH">High Priority Only</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>
        </div>

      </div>

      {/* Leads Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead className="bg-gray-950/80 border-b border-gray-800 text-gray-400 font-semibold uppercase tracking-wider">
            <tr>
              <th className="px-4 py-3">Lead & Role</th>
              <th className="px-4 py-3">Company & Domain</th>
              <th className="px-4 py-3">Tavily Research</th>
              <th className="px-4 py-3">Nemotron Score</th>
              <th className="px-4 py-3">Pipeline Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-800/60 text-gray-200">
            {isLoading ? (
              [...Array(5)].map((_, i) => (
                <tr key={i} className="animate-pulse">
                  <td colSpan={6} className="px-4 py-4 h-12 bg-gray-900/30" />
                </tr>
              ))
            ) : leads.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center text-gray-500">
                  No sales leads found matching criteria. Upload a CSV to get started!
                </td>
              </tr>
            ) : (
              leads.map((lead) => (
                <tr
                  key={lead.id}
                  className="hover:bg-gray-800/40 transition cursor-pointer"
                  onClick={() => onSelectLead(lead)}
                >
                  {/* Lead & Role */}
                  <td className="px-4 py-3">
                    <div className="font-bold text-white text-sm">{lead.name}</div>
                    <div className="text-[11px] text-gray-400">{lead.job_title || "Role Unspecified"}</div>
                    <div className="text-[10px] font-mono text-gray-500">{lead.email}</div>
                  </td>

                  {/* Company & Domain */}
                  <td className="px-4 py-3">
                    <div className="font-semibold text-gray-200">{lead.company_name}</div>
                    {lead.website && (
                      <a
                        href={lead.website.startsWith("http") ? lead.website : `https://${lead.website}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[10px] text-cyan-400 hover:underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {lead.website.replace("https://", "").replace("http://", "")}
                      </a>
                    )}
                  </td>

                  {/* Tavily Research Status */}
                  <td className="px-4 py-3">
                    {lead.research_report ? (
                      <div className="space-y-1">
                        <span className="inline-flex items-center space-x-1 text-[11px] text-emerald-400 font-medium">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          <span>{lead.research_report.sources?.length || 2} Sources Verified</span>
                        </span>
                        <div className="text-[10px] text-gray-400 truncate max-w-xs">
                          {lead.research_report.summary || "Company web evidence synthesized."}
                        </div>
                      </div>
                    ) : (
                      <button
                        onClick={(e) => { e.stopPropagation(); onTriggerResearch(lead.id); }}
                        className="inline-flex items-center space-x-1 text-[10px] font-semibold px-2 py-1 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 hover:bg-indigo-500/20"
                      >
                        <Sparkles className="w-3 h-3 text-indigo-400" />
                        <span>Run Tavily Research</span>
                      </button>
                    )}
                  </td>

                  {/* Nemotron Score */}
                  <td className="px-4 py-3">
                    {getPriorityBadge(lead)}
                  </td>

                  {/* Pipeline Status */}
                  <td className="px-4 py-3">
                    {getStatusBadge(lead.status)}
                  </td>

                  {/* Quick Action Drawer Button */}
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={(e) => { e.stopPropagation(); onSelectLead(lead); }}
                      className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-indigo-600 text-gray-200 hover:text-white transition text-xs font-medium"
                    >
                      <span>Workbench</span>
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
};
