import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { MarkdownRenderer } from "../markdown-renderer";
import { useLanguage } from "@/contexts/language-context";
import { LanguageSwitcher } from "@/components/language-switcher";
import { Loading } from "@/components/Loading/loading";
import { Error as ErrorComponent } from "@/components/Error/error";

interface Algorithm {
  id: string;
  name: string;
  shortName?: string;
  file: string;
}

const algorithms: Algorithm[] = [
  {
    id: "lcg",
    name: "Linear Congruential Generator",
    shortName: "LCG",
    file: "LCG",
  },
  { id: "park-miller", name: "Park-Miller", file: "Park_Miller" },
  { id: "pcg32", name: "PCG32", file: "PCG32" },
  { id: "splitmix64", name: "SplitMix64", file: "SplitMix64" },
  {
    id: "awcg",
    name: "Add-With-Carry Generator",
    shortName: "AWCG",
    file: "AWCG",
  },
  {
    id: "python-rng",
    name: "Python Random (MT19937)",
    shortName: "Python RNG",
    file: "PythonRNG",
  },
  { id: "system-rng", name: "System RNG", file: "SystemRNG" },
  { id: "blum-blum-shub", name: "Blum Blum Shub", file: "BlumBlumShub" },
  { id: "chacha20", name: "ChaCha20", file: "ChaCha20" },
  { id: "xorshift", name: "Xorshift/Xoshiro", file: "Xorshift_Xoshiro" },
];

const getName = (alg: Algorithm) => alg.shortName || alg.name;

const translations = {
  en: {
    previous: "Previous",
    next: "Next",
    allAlgorithms: "All Algorithms",
    algorithmNotFound: "Algorithm not found",
  },
  pl: {
    previous: "Poprzedni",
    next: "Następny",
    allAlgorithms: "Wszystkie Algorytmy",
    algorithmNotFound: "Nie znaleziono algorytmu",
  },
};

export const AlgorithmsWiki = () => {
  const { algorithmId } = useParams<{ algorithmId: string }>();
  const navigate = useNavigate();
  const [content, setContent] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { language } = useLanguage();

  const t = translations[language as keyof typeof translations];

  const currentIndex = algorithms.findIndex((alg) => alg.id === algorithmId);
  const currentAlgorithm = algorithms[currentIndex];
  const prevAlgorithm = currentIndex > 0 ? algorithms[currentIndex - 1] : null;
  const nextAlgorithm =
    currentIndex < algorithms.length - 1 ? algorithms[currentIndex + 1] : null;

  useEffect(() => {
    if (!algorithmId) {
      navigate(`/wiki/algorithms/${algorithms[0].id}`);
      return;
    }

    const loadMarkdown = async () => {
      setLoading(true);
      setError(null);
      try {
        const fileName =
          language === "en"
            ? `${currentAlgorithm.file}_eng.md`
            : `${currentAlgorithm.file}.md`;

        const module = await import(
          `../../../assets/algorithms/${fileName}?raw`
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
  }, [algorithmId, currentAlgorithm, navigate, language]);

  if (loading) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <Loading message="Loading Wiki..." fullScreen />
      </div>
    );
  }

  if (error || !currentAlgorithm) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <ErrorComponent description={error || "Algorithm not found"} />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-8 max-w-4xl overflow-hidden">
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="text-2xl sm:text-3xl font-bold tracking-tight wrap-break-word min-w-0">
              {currentAlgorithm.name}
            </CardTitle>
            <div className="flex justify-end">
              <LanguageSwitcher />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <MarkdownRenderer content={content} />

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2 mt-8 pt-6 border-t min-w-0">
            {prevAlgorithm ? (
              <Button
                variant="outline"
                onClick={() => navigate(`/wiki/algorithms/${prevAlgorithm.id}`)}
                className="w-full sm:w-auto sm:max-w-[48%] min-w-0 justify-start"
              >
                <ChevronLeft className="mr-1 h-4 w-4 shrink-0" />
                {t.previous}: {getName(prevAlgorithm)}
              </Button>
            ) : (
              <div className="hidden sm:block" />
            )}

            {nextAlgorithm ? (
              <Button
                onClick={() => navigate(`/wiki/algorithms/${nextAlgorithm.id}`)}
                className="w-full sm:w-auto sm:max-w-[48%] min-w-0 justify-end"
              >
                {t.next}: {getName(nextAlgorithm)}
                <ChevronRight className="h-4 w-4 shrink-0" />
              </Button>
            ) : (
              <div className="hidden sm:block" />
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-lg">{t.allAlgorithms}</CardTitle>
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
