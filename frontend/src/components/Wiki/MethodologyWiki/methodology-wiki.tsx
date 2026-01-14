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

interface Test {
  id: string;
  name: string;
  shortName?: string;
  file: string;
}

const tests: Test[] = [
  // Basic Tests
  {
    id: "frequency-test",
    name: "Frequency Test",
    file: "FrequencyTest",
  },
  {
    id: "uniformity-test",
    name: "Uniformity Test",
    file: "UniformityTest",
  },
  // NIST Tests
  {
    id: "nist-monobit",
    name: "NIST Monobit Test",
    shortName: "Monobit",
    file: "NIST_Monobit",
  },
  {
    id: "nist-block-frequency",
    name: "NIST Block Frequency Test",
    shortName: "Block Frequency",
    file: "NIST_BlockFrequency",
  },
  {
    id: "nist-runs",
    name: "NIST Runs Test",
    shortName: "Runs",
    file: "NIST_Runs",
  },
  {
    id: "nist-longest-run",
    name: "NIST Longest Run of Ones Test",
    shortName: "Longest Run",
    file: "NIST_LongestRun",
  },
  {
    id: "nist-matrix-rank",
    name: "NIST Binary Matrix Rank Test",
    shortName: "Matrix Rank",
    file: "NIST_MatrixRank",
  },
  {
    id: "nist-dft",
    name: "NIST Discrete Fourier Transform Test",
    shortName: "DFT",
    file: "NIST_DFT",
  },
  {
    id: "nist-non-overlapping-template",
    name: "NIST Non-Overlapping Template Matching Test",
    shortName: "Non-Overlapping Template",
    file: "NIST_NonOverlappingTemplate",
  },
  {
    id: "nist-overlapping-template",
    name: "NIST Overlapping Template Matching Test",
    shortName: "Overlapping Template",
    file: "NIST_OverlappingTemplate",
  },
  {
    id: "nist-universal",
    name: "NIST Universal Statistical Test",
    shortName: "Universal",
    file: "NIST_Universal",
  },
  {
    id: "nist-approximate-entropy",
    name: "NIST Approximate Entropy Test",
    shortName: "Approximate Entropy",
    file: "NIST_ApproximateEntropy",
  },
  {
    id: "nist-serial",
    name: "NIST Serial Test",
    shortName: "Serial",
    file: "NIST_Serial",
  },
  {
    id: "nist-cumulative-sums",
    name: "NIST Cumulative Sums Test",
    shortName: "Cumulative Sums",
    file: "NIST_CumulativeSums",
  },
  {
    id: "nist-random-excursions",
    name: "NIST Random Excursions Test",
    shortName: "Random Excursions",
    file: "NIST_RandomExcursions",
  },
  {
    id: "nist-random-excursions-variant",
    name: "NIST Random Excursions Variant Test",
    shortName: "Random Excursions Variant",
    file: "NIST_RandomExcursionsVariant",
  },
  {
    id: "nist-linear-complexity",
    name: "NIST Linear Complexity Test",
    shortName: "Linear Complexity",
    file: "NIST_LinearComplexity",
  },
  // Diehard Tests
  {
    id: "diehard-birthday-spacings",
    name: "Diehard Birthday Spacings Test",
    shortName: "Birthday Spacings",
    file: "Diehard_BirthdaySpacings",
  },
  {
    id: "diehard-overlapping-permutations",
    name: "Diehard Overlapping Permutations Test",
    shortName: "Overlapping Permutations",
    file: "Diehard_OverlappingPermutations",
  },
  {
    id: "diehard-binary-rank",
    name: "Diehard Binary Rank Test",
    shortName: "Binary Rank",
    file: "Diehard_BinaryRank",
  },
  {
    id: "diehard-bitstream",
    name: "Diehard Bitstream Test",
    shortName: "Bitstream",
    file: "Diehard_Bitstream",
  },
  {
    id: "diehard-opso",
    name: "Diehard OPSO Test",
    shortName: "OPSO",
    file: "Diehard_OPSO",
  },
  {
    id: "diehard-oqso",
    name: "Diehard OQSO Test",
    shortName: "OQSO",
    file: "Diehard_OQSO",
  },
  {
    id: "diehard-dna",
    name: "Diehard DNA Test",
    shortName: "DNA",
    file: "Diehard_DNA",
  },
  {
    id: "diehard-count-1s",
    name: "Diehard Count the 1s Test",
    shortName: "Count the 1s",
    file: "Diehard_Count1s",
  },
  {
    id: "diehard-parking-lot",
    name: "Diehard Parking Lot Test",
    shortName: "Parking Lot",
    file: "Diehard_ParkingLot",
  },
  {
    id: "diehard-minimum-distance",
    name: "Diehard Minimum Distance Test",
    shortName: "Minimum Distance",
    file: "Diehard_MinimumDistance",
  },
  {
    id: "diehard-3d-spheres",
    name: "Diehard 3D Spheres Test",
    shortName: "3D Spheres",
    file: "Diehard_3DSpheres",
  },
  {
    id: "diehard-squeeze",
    name: "Diehard Squeeze Test",
    shortName: "Squeeze",
    file: "Diehard_Squeeze",
  },
  {
    id: "diehard-overlapping-sums",
    name: "Diehard Overlapping Sums Test",
    shortName: "Overlapping Sums",
    file: "Diehard_OverlappingSums",
  },
  {
    id: "diehard-runs",
    name: "Diehard Runs Test",
    shortName: "Runs",
    file: "Diehard_Runs",
  },
  {
    id: "diehard-craps",
    name: "Diehard Craps Test",
    shortName: "Craps",
    file: "Diehard_Craps",
  },
];

const getName = (test: Test) => test.shortName || test.name;

const translations = {
  en: {
    previous: "Previous",
    next: "Next",
    allTests: "All Tests",
    testNotFound: "Test not found",
  },
  pl: {
    previous: "Poprzedni",
    next: "Następny",
    allTests: "Wszystkie Testy",
    testNotFound: "Nie znaleziono testu",
  },
};

export const MethodologyWiki = () => {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();
  const [content, setContent] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { language } = useLanguage();

  const t = translations[language as keyof typeof translations];

  const currentIndex = tests.findIndex((test) => test.id === testId);
  const currentTest = tests[currentIndex];
  const prevTest = currentIndex > 0 ? tests[currentIndex - 1] : null;
  const nextTest =
    currentIndex < tests.length - 1 ? tests[currentIndex + 1] : null;

  const handleNavigation = (path: string) => {
    window.scrollTo({ top: 0, behavior: "smooth" });
    navigate(path);
  };

  useEffect(() => {
    if (!testId) {
      navigate(`/wiki/methodology/${tests[0].id}`);
      return;
    }

    const loadMarkdown = async () => {
      setLoading(true);
      setError(null);
      try {
        const fileName =
          language === "en"
            ? `${currentTest.file}_eng.md`
            : `${currentTest.file}.md`;

        const module = await import(`../../../assets/tests/${fileName}?raw`);
        setContent(module.default);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load content");
      } finally {
        setLoading(false);
      }
    };

    if (currentTest) {
      loadMarkdown();
    }
  }, [testId, currentTest, navigate, language]);

  if (loading) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <Loading message="Loading Wiki..." fullScreen />
      </div>
    );
  }

  if (error || !currentTest) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <ErrorComponent description={error || t.testNotFound} />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-8 max-w-4xl overflow-hidden">
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="text-2xl sm:text-3xl font-bold tracking-tight wrap-break-word min-w-0">
              {currentTest.name}
            </CardTitle>
            <div className="flex justify-end">
              <LanguageSwitcher />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <MarkdownRenderer content={content} />

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2 mt-8 pt-6 border-t min-w-0">
            {prevTest ? (
              <Button
                variant="outline"
                onClick={() =>
                  handleNavigation(`/wiki/methodology/${prevTest.id}`)
                }
                className="w-full sm:w-auto sm:max-w-[48%] min-w-0 justify-start overflow-hidden"
              >
                <ChevronLeft className="mr-1 h-4 w-4 shrink-0" />
                <span className="truncate">
                  {t.previous}: {getName(prevTest)}
                </span>
              </Button>
            ) : (
              <div className="hidden sm:block" />
            )}

            {nextTest ? (
              <Button
                onClick={() =>
                  handleNavigation(`/wiki/methodology/${nextTest.id}`)
                }
                className="w-full sm:w-auto sm:max-w-[48%] min-w-0 justify-end overflow-hidden"
              >
                <span className="truncate">
                  {t.next}: {getName(nextTest)}
                </span>
                <ChevronRight className="ml-1 h-4 w-4 shrink-0" />
              </Button>
            ) : (
              <div className="hidden sm:block" />
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-lg">{t.allTests}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {tests.map((test) => (
            <Button
              key={test.id}
              variant={test.id === testId ? "default" : "ghost"}
              className="w-full justify-start overflow-hidden"
              onClick={() => handleNavigation(`/wiki/methodology/${test.id}`)}
            >
              <span className="truncate">{test.name}</span>
            </Button>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};
