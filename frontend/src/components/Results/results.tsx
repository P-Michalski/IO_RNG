import { useState, useEffect } from "react";
import { NoResults } from "./NoResults/no-results";
import { TestResultCard } from "./test-result-card";
import { type TestResult, type RNG } from "@/types/test-results";
import { Loading } from "../Loading/loading";
import { Error as ErrorComponent } from "../Error/error";

export const Results = () => {
  const [results, setResults] = useState<TestResult[]>([]);
  const [rngs, setRngs] = useState<RNG[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [resultsRes, rngsRes] = await Promise.all([
          fetch("http://localhost:8000/api/test-results/"),
          fetch("http://localhost:8000/api/rngs/"),
        ]);

        if (!resultsRes.ok || !rngsRes.ok) {
          throw new Error("Failed to fetch data");
        }

        const resultsData = await resultsRes.json();
        const rngsData = await rngsRes.json();

        setResults(resultsData);
        setRngs(rngsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <Loading />;
  }

  if (error) {
    return <ErrorComponent />;
  }

  if (results.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen w-full">
        <NoResults />
      </div>
    );
  }

  const getRngName = (rngId: number) => {
    const rng = rngs.find((r) => r.id === rngId);
    return rng?.name || `RNG #${rngId}`;
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Test Results</h1>
        <p className="text-muted-foreground">
          View and analyze your RNG test results
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {results.map((result) => (
          <TestResultCard
            key={result.id}
            result={result}
            rngName={getRngName(result.rng_id)}
          />
        ))}
      </div>
    </div>
  );
};
