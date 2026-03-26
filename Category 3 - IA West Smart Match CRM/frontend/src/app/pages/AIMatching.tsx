import { useEffect, useState } from "react";
import { Calendar, Mail, MapPin, Sparkles, Target } from "lucide-react";

import {
  fetchEvents,
  generateEmail,
  rankSpeakers,
  splitTags,
  type CppEvent,
  type OutreachEmailResponse,
  type RankedMatch,
} from "@/lib/api";

const factorLabels: Record<string, string> = {
  topic_relevance: "Topic Relevance",
  role_fit: "Role Fit",
  geographic_proximity: "Geographic Proximity",
  calendar_fit: "Calendar Fit",
  historical_conversion: "Historical Conversion",
  student_interest: "Student Interest",
};

function ProgressBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div className={`h-2 rounded-full ${color}`} style={{ width: `${value}%` }} />
    </div>
  );
}

function buildMatchReasoning(match: RankedMatch): string {
  const strongestFactors = Object.entries(match.factor_scores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 2)
    .map(([key]) => factorLabels[key] || key);
  if (strongestFactors.length === 0) {
    return "This ranking is ready once factor data is available.";
  }
  return `${match.name} stands out on ${strongestFactors.join(" and ")} for ${match.event_name}.`;
}

export function AIMatching() {
  const [events, setEvents] = useState<CppEvent[]>([]);
  const [selectedEventName, setSelectedEventName] = useState("");
  const [matches, setMatches] = useState<RankedMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [ranking, setRanking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [selectedVolunteer, setSelectedVolunteer] = useState<RankedMatch | null>(null);
  const [emailResult, setEmailResult] = useState<OutreachEmailResponse | null>(null);
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    fetchEvents()
      .then((data) => {
        if (!active) {
          return;
        }
        setEvents(data);
        setSelectedEventName(data[0]?.["Event / Program"] ?? "");
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to load events.");
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedEventName) {
      return;
    }

    let active = true;
    setRanking(true);
    setError(null);

    rankSpeakers(selectedEventName, 5)
      .then((data) => {
        if (active) {
          setMatches(data);
        }
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to rank speakers.");
          setMatches([]);
        }
      })
      .finally(() => {
        if (active) {
          setRanking(false);
        }
      });

    return () => {
      active = false;
    };
  }, [selectedEventName]);

  const selectedEvent =
    events.find((event) => event["Event / Program"] === selectedEventName) ?? null;

  const openEmailModal = async (match: RankedMatch) => {
    if (!selectedEventName) {
      return;
    }
    setSelectedVolunteer(match);
    setShowEmailModal(true);
    setEmailLoading(true);
    setEmailError(null);
    setEmailResult(null);

    try {
      const result = await generateEmail(match.name, selectedEventName);
      setEmailResult(result);
    } catch (err: unknown) {
      setEmailError(err instanceof Error ? err.message : "Failed to generate email.");
    } finally {
      setEmailLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-500 rounded-lg flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-3xl font-semibold text-gray-900">AI Matching Engine</h1>
        </div>
        <p className="text-gray-600">
          Rank specialists against live CPP opportunities and generate outreach drafts.
        </p>
      </div>

      <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
        <label className="block text-sm font-medium text-gray-700 mb-2">Select event</label>
        <select
          value={selectedEventName}
          onChange={(event) => setSelectedEventName(event.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {events.map((event) => (
            <option key={event["Event / Program"]} value={event["Event / Program"]}>
              {event["Event / Program"]}
            </option>
          ))}
        </select>
      </div>

      {selectedEvent ? (
        <div className="bg-gradient-to-r from-blue-50 to-blue-50 rounded-xl p-6 border border-blue-200">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {selectedEvent["Event / Program"]}
              </h2>
              <p className="text-gray-700 mb-4">
                {selectedEvent["Primary Audience"] || "Audience details not provided"}
              </p>
            </div>
            <span className="px-3 py-1 bg-blue-600 text-white text-sm rounded-full font-medium">
              Selected
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="flex items-center gap-2 text-sm">
              <Target className="w-4 h-4 text-blue-600" />
              <span className="text-gray-700">
                <span className="font-medium">Host:</span>{" "}
                {selectedEvent["Host / Unit"] || "CPP partner"}
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Calendar className="w-4 h-4 text-blue-600" />
              <span className="text-gray-700">
                <span className="font-medium">Cadence:</span>{" "}
                {selectedEvent["Recurrence (typical)"] || "TBD"}
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <MapPin className="w-4 h-4 text-blue-600" />
              <span className="text-gray-700">
                <span className="font-medium">Contact:</span>{" "}
                {selectedEvent["Point(s) of Contact (published)"] || "Not listed"}
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-gray-700">
                <span className="font-medium">Role:</span>{" "}
                {splitTags(selectedEvent["Volunteer Roles (fit)"] || "")[0] || "Volunteer"}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 mt-4">
            {[selectedEvent.Category, ...splitTags(selectedEvent["Volunteer Roles (fit)"] || "").slice(0, 3)]
              .filter(Boolean)
              .map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded-full"
                >
                  {tag}
                </span>
              ))}
          </div>
        </div>
      ) : null}

      {error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700 text-center">
          {error}
        </div>
      ) : null}

      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Top Recommended Volunteers</h2>
          </div>
          <span className="text-sm text-gray-600">
            {ranking ? "Refreshing rankings..." : "Sorted by match score"}
          </span>
        </div>

        <div className="space-y-6">
          {loading || ranking ? (
            <div className="bg-white rounded-xl p-10 border border-gray-200 shadow-sm text-center text-gray-600">
              Loading ranking results...
            </div>
          ) : matches.length === 0 ? (
            <div className="bg-white rounded-xl p-10 border border-gray-200 shadow-sm text-center text-gray-600">
              No match results are available for the selected event yet.
            </div>
          ) : (
            matches.map((volunteer) => (
              <div
                key={`${volunteer.event_name}-${volunteer.name}`}
                className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start gap-6 mb-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-400 to-blue-400 rounded-full flex items-center justify-center text-white text-2xl font-semibold flex-shrink-0">
                    {volunteer.name
                      .split(" ")
                      .map((part) => part[0])
                      .join("")
                      .slice(0, 3)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900">{volunteer.name}</h3>
                        <p className="text-gray-600">
                          {volunteer.title || "IA West volunteer"} at {volunteer.company || "IA West"}
                        </p>
                        <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                          <MapPin className="w-4 h-4" />
                          {volunteer.metro_region || "Region not listed"}
                        </div>
                      </div>
                      <div className="text-center flex-shrink-0">
                        <div className="w-20 h-20 rounded-full border-4 border-blue-600 flex items-center justify-center">
                          <div>
                            <p className="text-2xl font-bold text-blue-600">
                              {(volunteer.score * 100).toFixed(0)}
                            </p>
                            <p className="text-xs text-gray-600">score</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-blue-50 rounded-lg p-4 mb-4">
                      <p className="text-sm text-gray-700 italic">{buildMatchReasoning(volunteer)}</p>
                    </div>

                    <div className="space-y-3">
                      <h4 className="font-medium text-gray-900">Match Score Breakdown:</h4>

                      {Object.entries(volunteer.factor_scores).map(([key, rawValue], index) => {
                        const value = Math.round(rawValue * 100);
                        const colors = [
                          "bg-blue-600",
                          "bg-blue-600",
                          "bg-green-600",
                          "bg-orange-600",
                          "bg-pink-600",
                          "bg-indigo-600",
                        ];

                        return (
                          <div key={key}>
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm text-gray-700">
                                {factorLabels[key] || key}
                              </span>
                              <span className="text-sm font-medium text-gray-900">{value}%</span>
                            </div>
                            <ProgressBar value={value} color={colors[index % colors.length]} />
                          </div>
                        );
                      })}
                    </div>

                    <button
                      onClick={() => void openEmailModal(volunteer)}
                      className="mt-6 w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center gap-2"
                    >
                      <Mail className="w-5 h-5" />
                      Generate Outreach Email
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showEmailModal && selectedVolunteer ? (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setShowEmailModal(false)}
          onKeyDown={(event) => { if (event.key === "Escape") setShowEmailModal(false); }}
          role="presentation"
        >
          <div
            className="bg-white rounded-xl p-8 max-w-3xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(event) => event.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="email-modal-title"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Mail className="w-5 h-5 text-blue-600" />
                </div>
                <h2 id="email-modal-title" className="text-2xl font-semibold text-gray-900">
                  AI-Generated Outreach Email
                </h2>
              </div>
              <button
                onClick={() => setShowEmailModal(false)}
                className="text-gray-400 hover:text-gray-600"
                aria-label="Close email modal"
              >
                Close
              </button>
            </div>

            {emailLoading ? (
              <div className="rounded-lg border border-gray-200 p-8 text-center text-gray-600">
                Generating outreach for {selectedVolunteer.name}...
              </div>
            ) : emailError ? (
              <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-700">
                {emailError}
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Subject</p>
                  <div className="rounded-lg bg-gray-50 px-4 py-3 text-gray-900">
                    {emailResult?.email_data.subject_line || "No subject returned"}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Message</p>
                  <div className="rounded-lg bg-gray-50 px-4 py-3 text-gray-900 whitespace-pre-wrap min-h-[320px]">
                    {emailResult?.email || "No email returned"}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
