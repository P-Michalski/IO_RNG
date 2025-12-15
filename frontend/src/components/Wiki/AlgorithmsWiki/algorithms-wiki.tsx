import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import { MarkdownRenderer } from "../markdown-renderer";

interface Algorithm {
  id: string;
  name: string;
  file: string;
}

const algorithms: Algorithm[] = [
  { id: "lcg", name: "Linear Congruential Generator (LCG)", file: "LCG.md" },
  { id: "park-miller", name: "Park-Miller", file: "Park_Miller.md" },
  { id: "pcg32", name: "PCG32", file: "PCG32.md" },
  { id: "splitmix64", name: "SplitMix64", file: "SplitMix64.md" },
  { id: "awcg", name: "Add-With-Carry Generator (AWCG)", file: "AWCG.md" },
  { id: "python-rng", name: "Python Random (MT19937)", file: "PythonRNG.md" },
  { id: "system-rng", name: "System RNG", file: "SystemRNG.md" },
  { id: "blum-blum-shub", name: "Blum Blum Shub", file: "BlumBlumShub.md" },
  { id: "chacha20", name: "ChaCha20", file: "ChaCha20.md" },
  { id: "xorshift", name: "Xorshift/Xoshiro", file: "Xorshift_Xoshiro.md" },
];

export const AlgorithmsWiki = () => {
  const { algorithmId } = useParams<{ algorithmId: string }>();
  const navigate = useNavigate();
  const [content, setContent] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const currentIndex = algorithms.findIndex((alg) => alg.id === algorithmId);
  const currentAlgorithm = algorithms[currentIndex];
  const prevAlgorithm = currentIndex > 0 ? algorithms[currentIndex - 1] : null;
  const nextAlgorithm =
    currentIndex < algorithms.length - 1 ? algorithms[currentIndex + 1] : null;

  useEffect(() => {
    // Redirect to first algorithm if no algorithmId
    if (!algorithmId) {
      navigate(`/wiki/algorithms/${algorithms[0].id}`);
      return;
    }

    const loadMarkdown = async () => {
      setLoading(true);
      setError(null);
      try {
        const module = await import(
          `../../../assets/algorithms/${currentAlgorithm.file}?raw`
        );
        setContent(module.default);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load content");
      } finally {
        setLoading(false);
      }
    };

    if (currentAlgorithm) {
      loadMarkdown();
    }
  }, [algorithmId, currentAlgorithm, navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error || !currentAlgorithm) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="p-6">
            <p className="text-destructive">{error || "Algorithm not found"}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl">{currentAlgorithm.name}</CardTitle>
        </CardHeader>
        <CardContent>
          <MarkdownRenderer content={content} />

          {/* Navigation */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t">
            {prevAlgorithm ? (
              <Button
                variant="outline"
                onClick={() => navigate(`/wiki/algorithms/${prevAlgorithm.id}`)}
              >
                <ChevronLeft className="mr-2 h-4 w-4" />
                Previous: {prevAlgorithm.name}
              </Button>
            ) : (
              <div />
            )}

            {nextAlgorithm ? (
              <Button
                onClick={() => navigate(`/wiki/algorithms/${nextAlgorithm.id}`)}
              >
                Next: {nextAlgorithm.name}
                <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            ) : (
              <div />
            )}
          </div>
        </CardContent>
      </Card>

      {/* Sidebar TOC */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-lg">All Algorithms</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {algorithms.map((alg) => (
            <Button
              key={alg.id}
              variant={alg.id === algorithmId ? "default" : "ghost"}
              className="w-full justify-start"
              onClick={() => navigate(`/wiki/algorithms/${alg.id}`)}
            >
              {alg.name}
            </Button>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};
