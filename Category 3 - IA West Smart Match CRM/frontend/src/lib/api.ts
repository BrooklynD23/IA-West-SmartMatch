export interface Specialist {
  name: string;
  board_role: string;
  metro_region: string;
  company: string;
  title: string;
  expertise_tags: string;
  initials: string;
}

export interface CppEvent {
  "Event / Program": string;
  Category: string;
  "Recurrence (typical)"?: string;
  "Host / Unit"?: string;
  "Volunteer Roles (fit)"?: string;
  "Primary Audience"?: string;
  "Public URL"?: string;
  "Point(s) of Contact (published)"?: string;
  "Contact Email / Phone (published)"?: string;
}

export interface PipelineRecord {
  event_name: string;
  speaker_name: string;
  match_score: string;
  rank: string;
  stage: string;
  stage_order: string;
}

export interface CalendarRecord {
  "IA Event Date": string;
  Region: string;
  "Nearby Universities": string;
  "Suggested Lecture Window"?: string;
  "Course Alignment"?: string;
}

export interface PocContact extends Record<string, unknown> {}

export interface RankedMatch {
  rank: number;
  name: string;
  title: string;
  company: string;
  board_role: string;
  metro_region: string;
  expertise_tags: string;
  event_id: string;
  event_name: string;
  score: number;
  match_score: number;
  total_score: number;
  factor_scores: Record<string, number>;
  weighted_factor_scores: Record<string, number>;
}

export interface MatchScore {
  speaker_name: string;
  event_name: string;
  total_score: number;
  factor_scores: Record<string, number>;
  weighted_factor_scores: Record<string, number>;
}

export interface OutreachEmailPayload {
  subject_line: string;
  greeting: string;
  body: string;
  closing: string;
  full_email: string;
}

export interface OutreachEmailResponse {
  email: string;
  email_data: OutreachEmailPayload;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        detail = payload.detail;
      }
    } catch {
      // Ignore non-JSON error bodies.
    }
    throw new Error(detail);
  }

  return (await response.json()) as T;
}

function normalizeRankedMatch(payload: Partial<RankedMatch> & Record<string, unknown>): RankedMatch {
  const factorScores = (payload.factor_scores ?? {}) as Record<string, number>;
  const weightedFactorScores = (payload.weighted_factor_scores ?? {}) as Record<string, number>;
  const rawScore =
    Number(payload.score ?? payload.match_score ?? payload.total_score ?? 0) || 0;

  return {
    rank: Number(payload.rank ?? 0) || 0,
    name: String(payload.name ?? payload.speaker_name ?? ""),
    title: String(payload.title ?? payload.speaker_title ?? ""),
    company: String(payload.company ?? payload.speaker_company ?? ""),
    board_role: String(payload.board_role ?? payload.speaker_board_role ?? ""),
    metro_region: String(payload.metro_region ?? payload.speaker_metro_region ?? ""),
    expertise_tags: String(payload.expertise_tags ?? payload.speaker_expertise_tags ?? ""),
    event_id: String(payload.event_id ?? ""),
    event_name: String(payload.event_name ?? ""),
    score: rawScore,
    match_score: rawScore,
    total_score: rawScore,
    factor_scores: factorScores,
    weighted_factor_scores: weightedFactorScores,
  };
}

export function splitTags(raw: string): string[] {
  return raw
    .split(/[;,]/)
    .map((value) => value.trim())
    .filter(Boolean);
}

export async function fetchSpecialists(): Promise<Specialist[]> {
  return requestJson<Specialist[]>("/api/data/specialists");
}

export async function fetchEvents(): Promise<CppEvent[]> {
  return requestJson<CppEvent[]>("/api/data/events");
}

export async function fetchPipeline(): Promise<PipelineRecord[]> {
  return requestJson<PipelineRecord[]>("/api/data/pipeline");
}

export async function fetchCalendar(): Promise<CalendarRecord[]> {
  return requestJson<CalendarRecord[]>("/api/data/calendar");
}

export async function fetchContacts(): Promise<PocContact[]> {
  return requestJson<PocContact[]>("/api/data/contacts");
}

export async function rankSpeakers(eventName: string, limit = 5): Promise<RankedMatch[]> {
  const payload = await requestJson<Array<Record<string, unknown>>>("/api/matching/rank", {
    method: "POST",
    body: JSON.stringify({
      event_name: eventName,
      limit,
    }),
  });

  return payload.map(normalizeRankedMatch);
}

export async function scoreSpeaker(
  speakerName: string,
  eventName: string,
): Promise<MatchScore> {
  return requestJson<MatchScore>("/api/matching/score", {
    method: "POST",
    body: JSON.stringify({
      speaker_name: speakerName,
      event_name: eventName,
    }),
  });
}

export async function generateEmail(
  speakerName: string,
  eventName: string,
): Promise<OutreachEmailResponse> {
  return requestJson<OutreachEmailResponse>("/api/outreach/email", {
    method: "POST",
    body: JSON.stringify({
      speaker_name: speakerName,
      event_name: eventName,
    }),
  });
}

export async function generateIcs(
  eventName: string,
  eventDate?: string,
  location?: string,
  description?: string,
): Promise<{ ics_content: string }> {
  return requestJson<{ ics_content: string }>("/api/outreach/ics", {
    method: "POST",
    body: JSON.stringify({
      event_name: eventName,
      event_date: eventDate,
      location,
      description,
    }),
  });
}
