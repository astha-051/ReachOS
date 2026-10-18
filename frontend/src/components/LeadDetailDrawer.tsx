import React, { useState } from "react";
import { 
  X, Sparkles, ExternalLink, ShieldCheck, Flame, CheckCircle2, 
  Send, Edit3, AlertCircle, MessageSquare, ThumbsUp, ThumbsDown, 
  RefreshCw, FileText, ArrowRight, CornerDownRight, Check, Database, Search
} from "lucide-react";
import { LeadDetail, api } from "../lib/api";

interface LeadDetailDrawerProps {
  lead: LeadDetail | null;
  onClose: () => void;
  onRefreshLead: (leadId: string) => void;
}

export const LeadDetailDrawer: React.FC<LeadDetailDrawerProps> = ({
  lead,
  onClose,
  onRefreshLead
}) => {
  const [activeTab, setActiveTab] = useState<"research" | "qualification" | "outreach" | "reply">("research");
  
  // Loading states
  const [isResearching, setIsResearching] = useState(false);
  const [isQualifying, setIsQualifying] = useState(false);
  const [isDrafting, setIsDrafting] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isAnalyzingReply, setIsAnalyzingReply] = useState(false);

  // Edit draft states
  const [isEditingDraft, setIsEditingDraft] = useState(false);
  const [editSubject, setEditSubject] = useState("");
  const [editBody, setEditBody] = useState("");

  // Reply text input state
  const [replyText, setReplyText] = useState("");

  if (!lead) return null;

  const report = lead.research_report;
  const qual = lead.qualification;
  const draft = lead.outreach_draft;
  const replies = lead.replies || [];

  const handleRunResearch = async () => {
    setIsResearching(true);
    try {
      await api.triggerResearch(lead.id, true);
      onRefreshLead(lead.id);
    } catch (err: any) {
      alert("Research failed: " + err.message);
    } finally {
      setIsResearching(false);
    }
  };

  const handleRunQualify = async () => {
    setIsQualifying(true);
    try {
      await api.qualifyLead(lead.id);
      onRefreshLead(lead.id);
      setActiveTab("qualification");
    } catch (err: any) {
      alert("Qualification failed: " + err.message);
    } finally {
      setIsQualifying(false);
    }
  };

  const handleGenerateOutreach = async () => {
    setIsDrafting(true);
    try {
      await api.generateOutreach(lead.id);
      onRefreshLead(lead.id);
      setActiveTab("outreach");
    } catch (err: any) {
      alert("Outreach generation failed: " + err.message);
    } finally {
      setIsDrafting(false);
    }
  };

  const handleApproveDraft = async (action: "APPROVE" | "REJECT") => {
    if (!draft) return;
    try {
      await api.approveOutreach(
        draft.id,
        action,
        isEditingDraft ? editSubject : undefined,
        isEditingDraft ? editBody : undefined
      );
      setIsEditingDraft(false);
      onRefreshLead(lead.id);
    } catch (err: any) {
      alert("Approval action failed: " + err.message);
    }
  };

  const handleSendEmail = async () => {
    if (!draft) return;
    setIsSending(true);
    try {
      await api.sendOutreach(draft.id);
      onRefreshLead(lead.id);
    } catch (err: any) {
      alert("Sending email failed: " + err.message);
    } finally {
      setIsSending(false);
    }
  };

  const handleAnalyzeReply = async () => {
    if (!replyText.trim()) return;
    setIsAnalyzingReply(true);
    try {
      await api.analyzeReply(lead.id, replyText);
      setReplyText("");
      onRefreshLead(lead.id);
    } catch (err: any) {
      alert("Reply analysis failed: " + err.message);
    } finally {
      setIsAnalyzingReply(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/70 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-3xl glass-panel bg-gray-950 border-l border-gray-800 h-full flex flex-col shadow-2xl">
        
        {/* Drawer Header */}
        <div className="p-6 border-b border-gray-800 flex items-start justify-between bg-gray-900/60">
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <h2 className="text-xl font-bold text-white">{lead.name}</h2>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-gray-800 text-gray-300 font-medium">
                {lead.job_title || "Role Unspecified"}
              </span>
            </div>

            <div className="flex items-center space-x-4 text-xs text-gray-400">
              <span className="font-semibold text-cyan-400">{lead.company_name}</span>
              <span>•</span>
              <span className="font-mono text-gray-400">{lead.email}</span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white p-2 rounded-lg hover:bg-gray-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-800 bg-gray-950 px-6">
          <button
            onClick={() => setActiveTab("research")}
            className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center space-x-2 transition ${
              activeTab === "research"
                ? "border-cyan-400 text-cyan-400"
                : "border-transparent text-gray-400 hover:text-gray-200"
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>1. Tavily Research</span>
          </button>

          <button
            onClick={() => setActiveTab("qualification")}
            className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center space-x-2 transition ${
              activeTab === "qualification"
                ? "border-purple-400 text-purple-400"
                : "border-transparent text-gray-400 hover:text-gray-200"
            }`}
          >
            <Flame className="w-4 h-4" />
            <span>2. Nemotron Scorecard</span>
          </button>

          <button
            onClick={() => setActiveTab("outreach")}
            className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center space-x-2 transition ${
              activeTab === "outreach"
                ? "border-emerald-400 text-emerald-400"
                : "border-transparent text-gray-400 hover:text-gray-200"
            }`}
          >
            <Edit3 className="w-4 h-4" />
            <span>3. Email Outreach</span>
          </button>

          <button
            onClick={() => setActiveTab("reply")}
            className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center space-x-2 transition ${
              activeTab === "reply"
                ? "border-rose-400 text-rose-400"
                : "border-transparent text-gray-400 hover:text-gray-200"
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>4. Reply Intelligence</span>
          </button>
        </div>

        {/* Drawer Body Content */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">

          {/* TAB 1: TAVILY RESEARCH */}
          {activeTab === "research" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300">
                    Verified Tavily Web Evidence
                  </h3>
                  {/* TASK 9: Model Transparency */}
                  <span className="text-[10px] text-purple-400 font-mono block mt-0.5">
                    Engine: Tavily Web Search API + NVIDIA Nemotron 550B (Deep Model)
                  </span>
                </div>

                <button
                  onClick={handleRunResearch}
                  disabled={isResearching}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium disabled:opacity-50"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{isResearching ? "Gathering Web Sources..." : "Refresh Tavily Research"}</span>
                </button>
              </div>

              {report ? (
                <div className="space-y-4">
                  {/* Summary Card */}
                  <div className="p-4 rounded-xl bg-gray-900 border border-gray-800">
                    <span className="text-xs font-semibold text-cyan-400 block mb-1">
                      {lead.company_name} Executive Overview
                    </span>
                    <p className="text-xs text-gray-300 leading-relaxed">{report.summary}</p>
                  </div>

                  {/* Signals & Pain Points */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20">
                      <span className="text-xs font-semibold text-emerald-400 block mb-2">Verified Recent Signals</span>
                      <ul className="space-y-1 text-xs text-emerald-200">
                        {report.recent_signals?.length ? (
                          report.recent_signals.map((sig, i) => (
                            <li key={i} className="flex items-start space-x-1.5">
                              <span className="text-emerald-400">•</span>
                              <span>{sig}</span>
                            </li>
                          ))
                        ) : (
                          <li className="text-gray-500 italic">No verified recent signals found.</li>
                        )}
                      </ul>
                    </div>

                    <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/20">
                      <span className="text-xs font-semibold text-amber-400 block mb-2">Detected Business Pain Points</span>
                      <ul className="space-y-1 text-xs text-amber-200">
                        {report.pain_points?.length ? (
                          report.pain_points.map((pain, i) => (
                            <li key={i} className="flex items-start space-x-1.5">
                              <span className="text-amber-400">•</span>
                              <span>{pain}</span>
                            </li>
                          ))
                        ) : (
                          <li className="text-gray-500 italic">No pain points detected.</li>
                        )}
                      </ul>
                    </div>
                  </div>

                  {/* Web Sources Citations */}
                  <div>
                    <span className="text-xs font-semibold text-gray-400 block mb-2">Verified Relevance Web Sources</span>
                    <div className="space-y-2">
                      {report.sources?.map((src) => (
                        <div key={src.id} className="p-3 rounded-lg bg-gray-900/60 border border-gray-800 flex justify-between items-start">
                          <div>
                            <a
                              href={src.url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-xs font-bold text-indigo-400 hover:underline flex items-center space-x-1 mb-1"
                            >
                              <span>{src.title}</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                            <p className="text-[11px] text-gray-400 line-clamp-2">{src.snippet}</p>
                          </div>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 whitespace-nowrap ml-2">
                            Relevance: {Math.round((src.relevance_score || 1.0) * 100)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center border border-dashed border-gray-800 rounded-xl bg-gray-900/30">
                  <Sparkles className="w-8 h-8 text-indigo-400 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-300">No Tavily Web Research Gathered Yet for {lead.company_name}</p>
                  <button
                    onClick={handleRunResearch}
                    disabled={isResearching}
                    className="mt-3 inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20"
                  >
                    <span>Run Grounded Web Research</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: NEMOTRON QUALIFICATION SCORECARD */}
          {activeTab === "qualification" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300">
                    NVIDIA Nemotron Qualification Scorecard
                  </h3>
                  {/* TASK 9: Model Transparency */}
                  <span className="text-[10px] text-purple-400 font-mono block mt-0.5">
                    Engine: NVIDIA Nemotron 120B (Reasoning Model via Nebius Token Factory)
                  </span>
                </div>

                <button
                  onClick={handleRunQualify}
                  disabled={isQualifying}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-medium disabled:opacity-50"
                >
                  <Flame className="w-3.5 h-3.5" />
                  <span>{isQualifying ? "Scoring Lead..." : "Re-Qualify Lead"}</span>
                </button>
              </div>

              {qual ? (
                <div className="space-y-6">
                  {/* Score Gauge Header */}
                  <div className="p-6 rounded-2xl bg-gradient-to-r from-purple-950/40 via-gray-900 to-indigo-950/40 border border-purple-500/30 flex items-center justify-between">
                    <div>
                      <span className="text-xs uppercase tracking-wider font-semibold text-purple-400 block mb-1">
                        Dynamic Lead Qualification Score
                      </span>
                      <div className="flex items-baseline space-x-2">
                        <span className="text-4xl font-black text-white">{qual.score}</span>
                        <span className="text-gray-400 font-medium text-sm">/ 100</span>
                      </div>
                      <p className="text-xs text-gray-300 mt-2">{qual.reason}</p>
                    </div>

                    <div className="text-right">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                        qual.priority === "HIGH"
                          ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                          : qual.priority === "MEDIUM"
                          ? "bg-blue-500/20 text-blue-300 border border-blue-500/40"
                          : "bg-gray-800 text-gray-400"
                      }`}>
                        {qual.priority} PRIORITY
                      </span>
                    </div>
                  </div>

                  {/* 3-Part Breakdown: Fit, Intent, Timing */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 text-center">
                      <span className="text-xs font-medium text-gray-400 block mb-1">Target Fit</span>
                      <span className="text-xl font-bold text-white">{qual.fit_score}%</span>
                      <div className="w-full bg-gray-800 h-1.5 rounded-full mt-2 overflow-hidden">
                        <div className="bg-indigo-500 h-full" style={{ width: `${qual.fit_score}%` }} />
                      </div>
                    </div>

                    <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 text-center">
                      <span className="text-xs font-medium text-gray-400 block mb-1">Buying Intent</span>
                      <span className="text-xl font-bold text-white">{qual.intent_score}%</span>
                      <div className="w-full bg-gray-800 h-1.5 rounded-full mt-2 overflow-hidden">
                        <div className="bg-cyan-500 h-full" style={{ width: `${qual.intent_score}%` }} />
                      </div>
                    </div>

                    <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 text-center">
                      <span className="text-xs font-medium text-gray-400 block mb-1">Growth Timing</span>
                      <span className="text-xl font-bold text-white">{qual.timing_score}%</span>
                      <div className="w-full bg-gray-800 h-1.5 rounded-full mt-2 overflow-hidden">
                        <div className="bg-emerald-500 h-full" style={{ width: `${qual.timing_score}%` }} />
                      </div>
                    </div>
                  </div>

                  {/* Bulleted Evidence Justifications */}
                  <div className="p-4 rounded-xl bg-gray-900/60 border border-gray-800">
                    <span className="text-xs font-bold text-gray-300 block mb-3">Evidence Justification Log</span>
                    <ul className="space-y-2 text-xs text-gray-300">
                      {qual.evidence?.map((ev, i) => (
                        <li key={i} className="flex items-start space-x-2">
                          <CheckCircle2 className="w-3.5 h-3.5 text-purple-400 shrink-0 mt-0.5" />
                          <span>{ev}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center border border-dashed border-gray-800 rounded-xl bg-gray-900/30">
                  <Flame className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-300">Lead Scorecard Not Calculated</p>
                  <button
                    onClick={handleRunQualify}
                    disabled={isQualifying}
                    className="mt-3 inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold"
                  >
                    <span>Calculate Nemotron Lead Score</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: EMAIL OUTREACH & APPROVAL WORKFLOW */}
          {activeTab === "outreach" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300">
                    Evidence-Grounded Outreach Email
                  </h3>
                  {/* TASK 9: Model Transparency */}
                  <span className="text-[10px] text-emerald-400 font-mono block mt-0.5">
                    Engine: {draft?.model_used || "NVIDIA Nemotron 120B (Reasoning Model)"}
                  </span>
                </div>

                {/* Hide generate draft if email is already SENT */}
                {draft?.status !== "SENT" && (
                  <button
                    onClick={handleGenerateOutreach}
                    disabled={isDrafting}
                    className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium disabled:opacity-50"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>{isDrafting ? "Drafting Email..." : "Generate AI Outreach"}</span>
                  </button>
                )}
              </div>

              {draft ? (
                <div className="space-y-4">
                  {/* Personalization Grounding Points */}
                  <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/20 text-xs">
                    <span className="font-semibold text-emerald-400 block mb-1">Grounded Evidence Personalization</span>
                    <ul className="space-y-1 text-emerald-300">
                      {draft.personalization_points?.map((pt, i) => (
                        <li key={i} className="flex items-center space-x-1">
                          <span>•</span>
                          <span>{pt}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Email Draft Content Box */}
                  <div className="p-5 rounded-2xl bg-gray-900 border border-gray-800 space-y-3">
                    <div>
                      <label className="text-[11px] uppercase tracking-wider font-semibold text-gray-400 block mb-1">
                        Subject Line
                      </label>
                      {isEditingDraft ? (
                        <input
                          type="text"
                          value={editSubject}
                          onChange={(e) => setEditSubject(e.target.value)}
                          className="w-full bg-gray-950 border border-indigo-500 rounded-lg px-3 py-2 text-xs text-white"
                        />
                      ) : (
                        <div className="font-bold text-white text-sm bg-gray-950 p-2.5 rounded-lg border border-gray-800">
                          {draft.subject}
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="text-[11px] uppercase tracking-wider font-semibold text-gray-400 block mb-1">
                        Email Body Text
                      </label>
                      {isEditingDraft ? (
                        <textarea
                          rows={6}
                          value={editBody}
                          onChange={(e) => setEditBody(e.target.value)}
                          className="w-full bg-gray-950 border border-indigo-500 rounded-lg p-3 text-xs text-white leading-relaxed"
                        />
                      ) : (
                        <div className="text-xs text-gray-200 bg-gray-950 p-3.5 rounded-lg border border-gray-800 whitespace-pre-wrap leading-relaxed">
                          {draft.body}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* TASK 7: EMAIL STATE MACHINE CONTROLS */}
                  <div className="p-4 rounded-xl glass-panel bg-gray-900 border border-gray-800 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-semibold text-gray-400">Approval State:</span>
                      <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                        draft.status === "SENT"
                          ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                          : draft.status === "APPROVED"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : draft.status === "REJECTED"
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                          : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                      }`}>
                        {draft.status}
                      </span>
                    </div>

                    {/* STATE CONTROLS */}
                    {draft.status === "SENT" ? (
                      /* IF SENT: HIDE APPROVE BUTTON and show SENT confirmation badge */
                      <div className="flex items-center space-x-2 text-xs text-cyan-400 font-semibold bg-cyan-950/40 px-3 py-1.5 rounded-lg border border-cyan-500/30">
                        <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                        <span>Email Sent via Configured Provider</span>
                      </div>
                    ) : draft.status === "APPROVED" ? (
                      /* IF APPROVED: SHOW SEND BUTTON */
                      <div className="flex items-center space-x-2">
                        {!isEditingDraft ? (
                          <button
                            onClick={() => {
                              setIsEditingDraft(true);
                              setEditSubject(draft.subject);
                              setEditBody(draft.body);
                            }}
                            className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium"
                          >
                            Edit Text
                          </button>
                        ) : (
                          <button
                            onClick={() => setIsEditingDraft(false)}
                            className="px-3 py-1.5 rounded-lg bg-gray-800 text-gray-300 text-xs"
                          >
                            Cancel Edit
                          </button>
                        )}
                        <button
                          onClick={handleSendEmail}
                          disabled={isSending}
                          className="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold flex items-center space-x-1 shadow-lg shadow-cyan-600/20"
                        >
                          <Send className="w-3.5 h-3.5" />
                          <span>{isSending ? "Sending Email..." : "Send Email Now"}</span>
                        </button>
                      </div>
                    ) : (
                      /* IF PENDING_APPROVAL / DRAFT: SHOW APPROVE / EDIT / REJECT BUTTONS */
                      <div className="flex items-center space-x-2">
                        {!isEditingDraft ? (
                          <button
                            onClick={() => {
                              setIsEditingDraft(true);
                              setEditSubject(draft.subject);
                              setEditBody(draft.body);
                            }}
                            className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium"
                          >
                            Edit Text
                          </button>
                        ) : (
                          <button
                            onClick={() => setIsEditingDraft(false)}
                            className="px-3 py-1.5 rounded-lg bg-gray-800 text-gray-300 text-xs"
                          >
                            Cancel Edit
                          </button>
                        )}

                        <button
                          onClick={() => handleApproveDraft("REJECT")}
                          className="px-3 py-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-500/30 text-xs font-medium"
                        >
                          Reject
                        </button>

                        <button
                          onClick={() => handleApproveDraft("APPROVE")}
                          className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20"
                        >
                          Approve Email
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center border border-dashed border-gray-800 rounded-xl bg-gray-900/30">
                  <Edit3 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-300">Outreach Email Draft Not Generated</p>
                  <button
                    onClick={handleGenerateOutreach}
                    disabled={isDrafting}
                    className="mt-3 inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                  >
                    <span>Generate Evidence-Grounded Email</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: REPLY INTELLIGENCE */}
          {activeTab === "reply" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300">
                    Prospect Reply Intelligence & Sentiment Analysis
                  </h3>
                  {/* TASK 9: Model Transparency */}
                  <span className="text-[10px] text-rose-400 font-mono block mt-0.5">
                    Engine: NVIDIA Nemotron 30B (Fast Model via Nebius Token Factory)
                  </span>
                </div>
              </div>

              {/* Reply Input Simulator */}
              <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 space-y-3">
                <label className="text-xs font-semibold text-gray-300 block">
                  Simulate Prospect Response Text
                </label>
                <textarea
                  rows={3}
                  placeholder="Paste prospect reply here e.g. 'Hi, I saw your email and would love to schedule a demo to discuss pricing...'"
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-rose-500"
                />

                <div className="flex justify-end">
                  <button
                    onClick={handleAnalyzeReply}
                    disabled={isAnalyzingReply || !replyText.trim()}
                    className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-rose-600/20"
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                    <span>{isAnalyzingReply ? "Analyzing Intent..." : "Analyze Reply Intent"}</span>
                  </button>
                </div>
              </div>

              {/* Analyzed Replies History */}
              <div className="space-y-3">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block">
                  Persisted Reply Classifications
                </span>

                {replies.length === 0 ? (
                  <p className="text-xs text-gray-500 text-center py-6">No prospect responses logged yet.</p>
                ) : (
                  replies.map((rep) => (
                    <div key={rep.id} className="p-4 rounded-xl bg-gray-900 border border-gray-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-rose-400 uppercase tracking-wider">
                            Classification: {rep.classification}
                          </span>
                          {rep.intent && (
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gray-800 text-gray-300">
                              intent: {rep.intent}
                            </span>
                          )}
                          {rep.sentiment && (
                            <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                              rep.sentiment === "positive" ? "bg-emerald-500/20 text-emerald-300" : "bg-gray-800 text-gray-300"
                            }`}>
                              sentiment: {rep.sentiment}
                            </span>
                          )}
                        </div>

                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                          Recommended: {rep.recommended_action}
                        </span>
                      </div>

                      <p className="text-xs text-gray-300 italic bg-gray-950 p-2.5 rounded-lg border border-gray-800">
                        "{rep.body}"
                      </p>

                      <div className="text-xs text-gray-400 space-y-1">
                        <div>
                          <span className="font-semibold text-gray-300">AI Intent Summary: </span>
                          <span>{rep.summary || rep.detected_intent}</span>
                        </div>
                        <p className="text-gray-400">{rep.reason}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};
