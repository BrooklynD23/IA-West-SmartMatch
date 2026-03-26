import { useEffect, useState } from "react";
import {
  Building2,
  Calendar,
  ExternalLink,
  Filter,
  MapPin,
  Search,
  Sparkles,
  Users,
} from "lucide-react";

import { fetchEvents, splitTags, type CppEvent } from "@/lib/api";

type OpportunityCard = {
  id: string;
  name: string;
  university: string;
  date: string;
  location: string;
  role: string;
  tags: string[];
  type: string;
  audience: string;
  url: string;
};

function mapEventToOpportunity(event: CppEvent, index: number): OpportunityCard {
  const name = event["Event / Program"] || `Opportunity ${index + 1}`;
  const university = event["Host / Unit"] || "IA West partner";
  const tags = [
    ...splitTags(event.Category || ""),
    ...splitTags(event["Volunteer Roles (fit)"] || "").slice(0, 2),
  ].filter((value, idx, values) => values.indexOf(value) === idx);

  return {
    id: `${name}-${index}`,
    name,
    university,
    date: event["Recurrence (typical)"] || "Schedule varies",
    location: university,
    role: splitTags(event["Volunteer Roles (fit)"] || "")[0] || "Guest speaker",
    tags,
    type: event.Category || "Opportunity",
    audience: event["Primary Audience"] || "Students",
    url: event["Public URL"] || "",
  };
}

export function Opportunities() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLocation, setSelectedLocation] = useState("All Locations");
  const [selectedRole, setSelectedRole] = useState("All Roles");
  const [selectedType, setSelectedType] = useState("All Types");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [opportunities, setOpportunities] = useState<OpportunityCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    fetchEvents()
      .then((events) => {
        if (!active) {
          return;
        }
        setOpportunities(events.map(mapEventToOpportunity));
      })
      .catch((err: unknown) => {
        if (!active) {
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load opportunities.");
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

  const locations = [
    "All Locations",
    ...Array.from(new Set(opportunities.map((opp) => opp.location))),
  ];
  const roles = ["All Roles", ...Array.from(new Set(opportunities.map((opp) => opp.role)))];
  const types = ["All Types", ...Array.from(new Set(opportunities.map((opp) => opp.type)))];
  const tags = Array.from(new Set(opportunities.flatMap((opp) => opp.tags))).sort();

  const filteredOpportunities = opportunities.filter((opp) => {
    const query = searchQuery.trim().toLowerCase();
    const matchesSearch =
      !query ||
      opp.name.toLowerCase().includes(query) ||
      opp.university.toLowerCase().includes(query);
    const matchesLocation =
      selectedLocation === "All Locations" || opp.location === selectedLocation;
    const matchesRole = selectedRole === "All Roles" || opp.role === selectedRole;
    const matchesType = selectedType === "All Types" || opp.type === selectedType;
    const matchesTags =
      selectedTags.length === 0 || selectedTags.some((tag) => opp.tags.includes(tag));

    return matchesSearch && matchesLocation && matchesRole && matchesType && matchesTags;
  });

  const toggleTag = (tag: string) => {
    setSelectedTags((previous) =>
      previous.includes(tag)
        ? previous.filter((value) => value !== tag)
        : [...previous, tag],
    );
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-gray-900">Opportunities</h1>
          <p className="text-gray-600 mt-1">
            Discover and match university engagement opportunities from the live dataset.
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg">
          <Sparkles className="w-5 h-5" />
          Find Best Matches
        </button>
      </div>

      <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search opportunities by name or host..."
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filters:</span>
          </div>

          <select
            value={selectedLocation}
            onChange={(event) => setSelectedLocation(event.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {locations.map((location) => (
              <option key={location} value={location}>
                {location}
              </option>
            ))}
          </select>

          <select
            value={selectedRole}
            onChange={(event) => setSelectedRole(event.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {roles.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>

          <select
            value={selectedType}
            onChange={(event) => setSelectedType(event.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {types.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-wrap gap-2">
          {tags.map((tag) => (
            <button
              key={tag}
              onClick={() => toggleTag(tag)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                selectedTags.includes(tag)
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700 text-center">
          {error}
        </div>
      ) : null}

      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">
          Showing {filteredOpportunities.length} of {opportunities.length} opportunities
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {loading
          ? Array.from({ length: 6 }, (_, index) => (
              <div
                key={index}
                className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm animate-pulse"
              >
                <div className="h-5 w-2/3 rounded bg-gray-200 mb-4" />
                <div className="space-y-3">
                  <div className="h-3 rounded bg-gray-200" />
                  <div className="h-3 rounded bg-gray-200" />
                  <div className="h-3 rounded bg-gray-200" />
                </div>
              </div>
            ))
          : filteredOpportunities.map((opportunity) => (
              <div
                key={opportunity.id}
                className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-2">{opportunity.name}</h3>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Building2 className="w-4 h-4" />
                      {opportunity.university}
                    </div>
                  </div>
                  <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">
                    {opportunity.type}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Calendar className="w-4 h-4" />
                    {opportunity.date}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <MapPin className="w-4 h-4" />
                    {opportunity.location}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Users className="w-4 h-4" />
                    {opportunity.audience}
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-2">Required Role:</p>
                  <span className="inline-flex px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
                    {opportunity.role}
                  </span>
                </div>

                <div className="mb-6">
                  <p className="text-sm text-gray-600 mb-2">Tags:</p>
                  <div className="flex flex-wrap gap-2">
                    {opportunity.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-md"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium">
                    Match Volunteers
                  </button>
                  {opportunity.url ? (
                    <a
                      href={opportunity.url}
                      target="_blank"
                      rel="noreferrer"
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <ExternalLink className="w-5 h-5" />
                    </a>
                  ) : null}
                </div>
              </div>
            ))}
      </div>

      {!loading && !error && filteredOpportunities.length === 0 ? (
        <div className="bg-white rounded-xl p-10 border border-gray-200 shadow-sm text-center text-gray-600">
          No opportunities matched the active filters.
        </div>
      ) : null}
    </div>
  );
}
