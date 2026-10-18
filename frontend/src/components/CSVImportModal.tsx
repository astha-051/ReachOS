import React, { useState } from "react";
import { UploadCloud, CheckCircle, AlertOctagon, Copy, X, FileText, ArrowRight } from "lucide-react";
import { api, CSVImportPreview, Campaign } from "../lib/api";

interface CSVImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  campaigns: Campaign[];
  activeCampaignId?: string;
  onImportComplete: () => void;
}

export const CSVImportModal: React.FC<CSVImportModalProps> = ({
  isOpen,
  onClose,
  campaigns,
  activeCampaignId,
  onImportComplete
}) => {
  const [selectedCampaignId, setSelectedCampaignId] = useState<string>(activeCampaignId || (campaigns[0]?.id || ""));
  const [newCampaignName, setNewCampaignName] = useState("");
  const [isCreatingCampaign, setIsCreatingCampaign] = useState(false);
  
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<CSVImportPreview | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;
    setFile(uploadedFile);
    setError(null);
    setIsUploading(true);

    try {
      let targetId = selectedCampaignId;
      if (isCreatingCampaign && newCampaignName.trim()) {
        const newCamp = await api.createCampaign({ name: newCampaignName });
        targetId = newCamp.id;
        setSelectedCampaignId(newCamp.id);
        setIsCreatingCampaign(false);
      } else if (!targetId && campaigns.length > 0) {
        targetId = campaigns[0].id;
        setSelectedCampaignId(targetId);
      }

      if (!targetId) {
        throw new Error("Please select or create a campaign first.");
      }

      const previewData = await api.previewCSV(targetId, uploadedFile);
      setPreview(previewData);
    } catch (err: any) {
      setError(err.message || "Failed to parse CSV preview");
    } finally {
      setIsUploading(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!file || !selectedCampaignId) return;
    setIsImporting(true);
    setError(null);

    try {
      await api.importCSV(selectedCampaignId, file);
      onImportComplete();
      onClose();
    } catch (err: any) {
      setError(err.message || "Import failed");
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="w-full max-w-2xl glass-panel bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <UploadCloud className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-white">Import Sales Leads CSV</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-gray-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          
          {/* Campaign Selector */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
              Select Target Campaign
            </label>

            {!isCreatingCampaign ? (
              <div className="flex items-center space-x-2">
                <select
                  value={selectedCampaignId}
                  onChange={(e) => setSelectedCampaignId(e.target.value)}
                  className="flex-1 bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  {campaigns.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.total_leads} leads)
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={() => setIsCreatingCampaign(true)}
                  className="px-3 py-2 text-xs font-medium rounded-lg bg-gray-800 text-gray-200 hover:bg-gray-700 whitespace-nowrap"
                >
                  + New Campaign
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="Enter Campaign Name..."
                  value={newCampaignName}
                  onChange={(e) => setNewCampaignName(e.target.value)}
                  className="flex-1 bg-gray-950 border border-indigo-500/50 rounded-lg px-3 py-2 text-sm text-white focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => setIsCreatingCampaign(false)}
                  className="px-3 py-2 text-xs font-medium rounded-lg bg-gray-800 text-gray-300"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>

          {/* File Upload Box */}
          {!preview ? (
            <div className="border-2 border-dashed border-gray-800 hover:border-indigo-500/50 rounded-xl p-8 text-center transition bg-gray-950/40">
              <UploadCloud className="w-10 h-10 mx-auto text-indigo-400 mb-3" />
              <p className="text-sm font-medium text-gray-200 mb-1">
                Click to upload or drag & drop CSV file
              </p>
              <p className="text-xs text-gray-500 mb-4">
                Supports headers: Full Name, Email Address, Company Name, Website, Job Title
              </p>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
                id="csv-file-input"
              />
              <label
                htmlFor="csv-file-input"
                className="inline-flex items-center px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white cursor-pointer shadow-lg shadow-indigo-600/20"
              >
                {isUploading ? "Analyzing CSV Headers..." : "Select CSV File"}
              </label>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Validation Summary Badges */}
              <div className="grid grid-cols-4 gap-3 text-center">
                <div className="p-3 rounded-lg bg-gray-950 border border-gray-800">
                  <span className="text-xs text-gray-400 block">Total Rows</span>
                  <span className="text-lg font-bold text-white">{preview.total_rows}</span>
                </div>
                <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-500/30">
                  <span className="text-xs text-emerald-400 block flex items-center justify-center space-x-1">
                    <CheckCircle className="w-3 h-3" />
                    <span>Valid</span>
                  </span>
                  <span className="text-lg font-bold text-emerald-300">{preview.valid_count}</span>
                </div>
                <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-500/30">
                  <span className="text-xs text-amber-400 block flex items-center justify-center space-x-1">
                    <Copy className="w-3 h-3" />
                    <span>Duplicates</span>
                  </span>
                  <span className="text-lg font-bold text-amber-300">{preview.duplicate_count}</span>
                </div>
                <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-500/30">
                  <span className="text-xs text-rose-400 block flex items-center justify-center space-x-1">
                    <AlertOctagon className="w-3 h-3" />
                    <span>Invalid</span>
                  </span>
                  <span className="text-lg font-bold text-rose-300">{preview.invalid_count}</span>
                </div>
              </div>

              {/* Rows Preview Table */}
              <div className="max-h-48 overflow-y-auto border border-gray-800 rounded-lg bg-gray-950">
                <table className="w-full text-left text-xs">
                  <thead className="bg-gray-900 border-b border-gray-800 text-gray-400 uppercase tracking-wider sticky top-0">
                    <tr>
                      <th className="px-3 py-2">Row</th>
                      <th className="px-3 py-2">Name</th>
                      <th className="px-3 py-2">Email</th>
                      <th className="px-3 py-2">Company</th>
                      <th className="px-3 py-2">Validation Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800 text-gray-300">
                    {preview.rows.map((row) => (
                      <tr key={row.row_index} className="hover:bg-gray-900/50">
                        <td className="px-3 py-2 text-gray-500 font-mono">#{row.row_index}</td>
                        <td className="px-3 py-2 font-medium">{row.data.name || "-"}</td>
                        <td className="px-3 py-2 font-mono text-gray-400">{row.data.email || "-"}</td>
                        <td className="px-3 py-2">{row.data.company || "-"}</td>
                        <td className="px-3 py-2">
                          {row.status === "VALID" && (
                            <span className="inline-flex items-center text-emerald-400 font-semibold text-[10px]">
                              VALID
                            </span>
                          )}
                          {row.status === "DUPLICATE" && (
                            <span className="inline-flex items-center text-amber-400 font-semibold text-[10px]">
                              DUPLICATE
                            </span>
                          )}
                          {row.status === "INVALID" && (
                            <span className="inline-flex items-center text-rose-400 font-semibold text-[10px]">
                              INVALID: {row.errors.join(", ")}
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="flex items-center justify-between pt-2">
                <button
                  type="button"
                  onClick={() => { setFile(null); setPreview(null); }}
                  className="text-xs text-gray-400 hover:text-white"
                >
                  Change File
                </button>

                <button
                  type="button"
                  onClick={handleConfirmImport}
                  disabled={isImporting || preview.valid_count === 0}
                  className="inline-flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white shadow-lg shadow-emerald-600/20"
                >
                  <span>{isImporting ? "Importing Leads..." : `Import ${preview.valid_count} Valid Leads`}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
              {error}
            </div>
          )}

        </div>

      </div>
    </div>
  );
};
