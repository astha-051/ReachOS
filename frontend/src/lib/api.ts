export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface Campaign {
  id: string;
  name: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  total_leads: number;
  validated_leads: number;
  high_priority_leads: number;
}

export interface ResearchSource {
  id: string;
  title: string;
  url: string;
  domain?: string;
  snippet?: string;
  source_type: string;
  published_date?: string;
  relevance_score?: number;
}

export interface ResearchReport {
  id: string;
  lead_id: string;
  summary?: string;
  recent_signals?: string[];
  pain_points?: string[];
  opportunities?: string[];
  research_confidence: number;
  status: string;
  sources?: ResearchSource[];
}

export interface LeadQualification {
  id: string;
  lead_id: string;
  score: number;
  priority: string;
  fit_score: number;
  intent_score: number;
  timing_score: number;
  evidence?: string[];
  reason?: string;
}

export interface OutreachDraft {
  id: string;
  lead_id: string;
  subject: string;
  body: string;
  personalization_points?: string[];
  grounding_evidence_ids?: string[];
  model_used?: string;
  confidence: number;
  status: string;
  created_at: string;
}

export interface Reply {
  id: string;
  lead_id: string;
  body: string;
  classification: string;
  intent?: string;
  sentiment?: string;
  urgency?: string;
  meeting_requested?: boolean;
  confidence: number;
  detected_intent?: string;
  recommended_action?: string;
  reason?: string;
  summary?: string;
  created_at: string;
}

export interface LeadDetail {
  id: string;
  campaign_id: string;
  name: string;
  email: string;
  company_name: string;
  website?: string;
  job_title?: string;
  industry?: string;
  validation_status: string;
  validation_errors?: string[];
  status: string;
  created_at: string;
  research_report?: ResearchReport;
  qualification?: LeadQualification;
  outreach_draft?: OutreachDraft;
  replies?: Reply[];
}

export interface CSVPreviewRow {
  row_index: number;
  data: Record<string, any>;
  status: string;
  errors: string[];
}

export interface CSVImportPreview {
  total_rows: number;
  valid_count: number;
  invalid_count: number;
  duplicate_count: number;
  rows: CSVPreviewRow[];
}

export interface DashboardStats {
  total_campaigns: number;
  total_leads: number;
  validated_leads: number;
  research_completed: number;
  high_priority_leads: number;
  medium_priority_leads: number;
  low_priority_leads: number;
  emails_approved: number;
  emails_sent: number;
  replies_received: number;
  interested_replies: number;
}

async function fetchJSON(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || `API request failed with status ${res.status}`);
  }
  return res.json();
}

export const api = {
  getStats: (): Promise<DashboardStats> => fetchJSON("/dashboard/stats"),
  
  getCampaigns: (): Promise<Campaign[]> => fetchJSON("/campaigns"),
  createCampaign: (data: { name: string; description?: string }): Promise<Campaign> =>
    fetchJSON("/campaigns", { method: "POST", body: JSON.stringify(data) }),

  previewCSV: async (campaignId: string, file: File): Promise<CSVImportPreview> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/leads/import-preview`, {
      method: "POST",
      body: formData
    });
    if (!res.ok) throw new Error("CSV preview failed");
    return res.json();
  },

  importCSV: async (campaignId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/leads/import`, {
      method: "POST",
      body: formData
    });
    if (!res.ok) throw new Error("CSV import failed");
    return res.json();
  },

  getLeads: (params: { campaign_id?: string; validation_status?: string; priority?: string; status?: string; search?: string } = {}): Promise<LeadDetail[]> => {
    const query = new URLSearchParams();
    if (params.campaign_id) query.append("campaign_id", params.campaign_id);
    if (params.validation_status) query.append("validation_status", params.validation_status);
    if (params.priority) query.append("priority", params.priority);
    if (params.status) query.append("status", params.status);
    if (params.search) query.append("search", params.search);
    return fetchJSON(`/leads?${query.toString()}`);
  },

  getLead: (leadId: string): Promise<LeadDetail> => fetchJSON(`/leads/${leadId}`),
  
  triggerResearch: (leadId: string, forceRefresh: boolean = false): Promise<ResearchReport> =>
    fetchJSON(`/leads/${leadId}/research?force_refresh=${forceRefresh}`, { method: "POST" }),

  qualifyLead: (leadId: string): Promise<LeadQualification> =>
    fetchJSON(`/leads/${leadId}/qualify`, { method: "POST" }),

  generateOutreach: (leadId: string): Promise<OutreachDraft> =>
    fetchJSON(`/leads/${leadId}/outreach`, { method: "POST" }),

  approveOutreach: (draftId: string, action: "APPROVE" | "EDIT" | "REJECT", subject?: string, body?: string): Promise<OutreachDraft> =>
    fetchJSON(`/outreach/${draftId}/approve`, {
      method: "POST",
      body: JSON.stringify({ action, subject, body })
    }),

  sendOutreach: (draftId: string) =>
    fetchJSON(`/outreach/${draftId}/send`, { method: "POST" }),

  analyzeReply: (leadId: string, replyBody: string): Promise<Reply> =>
    fetchJSON(`/leads/${leadId}/reply/analyze`, {
      method: "POST",
      body: JSON.stringify({ reply_body: replyBody })
    })
};
