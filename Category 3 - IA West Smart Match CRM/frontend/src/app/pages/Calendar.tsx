import { useEffect, useState } from "react";
import {
  Building2,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  MapPin,
} from "lucide-react";

import { fetchCalendar, splitTags, type CalendarRecord } from "@/lib/api";

type CalendarView = "month" | "list";
type FilterType = "all" | "ia";

type CalendarEvent = {
  id: string;
  title: string;
  type: "ia";
  date: string;
  location: string;
  nearbyUniversities: string[];
  lectureWindow: string;
};

const months = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function mapCalendarRecord(record: CalendarRecord, index: number): CalendarEvent {
  const date = record["IA Event Date"];
  const region = record.Region || "Unknown Region";

  return {
    id: `${date}-${region}-${index}`,
    title: `IA West ${region} Event`,
    type: "ia",
    date,
    location: region,
    nearbyUniversities: splitTags(record["Nearby Universities"] || ""),
    lectureWindow: record["Suggested Lecture Window"] || "Window TBD",
  };
}

function getDaysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate();
}

function getFirstDayOfMonth(year: number, month: number) {
  return new Date(year, month, 1).getDay();
}

/** Parse "YYYY-MM-DD" as local-timezone midnight (avoids UTC shift). */
function parseLocalDate(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

export function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date(2026, 0, 1));
  const [view, setView] = useState<CalendarView>("month");
  const [filterType, setFilterType] = useState<FilterType>("all");
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    fetchCalendar()
      .then((data) => {
        if (!active) {
          return;
        }
        const mapped = data.map(mapCalendarRecord);
        setEvents(mapped);
        if (mapped[0]?.date) {
          const firstDate = parseLocalDate(mapped[0].date);
          if (!Number.isNaN(firstDate.getTime())) {
            setCurrentDate(new Date(firstDate.getFullYear(), firstDate.getMonth(), 1));
          }
        }
      })
      .catch((err: unknown) => {
        if (!active) {
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load calendar.");
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

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);

  const filteredEvents = events.filter(
    (event) => filterType === "all" || event.type === filterType,
  );

  const getEventsForDate = (day: number) => {
    const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    return filteredEvents.filter((event) => event.date === dateStr);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-gray-900">Event Calendar</h1>
        <p className="text-gray-600 mt-1">
          Track IA West event windows and the nearby university footprint.
        </p>
      </div>

      <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCurrentDate(new Date(year, month - 1, 1))}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Previous month"
            >
              <ChevronLeft className="w-5 h-5 text-gray-700" />
            </button>
            <h2 className="text-xl font-semibold text-gray-900 min-w-[200px] text-center">
              {months[month]} {year}
            </h2>
            <button
              onClick={() => setCurrentDate(new Date(year, month + 1, 1))}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Next month"
            >
              <ChevronRight className="w-5 h-5 text-gray-700" />
            </button>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex gap-2">
              <button
                onClick={() => setView("month")}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  view === "month"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                Month
              </button>
              <button
                onClick={() => setView("list")}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  view === "list"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                List
              </button>
            </div>

            <select
              value={filterType}
              onChange={(event) => setFilterType(event.target.value as FilterType)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Events</option>
              <option value="ia">IA Events</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-6 px-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 rounded" />
          <span className="text-sm text-gray-700">IA Event Windows</span>
        </div>
      </div>

      {error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700 text-center">
          {error}
        </div>
      ) : null}

      {loading ? (
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm animate-pulse h-72" />
      ) : view === "month" ? (
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="grid grid-cols-7 gap-2">
            {daysOfWeek.map((day) => (
              <div key={day} className="text-center text-sm font-medium text-gray-700 py-2">
                {day}
              </div>
            ))}

            {Array.from({ length: firstDay }).map((_, index) => (
              <div key={`empty-${index}`} className="aspect-square" />
            ))}

            {Array.from({ length: daysInMonth }).map((_, index) => {
              const day = index + 1;
              const dayEvents = getEventsForDate(day);
              const now = new Date();
              const isToday = day === now.getDate() && month === now.getMonth() && year === now.getFullYear();

              return (
                <div
                  key={day}
                  className={`aspect-square border border-gray-200 rounded-lg p-2 ${
                    isToday ? "bg-blue-50 border-blue-300" : "bg-white"
                  }`}
                >
                  <div
                    className={`text-sm font-medium mb-1 ${
                      isToday ? "text-blue-600" : "text-gray-900"
                    }`}
                  >
                    {day}
                  </div>
                  <div className="space-y-1">
                    {dayEvents.slice(0, 2).map((event) => (
                      <div
                        key={event.id}
                        className="text-xs p-1 rounded truncate bg-blue-100 text-blue-700"
                        title={event.title}
                      >
                        {event.title}
                      </div>
                    ))}
                    {dayEvents.length > 2 ? (
                      <div className="text-xs text-gray-500">+{dayEvents.length - 2} more</div>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredEvents.map((event) => (
            <div
              key={event.id}
              className="bg-white rounded-xl p-6 border-l-4 border border-gray-200 border-l-blue-500 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{event.title}</h3>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                      IA Event
                    </span>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <CalendarDays className="w-4 h-4" />
                      {parseLocalDate(event.date).toLocaleDateString("en-US", {
                        weekday: "long",
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <MapPin className="w-4 h-4" />
                      {event.location}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Building2 className="w-4 h-4" />
                      {event.nearbyUniversities.join(", ") || "Nearby campuses not listed"}
                    </div>
                    <div className="text-sm text-gray-600">
                      <span className="font-medium text-gray-900">Suggested lecture window:</span>{" "}
                      {event.lectureWindow}
                    </div>
                  </div>
                </div>

                <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium">
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
