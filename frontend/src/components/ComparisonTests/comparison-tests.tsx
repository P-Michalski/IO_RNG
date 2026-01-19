import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { type RNG } from "@/types/test-results";
import {
  GitCompare,
  Loader2,
  Play,
  BarChart3,
  TrendingDown,
  Activity,
  TrendingUp,
  CheckCircle2,
  XCircle,
  Clock,
  Trophy,
} from "lucide-react";
import { Loading } from "../Loading/loading";
import { Error as ErrorComponent } from "../Error/error";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";

// Pula wszystkich dostępnych testów NIST
const ALL_NIST_TESTS = [
  "nist_monobit",
  "nist_block_frequency",
  "nist_runs",
  "nist_longest_run",
  "nist_matrix_rank",
  "nist_dft",
  "nist_serial",
  "nist_approximate_entropy",
  "nist_cumulative_sums",
  "nist_linear_complexity",
  "nist_overlapping_template",
  "nist_non_overlapping_template",
] as const;

// Parametry algorytmów dla różnych scenariuszy
const SCENARIO_PARAMS = {
  worst: {
    // Najgorsze parametry - BARDZO słabe, celowo złe wartości
    2: { seed: 0, bits_per_value: 16, msb_first: 0 }, // SplitMix64 - seed=0, tylko 16 bitów, LSB first
    3: { seed: 0, a: 1, c: 1, m: 256, bits_per_value: 8, msb_first: 0 }, // LCG - KATASTROFALNE parametry: a=1, c=1, m=256
    4: { seed: 1, bits_per_value: 8, msb_first: 0 }, // Park-Miller - tylko 8 bitów
    5: { initstate: 0, seq: 0, bits_per_value: 16, msb_first: 0 }, // PCG32 - zero init, 16 bitów
    6: { seed: 0, bits_per_value: 16, msb_first: 0 }, // Mersenne Twister - seed=0, 16 bitów
    7: { bits_per_value: 8, msb_first: 0 }, // OS /dev/urandom - tylko 8 bitów
    11: { seed: 0, r: 2, s: 1, base: 100, bits_per_value: 8, msb_first: 0 }, // AWCG - bardzo małe wartości
    16: { seed: 1, p: 3, q: 5, bits_per_value: 1, msb_first: 1 }, // Blum Blum Shub - najmniejsze możliwe liczby pierwsze
    23: { bits_per_value: 8, msb_first: 0 }, // ChaCha20 - tylko 8 bitów
    24: { bits_per_value: 8, msb_first: 0 }, // Xoshiro256** - tylko 8 bitów
  },
  medium: {
    // Średnie parametry - standardowe wartości
    2: { seed: 123456789, bits_per_value: 64, msb_first: 1 },
    3: { seed: 123456789, a: 1664525, c: 1013904223, m: 4294967296, bits_per_value: 32, msb_first: 1 },
    4: { seed: 123456789, bits_per_value: 31, msb_first: 1 },
    5: { initstate: 42, seq: 54, bits_per_value: 32, msb_first: 1 },
    6: { seed: 12345, bits_per_value: 32, msb_first: 1 },
    7: { bits_per_value: 32, msb_first: 1 },
    11: { seed: 123456789, r: 24, s: 10, base: 4294967296, bits_per_value: 32, msb_first: 1 },
    16: { seed: 12345, p: 383, q: 503, bits_per_value: 1, msb_first: 1 },
    23: { bits_per_value: 32, msb_first: 1 },
    24: { bits_per_value: 32, msb_first: 1 },
  },
  best: {
    // Najlepsze parametry - optymalne seedy i wartości
    2: { seed: 9876543210, bits_per_value: 64, msb_first: 1 },
    3: { seed: 987654321, a: 1664525, c: 1013904223, m: 4294967296, bits_per_value: 32, msb_first: 1 },
    4: { seed: 987654321, bits_per_value: 31, msb_first: 1 },
    5: { initstate: 314159265, seq: 271828182, bits_per_value: 32, msb_first: 1 },
    6: { seed: 987654321, bits_per_value: 32, msb_first: 1 },
    7: { bits_per_value: 32, msb_first: 1 },
    11: { seed: 987654321, r: 48, s: 20, base: 4294967296, bits_per_value: 32, msb_first: 1 },
    16: { seed: 987654321, p: 1009, q: 2003, bits_per_value: 1, msb_first: 1 }, // Większe liczby pierwsze
    23: { bits_per_value: 32, msb_first: 1 },
    24: { bits_per_value: 32, msb_first: 1 },
  },
} as const;

// Definiowanie scenariuszy testowych (liczba próbek + parametry)
const TEST_SCENARIOS = {
  worst: {
    name: "Najgorszy scenariusz",
    icon: TrendingDown,
    description: "Minimalna liczba próbek (1,000) + słabe parametry",
    samples: 1000,
    color: "text-red-500",
    getParams: (rngId: number) => SCENARIO_PARAMS.worst[rngId as keyof typeof SCENARIO_PARAMS.worst] || {},
  },
  medium: {
    name: "Średni scenariusz",
    icon: Activity,
    description: "Zrównoważona liczba próbek (100,000) + standardowe parametry",
    samples: 100000,
    color: "text-yellow-500",
    getParams: (rngId: number) => SCENARIO_PARAMS.medium[rngId as keyof typeof SCENARIO_PARAMS.medium] || {},
  },
  best: {
    name: "Najlepszy scenariusz",
    icon: TrendingUp,
    description: "Wysoka liczba próbek (1,000,000) + optymalne parametry",
    samples: 1000000,
    color: "text-green-500",
    getParams: (rngId: number) => SCENARIO_PARAMS.best[rngId as keyof typeof SCENARIO_PARAMS.best] || {},
  },
} as const;

type ScenarioType = keyof typeof TEST_SCENARIOS;

interface TestResult {
  test_name: string;
  passed: boolean;
  score: number;
  duration: number;
}

interface GeneratorResults {
  rng_id: string;
  rng_name: string;
  scenario: ScenarioType;
  results: TestResult[];
  totalTests: number;
  passedTests: number;
  failedTests: number;
  totalDuration: number;
  avgScore: number;
}

const comparisonFormSchema = z.object({
  rng1_id: z.string().min(1, "Wybierz pierwszy generator"),
  rng1_scenario: z.enum(["worst", "medium", "best"], {
    message: "Wybierz scenariusz dla pierwszego generatora",
  }),
  rng2_id: z.string().min(1, "Wybierz drugi generator"),
  rng2_scenario: z.enum(["worst", "medium", "best"], {
    message: "Wybierz scenariusz dla drugiego generatora",
  }),
  test_count: z.enum(["3", "6", "9"], {
    message: "Wybierz liczbę testów",
  }),
});

type ComparisonFormValues = z.infer<typeof comparisonFormSchema>;

export const ComparisonTests = () => {
  const [rngs, setRngs] = useState<RNG[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [totalTests, setTotalTests] = useState(0);
  const [comparisonResults, setComparisonResults] = useState<{
    generator1: GeneratorResults | null;
    generator2: GeneratorResults | null;
  }>({ generator1: null, generator2: null });

  const form = useForm<ComparisonFormValues>({
    resolver: zodResolver(comparisonFormSchema),
    defaultValues: {
      rng1_id: "",
      rng1_scenario: "medium",
      rng2_id: "",
      rng2_scenario: "medium",
      test_count: "6",
    },
  });

  useEffect(() => {
    const fetchRngs = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/rngs");
        if (!response.ok) throw new Error("Nie udało się pobrać generatorów RNG");
        const data = await response.json();
        setRngs(data.filter((rng: RNG) => rng.is_active));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Nieznany błąd");
        toast.error("Nie udało się załadować algorytmów RNG");
      } finally {
        setLoading(false);
      }
    };

    fetchRngs();
  }, []);

  const runTestForGenerator = async (
    rngId: string,
    scenario: ScenarioType,
    testsToRun: string[]
  ): Promise<GeneratorResults> => {
    const scenarioConfig = TEST_SCENARIOS[scenario];
    const results: TestResult[] = [];
    
    const rng = rngs.find((r) => r.id.toString() === rngId);
    const rngName = rng?.name || "Unknown";
    
    // Pobierz parametry dla tego scenariusza i algorytmu
    const rngIdNum = parseInt(rngId);
    const parameters = scenarioConfig.getParams(rngIdNum);

    for (const testName of testsToRun) {
      const startTime = Date.now();
      
      try {
        const response = await fetch(
          `http://localhost:8000/api/rngs/${rngId}/run_test?compressed=true`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              test_name: testName,
              samples_count: scenarioConfig.samples,
              parameters: parameters,
            }),
          }
        );

        if (!response.ok) {
          throw new Error("Wykonanie testu nie powiodło się");
        }

        const result = await response.json();
        const duration = (Date.now() - startTime) / 1000;

        results.push({
          test_name: testName,
          passed: result.passed,
          score: result.score,
          duration,
        });

        setCurrentProgress((prev) => prev + 1);
      } catch (error) {
        console.error(`Test ${testName} failed:`, error);
        results.push({
          test_name: testName,
          passed: false,
          score: 0,
          duration: (Date.now() - startTime) / 1000,
        });
        setCurrentProgress((prev) => prev + 1);
      }
    }

    const passedTests = results.filter((r) => r.passed).length;
    const totalDuration = results.reduce((sum, r) => sum + r.duration, 0);
    const avgScore =
      results.reduce((sum, r) => sum + r.score, 0) / results.length;

    return {
      rng_id: rngId,
      rng_name: rngName,
      scenario,
      results,
      totalTests: results.length,
      passedTests,
      failedTests: results.length - passedTests,
      totalDuration,
      avgScore,
    };
  };

  const onSubmit = async (values: ComparisonFormValues) => {
    setIsRunning(true);
    setCurrentProgress(0);
    setComparisonResults({ generator1: null, generator2: null });

    // Wybierz testy do uruchomienia na podstawie wybranej liczby
    const testCount = parseInt(values.test_count);
    const testsToRun = ALL_NIST_TESTS.slice(0, testCount);
    
    // Ustaw całkowitą liczbę testów (test_count * 2 generatory)
    setTotalTests(testCount * 2);

    try {
      toast.info("Rozpoczęcie testów porównawczych...");

      // Uruchom testy dla pierwszego generatora
      const results1 = await runTestForGenerator(
        values.rng1_id,
        values.rng1_scenario,
        testsToRun as unknown as string[]
      );

      // Uruchom testy dla drugiego generatora
      const results2 = await runTestForGenerator(
        values.rng2_id,
        values.rng2_scenario,
        testsToRun as unknown as string[]
      );

      setComparisonResults({
        generator1: results1,
        generator2: results2,
      });

      toast.success("Testy porównawcze zakończone!");
    } catch (error) {
      toast.error("Błąd podczas wykonywania testów");
      console.error(error);
    } finally {
      setIsRunning(false);
    }
  };

  const formatTestName = (name: string) => {
    return name
      .replace("nist_", "NIST: ")
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const getWinner = () => {
    if (!comparisonResults.generator1 || !comparisonResults.generator2) {
      return null;
    }

    const gen1 = comparisonResults.generator1;
    const gen2 = comparisonResults.generator2;

    const gen1PassRate = (gen1.passedTests / gen1.totalTests) * 100;
    const gen2PassRate = (gen2.passedTests / gen2.totalTests) * 100;

    if (gen1PassRate > gen2PassRate) return "generator1";
    if (gen2PassRate > gen1PassRate) return "generator2";
    
    // Jeśli równy wskaźnik zdawalności, porównaj średni wynik
    if (gen1.avgScore > gen2.avgScore) return "generator1";
    if (gen2.avgScore > gen1.avgScore) return "generator2";
    
    return "tie";
  };

  if (loading) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <Loading message="Ładowanie testów..." fullScreen />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <ErrorComponent description={error} />
      </div>
    );
  }

  const winner = getWinner();

  return (
    <div className="container mx-auto p-8 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <GitCompare className="h-8 w-8" />
          Testy Porównawcze RNG
        </h1>
        <p className="text-muted-foreground">
          Porównaj wydajność dwóch generatorów liczb losowych w różnych scenariuszach
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Formularz konfiguracji */}
        <Card>
          <CardHeader>
            <CardTitle>Konfiguracja Testów</CardTitle>
            <CardDescription>
              Wybierz dwa generatory i scenariusze testowe dla porównania
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                {/* Generator 1 */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Generator 1</h3>
                  <FormField
                    control={form.control}
                    name="rng1_id"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Algorytm RNG</FormLabel>
                        <Select
                          onValueChange={field.onChange}
                          value={field.value}
                          disabled={isRunning}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Wybierz generator">
                                {field.value &&
                                  rngs.find((rng) => rng.id.toString() === field.value)
                                    ?.name}
                              </SelectValue>
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {rngs.map((rng) => (
                              <SelectItem key={rng.id} value={rng.id.toString()}>
                                <div className="flex flex-col">
                                  <span className="font-medium">{rng.name}</span>
                                  <span className="text-xs text-muted-foreground">
                                    {rng.description}
                                  </span>
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="rng1_scenario"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Scenariusz Testowy</FormLabel>
                        <Select
                          onValueChange={field.onChange}
                          value={field.value}
                          disabled={isRunning}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Wybierz scenariusz" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {Object.entries(TEST_SCENARIOS).map(([key, scenario]) => {
                              const Icon = scenario.icon;
                              return (
                                <SelectItem key={key} value={key}>
                                  <div className="flex items-start gap-3">
                                    <Icon className={`h-5 w-5 mt-0.5 ${scenario.color}`} />
                                    <div className="flex flex-col">
                                       <span className="font-medium">{scenario.name}</span>
                                       <span className="text-xs text-muted-foreground">
                                         {scenario.description}
                                       </span>
                                     </div>
                                   </div>
                                 </SelectItem>
                               );
                             })}
                           </SelectContent>
                         </Select>
                         <FormMessage />
                       </FormItem>
                     )}
                   />
                 </div>

                 <Separator />

                 {/* Generator 2 */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Generator 2</h3>
                  <FormField
                    control={form.control}
                    name="rng2_id"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Algorytm RNG</FormLabel>
                        <Select
                          onValueChange={field.onChange}
                          value={field.value}
                          disabled={isRunning}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Wybierz generator">
                                {field.value &&
                                  rngs.find((rng) => rng.id.toString() === field.value)
                                    ?.name}
                              </SelectValue>
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {rngs.map((rng) => (
                              <SelectItem key={rng.id} value={rng.id.toString()}>
                                <div className="flex flex-col">
                                  <span className="font-medium">{rng.name}</span>
                                  <span className="text-xs text-muted-foreground">
                                    {rng.description}
                                  </span>
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="rng2_scenario"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Scenariusz Testowy</FormLabel>
                        <Select
                          onValueChange={field.onChange}
                          value={field.value}
                          disabled={isRunning}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Wybierz scenariusz" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {Object.entries(TEST_SCENARIOS).map(([key, scenario]) => {
                              const Icon = scenario.icon;
                              return (
                                <SelectItem key={key} value={key}>
                                  <div className="flex items-start gap-3">
                                    <Icon className={`h-5 w-5 mt-0.5 ${scenario.color}`} />
                                    <div className="flex flex-col">
                                       <span className="font-medium">{scenario.name}</span>
                                       <span className="text-xs text-muted-foreground">
                                         {scenario.description}
                                       </span>
                                     </div>
                                   </div>
                                 </SelectItem>
                               );
                             })}
                           </SelectContent>
                         </Select>
                         <FormMessage />
                       </FormItem>
                     )}
                   />
                 </div>

                 <Separator />

                 {/* Wybór liczby testów */}
                 <FormField
                   control={form.control}
                   name="test_count"
                   render={({ field }) => (
                     <FormItem>
                       <FormLabel>Liczba testów do wykonania</FormLabel>
                       <Select
                         onValueChange={field.onChange}
                         value={field.value}
                         disabled={isRunning}
                       >
                         <FormControl>
                           <SelectTrigger>
                             <SelectValue placeholder="Wybierz liczbę testów" />
                           </SelectTrigger>
                         </FormControl>
                         <SelectContent>
                           <SelectItem value="3">
                             <div className="flex flex-col">
                               <span className="font-medium">3 testy</span>
                               <span className="text-xs text-muted-foreground">
                                 Szybkie porównanie (około 5-10s)
                               </span>
                             </div>
                           </SelectItem>
                           <SelectItem value="6">
                             <div className="flex flex-col">
                               <span className="font-medium">6 testów</span>
                               <span className="text-xs text-muted-foreground">
                                 Zrównoważone porównanie (około 15-30s)
                               </span>
                             </div>
                           </SelectItem>
                           <SelectItem value="9">
                             <div className="flex flex-col">
                               <span className="font-medium">9 testów</span>
                               <span className="text-xs text-muted-foreground">
                                 Kompleksowe porównanie (około 30-60s)
                               </span>
                             </div>
                           </SelectItem>
                         </SelectContent>
                       </Select>
                       <FormMessage />
                     </FormItem>
                   )}
                 />

                 <Button
                  type="submit"
                  className="w-full"
                  disabled={isRunning}
                  size="lg"
                >
                  {isRunning ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Wykonywanie testów...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-5 w-5" />
                      Uruchom Testy Porównawcze
                    </>
                  )}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>

        {/* Panel statusu/wyników */}
        <div className="space-y-6">
          {isRunning && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Trwa wykonywanie testów
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Postęp</span>
                    <span>
                      {currentProgress} / {totalTests} testów
                    </span>
                  </div>
                  <Progress value={(currentProgress / totalTests) * 100} />
                </div>
              </CardContent>
            </Card>
          )}

          {comparisonResults.generator1 && comparisonResults.generator2 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="h-5 w-5 text-yellow-500" />
                  Podsumowanie Porównania
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {winner && winner !== "tie" && (
                  <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                    <div className="flex items-center gap-2 text-yellow-600 dark:text-yellow-400 font-semibold">
                      <Trophy className="h-5 w-5" />
                      Zwycięzca: {winner === "generator1" 
                        ? comparisonResults.generator1.rng_name 
                        : comparisonResults.generator2.rng_name}
                    </div>
                  </div>
                )}
                
                {winner === "tie" && (
                  <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-semibold">
                      <BarChart3 className="h-5 w-5" />
                      Remis - oba generatory pokazały podobną wydajność
                    </div>
                  </div>
                )}

                {/* Szybkie statystyki */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h4 className="font-semibold text-sm">
                      {comparisonResults.generator1.rng_name}
                    </h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Zdane:</span>
                        <span className="font-medium text-green-600">
                          {comparisonResults.generator1.passedTests} /{" "}
                          {comparisonResults.generator1.totalTests}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Śr. wynik:</span>
                        <span className="font-medium">
                          {comparisonResults.generator1.avgScore.toFixed(4)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Czas:</span>
                        <span className="font-medium">
                          {comparisonResults.generator1.totalDuration.toFixed(2)}s
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-semibold text-sm">
                      {comparisonResults.generator2.rng_name}
                    </h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Zdane:</span>
                        <span className="font-medium text-green-600">
                          {comparisonResults.generator2.passedTests} /{" "}
                          {comparisonResults.generator2.totalTests}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Śr. wynik:</span>
                        <span className="font-medium">
                          {comparisonResults.generator2.avgScore.toFixed(4)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Czas:</span>
                        <span className="font-medium">
                          {comparisonResults.generator2.totalDuration.toFixed(2)}s
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Szczegółowe wyniki */}
      {comparisonResults.generator1 && comparisonResults.generator2 && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Szczegółowe Wyniki</CardTitle>
            <CardDescription>
              Porównanie wyników poszczególnych testów dla obu generatorów
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="generator1" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="generator1">
                  {comparisonResults.generator1.rng_name}
                </TabsTrigger>
                <TabsTrigger value="generator2">
                  {comparisonResults.generator2.rng_name}
                </TabsTrigger>
              </TabsList>

              <TabsContent value="generator1" className="space-y-4 mt-4">
                <div className="flex items-center gap-4 mb-4">
                  <Badge variant="outline" className="text-base">
                    Scenariusz: {TEST_SCENARIOS[comparisonResults.generator1.scenario].name}
                  </Badge>
                  <Badge variant="outline" className="text-base">
                    Próbek: {TEST_SCENARIOS[comparisonResults.generator1.scenario].samples.toLocaleString()}
                  </Badge>
                </div>
                <div className="space-y-2">
                  {comparisonResults.generator1.results.map((result, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 rounded-md bg-muted/50 hover:bg-muted transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        {result.passed ? (
                          <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" />
                        ) : (
                          <XCircle className="h-5 w-5 text-destructive shrink-0" />
                        )}
                        <div className="flex flex-col">
                          <span className="text-sm font-medium">
                            {formatTestName(result.test_name)}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            Wynik: {result.score.toFixed(4)}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">
                          {result.duration.toFixed(2)}s
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="generator2" className="space-y-4 mt-4">
                <div className="flex items-center gap-4 mb-4">
                  <Badge variant="outline" className="text-base">
                    Scenariusz: {TEST_SCENARIOS[comparisonResults.generator2.scenario].name}
                  </Badge>
                  <Badge variant="outline" className="text-base">
                    Próbek: {TEST_SCENARIOS[comparisonResults.generator2.scenario].samples.toLocaleString()}
                  </Badge>
                </div>
                <div className="space-y-2">
                  {comparisonResults.generator2.results.map((result, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 rounded-md bg-muted/50 hover:bg-muted transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        {result.passed ? (
                          <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" />
                        ) : (
                          <XCircle className="h-5 w-5 text-destructive shrink-0" />
                        )}
                        <div className="flex flex-col">
                          <span className="text-sm font-medium">
                            {formatTestName(result.test_name)}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            Wynik: {result.score.toFixed(4)}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">
                          {result.duration.toFixed(2)}s
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
