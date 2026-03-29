import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { fetchCrawlerStatus, type CrawlerStatusResponse } from "@/lib/api";

interface CrawlerContextValue {
  status: CrawlerStatusResponse | null;
  refresh: () => void;
}

const CrawlerContext = createContext<CrawlerContextValue>({
  status: null,
  refresh: () => {},
});

export function CrawlerProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<CrawlerStatusResponse | null>(null);

  const refresh = () => {
    fetchCrawlerStatus()
      .then(setStatus)
      .catch(() => {});
  };

  useEffect(() => {
    refresh();
    // Poll every 3 s — stops being meaningful once state=done but cost is negligible
    const id = setInterval(refresh, 3000);
    return () => clearInterval(id);
  }, []);

  return (
    <CrawlerContext.Provider value={{ status, refresh }}>
      {children}
    </CrawlerContext.Provider>
  );
}

export function useCrawlerStatus(): CrawlerContextValue {
  return useContext(CrawlerContext);
}
