import { useEffect, useState } from "react";
import { Briefcase, Check, MapPin, Search, X } from "lucide-react";

import { fetchSpecialists, splitTags, type Specialist } from "@/lib/api";

function VolunteerSkeleton() {
  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm animate-pulse">
      <div className="flex items-start gap-4 mb-4">
        <div className="w-16 h-16 rounded-full bg-gray-200" />
        <div className="flex-1 space-y-2">
          <div className="h-4 w-2/3 rounded bg-gray-200" />
          <div className="h-3 w-1/2 rounded bg-gray-200" />
          <div className="h-5 w-24 rounded-full bg-gray-200" />
        </div>
      </div>
      <div className="space-y-2 mb-4">
        <div className="h-3 rounded bg-gray-200" />
        <div className="h-3 rounded bg-gray-200" />
      </div>
      <div className="flex flex-wrap gap-2">
        <div className="h-6 w-20 rounded-md bg-gray-200" />
        <div className="h-6 w-24 rounded-md bg-gray-200" />
        <div className="h-6 w-16 rounded-md bg-gray-200" />
      </div>
    </div>
  );
}

export function Volunteers() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedVolunteer, setSelectedVolunteer] = useState<string | null>(null);
  const [volunteers, setVolunteers] = useState<Specialist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    fetchSpecialists()
      .then((data) => {
        if (!active) {
          return;
        }
        setVolunteers(data);
      })
      .catch((err: unknown) => {
        if (!active) {
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load volunteers.");
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

  const filteredVolunteers = volunteers.filter((volunteer) => {
    const expertise = splitTags(volunteer.expertise_tags);
    const query = searchQuery.trim().toLowerCase();
    if (!query) {
      return true;
    }

    return (
      volunteer.name.toLowerCase().includes(query) ||
      volunteer.company.toLowerCase().includes(query) ||
      volunteer.metro_region.toLowerCase().includes(query) ||
      expertise.some((tag) => tag.toLowerCase().includes(query))
    );
  });

  const selectedVol =
    volunteers.find((volunteer) => volunteer.name === selectedVolunteer) ?? null;

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-gray-900">Volunteer Profiles</h1>
        <p className="text-gray-600 mt-1">
          Browse and manage IA West specialist profiles from the live roster.
        </p>
      </div>

      <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name, company, region, or expertise..."
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700 text-center">
          {error}
        </div>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {loading
          ? Array.from({ length: 6 }, (_, index) => <VolunteerSkeleton key={index} />)
          : filteredVolunteers.map((volunteer) => {
              const expertise = splitTags(volunteer.expertise_tags);
              return (
                <div
                  key={volunteer.name}
                  className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => setSelectedVolunteer(volunteer.name)}
                >
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-400 rounded-full flex items-center justify-center text-white text-xl font-semibold">
                      {volunteer.initials}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900 truncate">{volunteer.name}</h3>
                      <p className="text-sm text-gray-600">{volunteer.title || "Board volunteer"}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                          <Check className="w-3 h-3" />
                          {volunteer.board_role || "Available"}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Briefcase className="w-4 h-4" />
                      {volunteer.company || "Independent"}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <MapPin className="w-4 h-4" />
                      {volunteer.metro_region || "Region not listed"}
                    </div>
                  </div>

                  <div className="mb-4">
                    <p className="text-xs text-gray-500 mb-2">Expertise:</p>
                    <div className="flex flex-wrap gap-1">
                      {expertise.slice(0, 4).map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-md"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                    <div className="text-center">
                      <p className="text-sm text-gray-600">Board Role</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {volunteer.board_role || "Member"}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-600">Skill Tags</p>
                      <p className="text-lg font-semibold text-blue-600">{expertise.length}</p>
                    </div>
                  </div>
                </div>
              );
            })}
      </div>

      {!loading && !error && filteredVolunteers.length === 0 ? (
        <div className="bg-white rounded-xl p-10 border border-gray-200 shadow-sm text-center text-gray-600">
          No volunteers matched that search.
        </div>
      ) : null}

      {selectedVol ? (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedVolunteer(null)}
        >
          <div
            className="bg-white rounded-xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-start gap-6 mb-6">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-400 to-blue-400 rounded-full flex items-center justify-center text-white text-3xl font-semibold">
                {selectedVol.initials}
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-semibold text-gray-900">{selectedVol.name}</h2>
                <p className="text-gray-600 mt-1">{selectedVol.title || "Board volunteer"}</p>
                <p className="text-gray-600">{selectedVol.company || "Independent"}</p>
                <div className="flex items-center gap-2 mt-3">
                  <span className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">
                    <Check className="w-4 h-4" />
                    {selectedVol.board_role || "Available"}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedVolunteer(null)}
                className="text-gray-400 hover:text-gray-600"
                aria-label="Close volunteer details"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Profile</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-gray-600">
                    <MapPin className="w-4 h-4" />
                    {selectedVol.metro_region || "Region not listed"}
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <Briefcase className="w-4 h-4" />
                    {selectedVol.company || "Independent"}
                  </div>
                  <div className="text-gray-600">
                    <span className="font-medium text-gray-900">Board Role:</span>{" "}
                    {selectedVol.board_role || "Member"}
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Expertise</h3>
                <div className="flex flex-wrap gap-2">
                  {splitTags(selectedVol.expertise_tags).map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1.5 bg-blue-50 text-blue-700 text-sm rounded-lg"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
