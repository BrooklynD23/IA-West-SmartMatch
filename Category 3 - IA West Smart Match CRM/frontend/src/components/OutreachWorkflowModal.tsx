import { Check, Download, Loader2, Mail, X } from "lucide-react";

import { type RankedMatch, type WorkflowResponse } from "@/lib/api";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/app/components/ui/dialog";

interface OutreachWorkflowModalProps {
  volunteer: RankedMatch;
  result: WorkflowResponse | null;
  loading: boolean;
  error: string | null;
  onClose: () => void;
}

const STEPS: { key: keyof WorkflowResponse["steps"]; label: string }[] = [
  { key: "email", label: "Generating outreach email..." },
  { key: "ics", label: "Creating calendar invite..." },
  { key: "pipeline", label: "Updating pipeline status..." },
];

export function OutreachWorkflowModal({
  volunteer,
  result,
  loading,
  error,
  onClose,
}: OutreachWorkflowModalProps) {
  const handleDownloadIcs = () => {
    if (!result) return;
    const blob = new Blob([result.ics_content], { type: "text/calendar" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${volunteer.name.replace(/\s+/g, "-")}-invite.ics`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-h-[90vh] max-w-3xl overflow-y-auto rounded-xl p-8 sm:max-w-3xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Mail className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <DialogTitle id="workflow-modal-title" className="text-2xl font-semibold text-gray-900">
                Outreach Workflow
              </DialogTitle>
              <DialogDescription className="mt-1 text-sm text-gray-600">
                Review generated outreach steps for {volunteer.name} before you dispatch follow-up.
              </DialogDescription>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close workflow modal"
          >
            Close
          </button>
        </div>

        {/* Error banner */}
        {error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 mb-4">
            {error}
          </div>
        ) : null}

        {/* 3-step checklist */}
        <div className="space-y-3 mb-6">
          {STEPS.map((step) => {
            if (loading) {
              return (
                <div key={step.key} className="flex items-center gap-3 text-gray-700">
                  <Loader2 className="w-5 h-5 animate-spin text-purple-600 flex-shrink-0" />
                  <span>{step.label}</span>
                </div>
              );
            }

            if (!result) return null;

            const stepResult = result.steps[step.key];
            const isOk = stepResult.status === "ok";

            return (
              <div key={step.key} className="flex items-start gap-3">
                {isOk ? (
                  <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                ) : (
                  <X className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                )}
                <div>
                  <span className={isOk ? "text-gray-700" : "text-gray-700"}>
                    {step.label}
                  </span>
                  {!isOk && stepResult.error ? (
                    <p className="text-sm text-red-600 mt-1">{stepResult.error}</p>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>

        {/* Email content (shown after success) */}
        {result ? (
          <div className="space-y-4">
            {result.steps.email.status === "ok" ? (
              <>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Subject</p>
                  <div className="rounded-lg bg-gray-50 px-4 py-3 text-gray-900">
                    {result.email_data.subject_line}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Message</p>
                  <div className="rounded-lg bg-gray-50 px-4 py-3 text-gray-900 whitespace-pre-wrap min-h-[240px]">
                    {result.email}
                  </div>
                </div>
              </>
            ) : null}

            {/* ICS download button */}
            {result.steps.ics.status === "ok" ? (
              <button
                onClick={handleDownloadIcs}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Download className="w-4 h-4" /> Download Calendar Invite
              </button>
            ) : null}

            {/* Pipeline status badge */}
            {result.pipeline_updated ? (
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                <Check className="w-4 h-4" />
                Pipeline Updated: Contacted
              </div>
            ) : result.steps.pipeline.status === "error" ? (
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-red-100 text-red-800 rounded-full text-sm font-medium">
                <X className="w-4 h-4" />
                Pipeline Update Failed
              </div>
            ) : null}
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
