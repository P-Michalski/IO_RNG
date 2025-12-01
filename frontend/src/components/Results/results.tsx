import { useState } from "react";
import { NoResults } from "./NoResults/no-results";

export const Results = () => {
  const [results, setResults] = useState([]);

  return results.length === 0 ? (
    <div className="flex items-center justify-center min-h-screen w-full">
      <NoResults />
    </div>
  ) : (
    <div>This is the Results component.</div>
  );
};
