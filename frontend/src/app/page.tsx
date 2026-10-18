"use client";

import React, { useEffect, useState } from "react";
import { Plus, UploadCloud, RefreshCw, Zap, Sparkles, Database, Search } from "lucide-react";
import { Header } from "@/components/Header";
import { StatsOverview } from "@/components/StatsOverview";
import { LeadTable } from "@/components/LeadTable";
import { CSVImportModal } from "@/components/CSVImportModal";
import { LeadDetailDrawer } from "@/components/LeadDetailDrawer";
import { api, DashboardStats, Campaign, LeadDetail } from "@/lib/api";

export default function Home() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [leads, setLeads] = useState<LeadDetail[]>([]);
  
  const [isLoading, setIsLoading] = useState(true);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [selectedLead, setSelectedLead] = useState<LeadDetail | null>(null);

  // Filters
  const [selectedCampaignId, setSelectedCampaignId] = useState<string | undefined>(undefined);
  const [searchQuery, setSearchQuery] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [statsData, campaignsData, leadsData] = await Promise.all([
        api.getStats().catch(() => null),
        api.getCampaigns().catch(() => []),
        api.getLeads({
          campaign_id: selectedCampaignId,
          priority: priorityFilter || undefined,
          search: searchQuery || undefined
        }).catch(() => [])
      ]);

      if (statsData) setStats(statsData);
      setCampaigns(campaignsData);
      setLeads(leadsData);
    } catch (err) {
      console.error("Failed loading dashboard data:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedCampaignId, priorityFilter, searchQuery]);

  const handleRefreshLead = async (leadId: string) => {
    try {
      const updatedLead = await api.getLead(leadId);
      setSelectedLead(updatedLead);
      loadData();
    } catch (err) {
      console.error("Failed refreshing lead detail:", err);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-gray-100 font-sans flex flex-col selection:bg-indigo-500 selection:text-white">
      
      {/* Header Bar */}
      <Header demoMode={true} onRefresh={loadData} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Hero / Action Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-gray-800/80">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center space-x-2">
              <span>Sales Intelligence & Lead Workbench</span>
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              Autonomous lead research with Tavily and explainable qualification powered by NVIDIA Nemotron.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsImportModalOpen(true)}
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-semibold text-xs shadow-lg shadow-indigo-500/20 transition-all hover:scale-[1.02]"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Import Leads CSV</span>
            </button>
          </div>
        </div>

        {/* Dashboard Metrics Overview */}
        <StatsOverview stats={stats} isLoading={isLoading} />

        {/* Interactive Leads Table */}
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <span>Prospect Pipeline</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 font-medium">
                {leads.length} Leads
              </span>
            </h2>
          </div>

          <LeadTable
            leads={leads}
            campaigns={campaigns}
            isLoading={isLoading}
            selectedCampaignId={selectedCampaignId}
            onSelectCampaign={setSelectedCampaignId}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            priorityFilter={priorityFilter}
            onPriorityFilterChange={setPriorityFilter}
            onSelectLead={(lead) => setSelectedLead(lead)}
            onTriggerResearch={async (leadId) => {
              await api.triggerResearch(leadId);
              loadData();
            }}
            onTriggerQualify={async (leadId) => {
              await api.qualifyLead(leadId);
              loadData();
            }}
            onTriggerOutreach={async (leadId) => {
              await api.generateOutreach(leadId);
              loadData();
            }}
          />
        </div>

      </main>

      {/* CSV Import Modal */}
      <CSVImportModal
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
        campaigns={campaigns}
        activeCampaignId={selectedCampaignId}
        onImportComplete={loadData}
      />

      {/* Lead Intelligence Workbench Drawer */}
      <LeadDetailDrawer
        lead={selectedLead}
        onClose={() => setSelectedLead(null)}
        onRefreshLead={handleRefreshLead}
      />

    </div>
  );
}
