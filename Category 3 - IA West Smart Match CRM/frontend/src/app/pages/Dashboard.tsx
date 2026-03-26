import { useEffect, useState } from "react";
import {
  ArrowRight,
  Briefcase,
  CalendarDays,
  Sparkles,
  TrendingUp,
  Users,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Funnel,
  FunnelChart,
  LabelList,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  fetchCalendar,
  fetchEvents,
  fetchPipeline,
  fetchSpecialists,
  rankSpeakers,
  splitTags,
  type CalendarRecord,
  type PipelineRecord,
  type RankedMatch,
  type Specialist,
} from "@/lib/api";

import { MetricCard } from "../components/MetricCard";

const funnelPalette = ["#a78bfa", "#8b5cf6", "#7c3aed", "#6d28d9", "#5b21b6"];

function monthLabel(dateString: string): string {
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) {
    return dateString;
  }
  return date.toLocaleDateString("en-US", { month: "short" });
}

function stageCounts(records: PipelineRecord[]) {
  const counts = new Map<string, { count: number; order: number }>();
  for (const record of records) {
    const stage = record.stage || "Unknown";
    const order = Number(record.stage_order) || 0;
    const current = counts.get(stage);
    counts.set(stage, {
      count: (current?.count ?? 0) + 1,
      order: current?.order ?? order,
    });
  }
  return Array.from(counts.entries())
    .sort((a, b) => a[1].order - b[1].order)
    .map(([stage, value], index) => ({
      name: stage,
      value: value.count,
      fill: funnelPalette[index % funnelPalette.length],
    }));
}

function matchVolume(records: PipelineRecord[]) {
  const counts = new Map<string, number>();
  for (const record of records) {
    counts.set(record.event_name, (counts.get(record.event_name) ?? 0) + 1);
  }
  return Array.from(counts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 7)
    .map(([event, count]) => ({
      event: event.length > 18 ? `${event.slice(0, 18)}…` : event,
      matches: count,
    }));
}

function calendarReach(records: CalendarRecord[]) {
  const byMonth = new Map<string, { windows: number; campuses: number }>();
  for (const record of records) {
    const label = monthLabel(record["IA Event Date"]);
    const campuses = splitTags(record["Nearby Universities"] || "").length;
    const current = byMonth.get(label) ?? { windows: 0, campuses: 0 };
    byMonth.set(label, {
      windows: current.windows + 1,
      campuses: current.campuses + campuses,
    });
  }
  return Array.from(byMonth.entries()).map(([month, value]) => ({
    month,
    windows: value.windows,
    campuses: value.campuses,
  }));
}

export function Dashboard() {
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [pipeline, setPipeline] = useState<PipelineRecord[]>([]);
  const [calendar, setCalendar] = useState<CalendarRecord[]>([]);
  const [eventCount, setEventCount] = useState(0);
  const [topMatches, setTopMatches] = useState<RankedMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const [specialistRows, eventRows, pipelineRows, calendarRows] = await Promise.all([
          fetchSpecialists(),
          fetchEvents(),
          fetchPipeline(),
          fetchCalendar(),
        ]);

        if (!active) {
          return;
        }

        setSpecialists(specialistRows);
        setEventCount(eventRows.length);
        setPipeline(pipelineRows);
        setCalendar(calendarRows);

        const firstEventName = eventRows[0]?.["Event / Program"];
        if (firstEventName) {
          try {
            const ranked = await rankSpeakers(firstEventName, 4);
            if (active) {
              setTopMatches(ranked);
            }
          } catch {
            if (active) {
              setTopMatches([]);
            }
          }
        }
      } catch (err: unknown) {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to load dashboard data.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      active = false;
    };
  }, []);

  const funnelData = stageCounts(pipeline);
  const eventVolume = matchVolume(pipeline);
  const reachTrend = calendarReach(calendar);
  const matchedCount = funnelData.find((stage) => stage.name === "Matched")?.value ?? 0;
  const memberInquiryCount =
    funnelData.find((stage) => stage.name === "Member Inquiry")?.value ?? 0;
  const uniqueMatchedSpeakers = new Set(pipeline.map((record) => record.speaker_name)).size;
  const utilization = specialists.length
    ? Math.round((uniqueMatchedSpeakers / specialists.length) * 100)
    : 0;
  const conversionRate = matchedCount
    ? `${((memberInquiryCount / matchedCount) * 100).toFixed(1)}%`
    : "0.0%";

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="h-10 w-48 rounded bg-gray-200 animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }, (_, index) => (
            <div
              key={index}
              className="h-36 rounded-xl border border-gray-200 bg-white shadow-sm animate-pulse"
            />
          ))}
        </div>
        <div className="h-80 rounded-xl border border-gray-200 bg-white shadow-sm animate-pulse" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Live summary of the specialist roster, active opportunities, and pipeline movement.
        </p>
      </div>

      {error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700 text-center">
          {error}
        </div>
      ) : null}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Opportunities"
          value={eventCount}
          change="Loaded from CPP events"
          changeType="neutral"
          icon={Briefcase}
          iconColor="bg-blue-100 text-blue-600"
        />
        <MetricCard
          title="Volunteer Utilization"
          value={`${utilization}%`}
          change={`${uniqueMatchedSpeakers} specialists in pipeline`}
          changeType="positive"
          icon={Users}
          iconColor="bg-green-100 text-green-600"
        />
        <MetricCard
          title="Upcoming IA Windows"
          value={calendar.length}
          change="Calendar dataset"
          changeType="neutral"
          icon={CalendarDays}
          iconColor="bg-blue-100 text-blue-600"
        />
        <MetricCard
          title="Member Inquiry Rate"
          value={conversionRate}
          change={`${memberInquiryCount} records at latest stage`}
          changeType="positive"
          icon={TrendingUp}
          iconColor="bg-orange-100 text-orange-600"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-4">Pipeline Funnel</h3>
          <ResponsiveContainer width="100%" height={300}>
            <FunnelChart>
              <Tooltip />
              <Funnel dataKey="value" data={funnelData}>
                <LabelList position="right" fill="#000" stroke="none" dataKey="name" />
              </Funnel>
            </FunnelChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-4">Match Volume by Event</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={eventVolume}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="event" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="matches" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
        <h3 className="font-semibold text-gray-900 mb-4">Calendar Reach Trend</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={reachTrend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="windows"
              stroke="#8b5cf6"
              strokeWidth={3}
              name="IA windows"
            />
            <Line
              type="monotone"
              dataKey="campuses"
              stroke="#3b82f6"
              strokeWidth={3}
              name="Nearby campuses"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">Top Recommended Matches</h3>
          </div>
          <button className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1">
            View All
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-4">
          {topMatches.length === 0 ? (
            <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center text-gray-600">
              Ranking data will appear here once the FastAPI backend is running with the matching endpoint.
            </div>
          ) : (
            topMatches.map((match) => (
              <div
                key={`${match.event_name}-${match.name}`}
                className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-blue-50 rounded-lg border border-blue-100 hover:shadow-md transition-shadow"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-gray-900">{match.name}</p>
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                      {splitTags(match.expertise_tags)[0] || match.board_role || "Specialist"}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {match.event_name} · {match.company || "IA West volunteer"}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Match Score</p>
                    <p className="text-2xl font-semibold text-blue-600">
                      {(match.score * 100).toFixed(0)}%
                    </p>
                  </div>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                    Connect
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
