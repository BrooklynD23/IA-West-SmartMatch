import { useEffect, useRef, useState } from "react";
import { CheckCircle2, Globe, Loader2, XCircle } from "lucide-react";

import { Button } from "@/app/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { startCrawl, type CrawlerEvent } from "@/lib/api";

interface CrawlerFeedProps {
  className?: string;
}

export function CrawlerFeed({ className }: CrawlerFeedProps) {
  const [events, setEvents] = useState<CrawlerEvent[]>([]);
  const [isActive, setIsActive] = useState(false);
  const [isDone, setIsDone] = useState(false);
  const [foundCount, setFoundCount] = useState(0);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!isActive) {
      return;
    }

    const es = new EventSource("/api/crawler/feed");
    esRef.current = es;

    es.onmessage = (e: MessageEvent) => {
      let data: Partial<CrawlerEvent> & { status?: string };
      try {
        data = JSON.parse(e.data as string) as Partial<CrawlerEvent> & { status?: string };
      } catch {
        return;
      }

      if (data.status === "done") {
        setIsDone(true);
        setIsActive(false);
        es.close();
        return;
      }

      const event: CrawlerEvent = {
        url: data.url ?? "",
        title: data.title ?? "",
        status: (data.status as CrawlerEvent["status"]) ?? "crawling",
        timestamp: data.timestamp ?? new Date().toISOString(),
      };

      setEvents((prev) => {
        const updated = [event, ...prev].slice(0, 50);
        const found = updated.filter((ev) => ev.status === "found").length;
        setFoundCount(found);
        return updated;
      });
    };

    es.onerror = () => {
      es.close();
      setIsActive(false);
    };

    return () => {
      esRef.current?.close();
    };
  }, [isActive]);

  async function handleStartCrawl() {
    setIsActive(true);
    setIsDone(false);
    setEvents([]);
    setFoundCount(0);
    try {
      await startCrawl();
    } catch {
      // SSE stream will independently signal errors via onerror
    }
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Globe className="h-4 w-4" />
            Web Crawler Feed
          </CardTitle>
          <Button
            size="sm"
            variant={isActive ? "outline" : "default"}
            onClick={() => { void handleStartCrawl(); }}
            disabled={isActive}
          >
            {isActive ? "Crawling..." : "Start Crawl"}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isDone && (
          <div className="mb-3 rounded-md bg-green-50 px-3 py-2 text-sm text-green-700">
            Found {foundCount} directed school pages — results saved
          </div>
        )}
        <div className="max-h-[320px] overflow-y-auto space-y-1.5">
          {events.length === 0 && !isActive && (
            <p className="text-sm text-muted-foreground py-4 text-center">
              Click &quot;Start Crawl&quot; to discover IA West directed school pages
            </p>
          )}
          {events.map((event, i) => (
            <div
              key={`${event.timestamp}-${i}`}
              className="flex items-start gap-2 rounded-md px-2 py-1.5 text-sm transition-all duration-300"
            >
              <span className="mt-0.5 shrink-0">
                {event.status === "crawling" && (
                  <Loader2 className="h-3.5 w-3.5 animate-spin text-blue-500" />
                )}
                {event.status === "found" && (
                  <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                )}
                {event.status === "error" && (
                  <XCircle className="h-3.5 w-3.5 text-red-400" />
                )}
              </span>
              <div className="min-w-0 flex-1">
                <span className="font-medium truncate block">
                  {event.title || event.url}
                </span>
                {event.url && event.title && (
                  <span className="text-xs text-muted-foreground truncate block">
                    {event.url}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default CrawlerFeed;
