import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import { type TestResult, type RNG } from "@/types/test-results";
import { toast } from "sonner";

interface TestResultsContextType {
  results: TestResult[];
  rngs: RNG[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  getRngName: (rngId: number) => string;
}

const TestResultsContext = createContext<TestResultsContextType | undefined>(
  undefined
);

export const TestResultsProvider = ({ children }: { children: ReactNode }) => {
  const [results, setResults] = useState<TestResult[]>([]);
  const [rngs, setRngs] = useState<RNG[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastFetch, setLastFetch] = useState<number>(0);

  const fetchData = async (force = false) => {
    const now = Date.now();
    // Fetch only if forced or last fetch was more than 5 seconds ago
    if (!force && now - lastFetch < 5000 && results.length > 0) {
      return;
    }

    try {
      setLoading(true);
      const [resultsRes, rngsRes] = await Promise.all([
        fetch("http://localhost:8000/api/test-results"),
        fetch("http://localhost:8000/api/rngs"),
      ]);

      if (!resultsRes.ok || !rngsRes.ok) {
        throw new Error("Failed to fetch data");
      }

      const resultsData = await resultsRes.json();
      const rngsData = await rngsRes.json();

      setResults(resultsData);
      setRngs(rngsData);
      setLastFetch(now);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      toast.error("Failed to load results. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getRngName = (rngId: number) => {
    const rng = rngs.find((r) => r.id === rngId);
    return rng?.name || `RNG #${rngId}`;
  };

  return (
    <TestResultsContext.Provider
      value={{
        results,
        rngs,
        loading,
        error,
        refetch: () => fetchData(true),
        getRngName,
      }}
    >
      {children}
    </TestResultsContext.Provider>
  );
};

export const useTestResults = () => {
  const context = useContext(TestResultsContext);
  if (!context) {
    throw new Error("useTestResults must be used within TestResultsProvider");
  }
  return context;
};
