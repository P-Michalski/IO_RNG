import { useState, useEffect, useRef } from "react";
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
  FormDescription,
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
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import { type RNG } from "@/types/test-results";
import {
  FlaskConical,
  Loader2,
  Sparkles,
  AlertCircle,
  Plus,
  X,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  XCircle,
  Clock,
} from "lucide-react";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { Loading } from "../Loading/loading";
import { Error as ErrorComponent } from "../Error/error";
import {
  extractBitsFromResponse,
  compressBitsToBase64,
} from "@/utils/compression";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useTestStore, type TestFormValues } from "@/stores/test-store";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Link } from "react-router-dom";
import {
  ALGORITHM_PARAMS,
  type AlgorithmId,
} from "../Generator/generator-form";
import { Separator } from "@/components/ui/separator";

const NIST_TESTS = [
  {
    id: "nist_monobit",
    name: "Monobit Test",
    description: "Checks balance of 0s and 1s",
  },
  {
    id: "nist_block_frequency",
    name: "Block Frequency",
    description: "Checks local balance in blocks",
  },
  {
    id: "nist_runs",
    name: "Runs Test",
    description: "Checks number of transitions",
  },
  {
    id: "nist_longest_run",
    name: "Longest Run",
    description: "Checks longest sequences of 1s",
  },
  {
    id: "nist_matrix_rank",
    name: "Binary Matrix Rank",
    description: "Checks linear independence",
  },
  {
    id: "nist_dft",
    name: "Spectral (DFT)",
    description: "Detects periodic patterns",
  },
  {
    id: "nist_non_overlapping_template",
    name: "Non-Overlapping Template",
    description: "Searches for specific patterns",
  },
  {
    id: "nist_overlapping_template",
    name: "Overlapping Template",
    description: "Searches for overlapping 111...1 patterns",
  },
  {
    id: "nist_universal",
    name: "Maurer's Universal",
    description: "Measures compressibility",
  },
  {
    id: "nist_linear_complexity",
    name: "Linear Complexity",
    description: "Measures LFSR complexity (Berlekamp-Massey)",
  },
  {
    id: "nist_serial",
    name: "Serial Test",
    description: "Checks m-bit pattern frequencies",
  },
  {
    id: "nist_approximate_entropy",
    name: "Approximate Entropy",
    description: "Measures pattern predictability",
  },
  {
    id: "nist_cumulative_sums",
    name: "Cumulative Sums",
    description: "Checks systematic bias",
  },
  {
    id: "nist_random_excursions",
    name: "Random Excursions",
    description: "Analyzes random walk cycles",
  },
  {
    id: "nist_random_excursions_variant",
    name: "Random Excursions Variant",
    description: "Random walk with more states",
  },
] as const;

const DIEHARD_TESTS = [
  {
    id: "diehard_birthday_spacings",
    name: "Birthday Spacings",
    description: "Tests spacing between birthday collisions",
    minSamples: 2_097_152,
  },
  {
    id: "diehard_overlapping_permutations",
    name: "Overlapping Permutations",
    description: "Analyzes overlapping 5-letter word sequences",
    minSamples: 1_048_576,
  },
  {
    id: "diehard_binary_rank",
    name: "Binary Rank",
    description: "Tests rank of binary matrices",
    minSamples: 10_240,
  },
  {
    id: "diehard_bitstream",
    name: "Bitstream",
    description: "Checks overlapping 20-bit words",
    minSamples: 2_097_152,
  },
  {
    id: "diehard_opso",
    name: "OPSO (Overlapping-Pairs-Sparse-Occupancy)",
    description: "Tests sparse occupancy of word pairs",
    minSamples: 2_097_152,
  },
] as const;

const testFormSchema = z
  .object({
    input_type: z.enum(["algorithm", "custom_bits"], {
      message: "Please select input type",
    }),
    rng_id: z.string().optional(),
    custom_bits: z.string().optional(),
    test_type: z.enum(["single", "nist_suite", "diehard_suite"], {
      message: "Please select a test type",
    }),
    single_test: z.enum(["frequency_test", "uniformity_test"]).optional(),
    nist_tests: z.array(z.string()).optional(),
    diehard_tests: z.array(z.string()).optional(),
    samples_count: z
      .number()
      .min(100, "Minimum 100 samples")
      .max(10000000, "Maximum 10M samples"),
    seed: z.number().int().min(0, "Seed must be positive"),
  })
  .refine(
    (data) => {
      if (data.input_type === "algorithm") {
        return !!data.rng_id && data.rng_id.length > 0;
      }
      if (data.input_type === "custom_bits") {
        const bitCount = data.custom_bits?.replace(/\s/g, "").length || 0;
        return bitCount >= 100;
      }
      return false;
    },
    {
      message: "Please select an RNG or provide custom bits",
      path: ["rng_id"],
    }
  )
  .refine(
    (data) => {
      if (data.test_type === "single") {
        return !!data.single_test;
      }
      if (data.test_type === "nist_suite") {
        return data.nist_tests && data.nist_tests.length > 0;
      }
      if (data.test_type === "diehard_suite") {
        return data.diehard_tests && data.diehard_tests.length > 0;
      }
      return false;
    },
    {
      message: "Please select at least one test",
      path: ["nist_tests"],
    }
  );

export const Tests = () => {
  const [rngs, setRngs] = useState<RNG[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showResultsDialog, setShowResultsDialog] = useState(false);

  const [editingTabId, setEditingTabId] = useState<string | null>(null);
  const [editingTabName, setEditingTabName] = useState("");

  const shownDialogsRef = useRef<Set<string>>(new Set());
  const activeTabRef = useRef<HTMLButtonElement>(null);
  const editInputRef = useRef<HTMLInputElement>(null);

  const {
    sessions: testSessions,
    activeTab,
    setActiveTab,
    addSession,
    removeSession,
    updateSessionConfig,
    addTestResult,
    setSessionStatus,
    incrementCurrentTest,
    markResultsSeen,
  } = useTestStore();

  const activeSession = testSessions.find((s) => s.id === activeTab);

  const form = useForm<TestFormValues>({
    resolver: zodResolver(testFormSchema),
    defaultValues: activeSession?.config || {
      input_type: "algorithm",
      rng_id: "",
      custom_bits: "",
      test_type: "single",
      single_test: "frequency_test",
      nist_tests: [],
      diehard_tests: [],
      samples_count: 100000,
      seed: 42,
      algorithm_params: {},
      advanced_params: {},
      use_defaults: true,
    },
  });

  const previousTabRef = useRef<string>(activeTab);

  // State for algorithm parameters
  const [algorithmParams, setAlgorithmParams] = useState<Record<string, any>>(
    activeSession?.config?.algorithm_params || {}
  );
  const [advancedParams, setAdvancedParams] = useState<Record<string, any>>(
    activeSession?.config?.advanced_params || {}
  );
  const [useDefaults, setUseDefaults] = useState(
    activeSession?.config?.use_defaults ?? true
  );

  useEffect(() => {
    // Only reset if we actually switched tabs AND activeSession exists
    if (previousTabRef.current !== activeTab && activeSession) {
      // Use setTimeout to ensure form resets AFTER React finishes rendering
      requestAnimationFrame(() => {
        form.reset(activeSession.config, {
          keepDefaultValues: false,
        });
        // Also reset params state
        setAlgorithmParams(activeSession.config.algorithm_params || {});
        setAdvancedParams(activeSession.config.advanced_params || {});
        setUseDefaults(activeSession.config.use_defaults ?? true);
      });
      previousTabRef.current = activeTab;
    }
  }, [activeTab, activeSession]);

  const testType = form?.watch("test_type");
  const samplesCount = form?.watch("samples_count");
  const inputType = form?.watch("input_type");
  const customBits = form?.watch("custom_bits");
  const rngId = form?.watch("rng_id");

  const customBitCount = customBits?.replace(/\s/g, "").length || 0;

  // Load algorithm parameters when RNG changes
  useEffect(() => {
    if (rngId && inputType === "algorithm") {
      const selectedRng = rngs.find((rng) => rng.id.toString() === rngId);
      if (selectedRng && selectedRng.id in ALGORITHM_PARAMS) {
        const algoId = selectedRng.id as AlgorithmId;
        const algoConfig = ALGORITHM_PARAMS[algoId];

        // Always load fresh parameters for the selected algorithm
        setAlgorithmParams({ ...algoConfig.params });
        setAdvancedParams({ ...algoConfig.defaults });
      } else {
        setAlgorithmParams({});
        setAdvancedParams({});
      }
    } else if (inputType === "custom_bits") {
      // Clear params when switching to custom bits
      setAlgorithmParams({});
      setAdvancedParams({});
    }
  }, [rngId, inputType, rngs]);

  // Focus edit input when editing starts
  useEffect(() => {
    if (editingTabId && editInputRef.current) {
      editInputRef.current.focus();
      editInputRef.current.select();
    }
  }, [editingTabId]);

  useEffect(() => {
    // Scroll to active tab when it changes
    if (activeTabRef.current) {
      activeTabRef.current.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
        inline: "center",
      });
    }
  }, [activeTab]);

  useEffect(() => {
    const fetchRngs = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/rngs");
        if (!response.ok) throw new Error("Failed to fetch RNGs");
        const data = await response.json();
        setRngs(data.filter((rng: RNG) => rng.is_active));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
        toast.error("Failed to load RNG algorithms");
      } finally {
        setLoading(false);
      }
    };

    fetchRngs();
  }, []);

  useEffect(() => {
    const session = testSessions.find((s) => s.id === activeTab);

    if (
      session &&
      (session.status === "completed" ||
        session.status === "error" ||
        session.status === "cancelled") &&
      !session.resultsSeen &&
      !shownDialogsRef.current.has(`${session.id}-${session.endTime}`)
    ) {
      setShowResultsDialog(true);
      if (session.endTime) {
        shownDialogsRef.current.add(`${session.id}-${session.endTime}`);
      }
    }
  }, [activeTab, testSessions]);

  // Clean up old entries from shownDialogsRef when sessions are removed
  useEffect(() => {
    const currentSessionIds = new Set(testSessions.map((s) => s.id));
    const toRemove: string[] = [];

    shownDialogsRef.current.forEach((key) => {
      const sessionId = key.split("-")[0];
      if (!currentSessionIds.has(sessionId)) {
        toRemove.push(key);
      }
    });

    toRemove.forEach((key) => shownDialogsRef.current.delete(key));
  }, [testSessions]);

  // Debounced save form values to store
  useEffect(() => {
    const handler = setTimeout(() => {
      if (activeSession) {
        const values = form.getValues();
        updateSessionConfig(activeTab, {
          ...values,
          algorithm_params: algorithmParams,
          advanced_params: advancedParams,
          use_defaults: useDefaults,
        });
      }
    }, 500);

    return () => clearTimeout(handler);
  }, [
    inputType,
    testType,
    samplesCount,
    customBits,
    form.watch("rng_id"),
    form.watch("single_test"),
    form.watch("nist_tests"),
    form.watch("diehard_tests"),
    form.watch("seed"),
    algorithmParams,
    advancedParams,
    useDefaults,
    activeTab,
    activeSession,
    updateSessionConfig,
  ]);

  const navigateTab = (direction: "prev" | "next") => {
    // Save current form data before switching
    const currentFormData = form.getValues();
    updateSessionConfig(activeTab, currentFormData);

    const currentIndex = testSessions.findIndex((s) => s.id === activeTab);
    if (direction === "prev" && currentIndex > 0) {
      setActiveTab(testSessions[currentIndex - 1].id);
    } else if (direction === "next" && currentIndex < testSessions.length - 1) {
      setActiveTab(testSessions[currentIndex + 1].id);
    }
  };

  const addNewTestSession = () => {
    // Save current tab's form data before creating new tab
    const currentFormData = form.getValues();
    updateSessionConfig(activeTab, currentFormData);

    addSession();
  };

  const removeTestSession = (id: string) => {
    if (testSessions.length === 1) {
      toast.error("Cannot remove the last test session");
      return;
    }

    // Remove session from store
    removeSession(id);
  };

  const handleDialogAction = () => {
    markResultsSeen(activeTab);
    setShowResultsDialog(false);
  };

  const handleTabDoubleClick = (sessionId: string, currentName: string) => {
    setEditingTabId(sessionId);
    setEditingTabName(currentName);
  };

  const handleTabNameSubmit = () => {
    if (editingTabId && editingTabName.trim()) {
      useTestStore.getState().updateSession(editingTabId, {
        name: editingTabName.trim(),
      });
    }
    setEditingTabId(null);
    setEditingTabName("");
  };

  const handleTabNameKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleTabNameSubmit();
    } else if (e.key === "Escape") {
      setEditingTabId(null);
      setEditingTabName("");
    }
  };

  const onSubmit = async (values: TestFormValues) => {
    const session = testSessions.find((s) => s.id === activeTab);
    if (!session) return;

    let totalTests = 0;
    if (values.test_type === "single") {
      totalTests = 1;
    } else if (values.test_type === "nist_suite") {
      totalTests = values.nist_tests?.length || 0;
    } else if (values.test_type === "diehard_suite") {
      totalTests = values.diehard_tests?.length || 0;
    }

    setSessionStatus(activeTab, "running", {
      startTime: Date.now(),
      currentTest: 0,
      totalTests,
      results: [],
    });

    try {
      if (values.test_type === "single" && values.single_test) {
        await runSingleTest(values, values.single_test, activeTab);
      } else if (values.test_type === "nist_suite" && values.nist_tests) {
        for (let i = 0; i < values.nist_tests.length; i++) {
          await runSingleTest(values, values.nist_tests[i], activeTab);
          incrementCurrentTest(activeTab);
        }
      } else if (values.test_type === "diehard_suite" && values.diehard_tests) {
        for (let i = 0; i < values.diehard_tests.length; i++) {
          await runSingleTest(values, values.diehard_tests[i], activeTab);
          incrementCurrentTest(activeTab);
        }
      }

      setSessionStatus(activeTab, "completed", { endTime: Date.now() });

      const updatedSession = useTestStore
        .getState()
        .sessions.find((s) => s.id === activeTab);

      if (updatedSession) {
        const passed = updatedSession.results.filter((r) => r.passed).length;
        const failed = updatedSession.results.filter((r) => !r.passed).length;

        toast.success("Tests Completed", {
          description: `Passed: ${passed}, Failed: ${failed}`,
        });
      }
    } catch (error) {
      // Check if cancelled
      if (error instanceof Error && error.message === "Test cancelled") {
        // Status is already set to "cancelled" by cancelSession
        toast.info("Tests cancelled");
        return;
      }

      setSessionStatus(activeTab, "error", { endTime: Date.now() });
      toast.error("Error", {
        description:
          error instanceof Error ? error.message : "Failed to run tests",
      });
    }
  };

  const cancelTests = () => {
    const { cancelSession } = useTestStore.getState();
    cancelSession(activeTab);
    toast.info("Tests cancelled");
  };

  const runSingleTest = async (
    values: TestFormValues,
    testName: string,
    sessionId: string
  ) => {
    const startTime = Date.now();
    let result;

    // Get AbortController from session
    const session = useTestStore
      .getState()
      .sessions.find((s) => s.id === sessionId);
    const signal = session?.abortController?.signal;

    try {
      if (values.input_type === "custom_bits") {
        const bitsString = values.custom_bits!.replace(/\s/g, "");
        const bits = bitsString.split("").map((bit) => {
          const parsed = parseInt(bit);
          if (parsed !== 0 && parsed !== 1) {
            throw new Error("Custom bits must contain only 0s and 1s");
          }
          return parsed;
        });

        if (bits.length === 0) {
          throw new Error("No valid bits provided");
        }

        const bitsCompressed = compressBitsToBase64(bits);

        const response = await fetch(
          `http://localhost:8000/api/rngs/test-custom`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              bits_compressed: bitsCompressed,
              bits_count: bits.length,
              test_name: testName,
            }),
            signal, // Dodaj signal do fetch
          }
        );

        if (!response.ok) {
          throw new Error("Test execution failed");
        }

        result = await response.json();
      } else {
        const response = await fetch(
          `http://localhost:8000/api/rngs/${values.rng_id}/run_test?compressed=true`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              test_name: testName,
              samples_count: values.samples_count,
              seed: values.seed,
              parameters: {
                ...values.algorithm_params,
                ...values.advanced_params,
              },
            }),
            signal,
          }
        );

        if (!response.ok) {
          throw new Error("Test execution failed");
        }

        result = await response.json();

        if (result.generated_bits || result.bits_compressed) {
          const bits = extractBitsFromResponse(result);
          result.generated_bits = bits;
        }
      }

      const duration = (Date.now() - startTime) / 1000;

      // Add result to session
      addTestResult(sessionId, {
        test_name: testName,
        duration,
        passed: result.passed,
        score: result.score,
      });

      return result;
    } catch (error) {
      // Check if error is due to abort
      if (error instanceof Error && error.name === "AbortError") {
        throw new Error("Test cancelled");
      }
      throw error;
    }
  };

  const formatTestName = (name: string) => {
    const nistTest = NIST_TESTS.find((t) => t.id === name);
    if (nistTest) return nistTest.name;

    const diehardTest = DIEHARD_TESTS.find((t) => t.id === name);
    if (diehardTest) return diehardTest.name;

    return name
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const formatElapsedTime = (startTime: number) => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  if (loading) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <Loading message="Loading Tests..." fullScreen />
      </div>
    );
  }

  if (error)
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <ErrorComponent description={error} />
      </div>
    );

  const completedSession = activeSession;
  const passedCount =
    completedSession?.results.filter((r) => r.passed).length || 0;
  const failedCount =
    completedSession?.results.filter((r) => !r.passed).length || 0;
  const totalTime =
    completedSession?.endTime && completedSession?.startTime
      ? (
          (completedSession.endTime - completedSession.startTime) /
          1000
        ).toFixed(2)
      : "0";

  return (
    <div className="container mx-auto p-8 max-w-2xl">
      {/* Results Summary Dialog */}
      <Dialog
        open={showResultsDialog}
        onOpenChange={(open) => {
          if (!open) {
            handleDialogAction();
          }
          setShowResultsDialog(open);
        }}
      >
        <DialogContent className="max-w-2xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {completedSession?.status === "completed" ? (
                <>
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                  Tests Completed
                </>
              ) : completedSession?.status === "cancelled" ? (
                <>
                  <AlertCircle className="h-5 w-5 text-yellow-500" />
                  Tests Cancelled
                </>
              ) : (
                <>
                  <XCircle className="h-5 w-5 text-destructive" />
                  Tests Failed
                </>
              )}
            </DialogTitle>
            <DialogDescription>
              {completedSession?.status === "completed"
                ? `All tests have been executed successfully for ${completedSession?.name}`
                : `Some tests encountered errors for ${completedSession?.name}`}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Summary Stats */}
            <div className="grid grid-cols-3 gap-2 md:gap-4">
              <Card>
                <CardContent className="pt-3 pb-3 px-2 md:pt-6 md:pb-6 md:px-6">
                  {" "}
                  <div className="text-center">
                    <div className="text-lg md:text-2xl font-bold text-green-500">
                      {" "}
                      {passedCount}
                    </div>
                    <div className="text-[10px] md:text-sm text-muted-foreground">
                      Passed
                    </div>{" "}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-3 pb-3 px-2 md:pt-6 md:pb-6 md:px-6">
                  <div className="text-center">
                    <div className="text-lg md:text-2xl font-bold text-destructive">
                      {failedCount}
                    </div>
                    <div className="text-[10px] md:text-sm text-muted-foreground">
                      Failed
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-3 pb-3 px-2 md:pt-6 md:pb-6 md:px-6">
                  <div className="text-center">
                    <div className="text-base md:text-2xl font-bold break-all">
                      {" "}
                      {totalTime}s
                    </div>
                    <div className="text-[10px] md:text-sm text-muted-foreground whitespace-nowrap">
                      {" "}
                      Total Time
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            {/* Test Results List */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Test Results</h4>
              <ScrollArea className="h-[300px] border rounded-md">
                <div className="p-4 space-y-2">
                  {completedSession?.results.map((result, index) => (
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
                            {result.duration.toFixed(2)}s
                          </span>
                        </div>
                      </div>
                      {result.score !== undefined && (
                        <Badge variant="outline" className="ml-2">
                          Score: {result.score.toFixed(4)}
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          </div>

          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button
              variant="outline"
              onClick={handleDialogAction}
              className="w-full sm:w-auto"
            >
              OK
            </Button>
            <Button
              asChild
              onClick={handleDialogAction}
              className="w-full sm:w-auto"
            >
              <Link to="/results">View Results</Link>
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <div className="mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <FlaskConical className="h-8 w-8" />
          Run RNG Tests
        </h1>
        <p className="text-muted-foreground">
          Test your random number generators with statistical tests
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="flex items-center gap-2 mb-4">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                onClick={() => navigateTab("prev")}
                disabled={
                  testSessions.findIndex((s) => s.id === activeTab) === 0
                }
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Previous Tab</TooltipContent>
          </Tooltip>

          <ScrollArea className="flex-1 min-w-0 w-full">
            <TabsList className="inline-flex w-auto">
              {testSessions.map((session) => (
                <TabsTrigger
                  key={session.id}
                  value={session.id}
                  className="relative group"
                  ref={session.id === activeTab ? activeTabRef : null}
                  onDoubleClick={() =>
                    handleTabDoubleClick(session.id, session.name)
                  }
                >
                  {editingTabId === session.id ? (
                    <input
                      ref={editInputRef}
                      type="text"
                      value={editingTabName}
                      onChange={(e) => setEditingTabName(e.target.value)}
                      onBlur={handleTabNameSubmit}
                      onKeyDown={handleTabNameKeyDown}
                      className="bg-transparent border-b border-primary outline-none w-24 px-1"
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <>
                      <span>{session.name}</span>
                      {session.status === "running" && (
                        <Badge
                          variant="secondary"
                          className="ml-2 h-5 w-5 rounded-full p-0 flex items-center justify-center"
                        >
                          <Loader2 className="h-3 w-3 animate-spin" />
                        </Badge>
                      )}
                      {(session.status === "completed" ||
                        session.status === "error") &&
                        !session.resultsSeen && (
                          <Badge
                            variant="secondary"
                            className="ml-2 h-5 w-5 rounded-full p-0 flex items-center justify-center"
                          >
                            {session.status === "completed" ? (
                              <CheckCircle2 className="h-3 w-3 text-green-500" />
                            ) : (
                              <XCircle className="h-3 w-3 text-destructive" />
                            )}
                          </Badge>
                        )}
                      {testSessions.length > 1 && (
                        <span
                          role="button"
                          tabIndex={0}
                          className="ml-2 h-5 w-5 md:opacity-0 md:group-hover:opacity-100 transition-opacity inline-flex items-center justify-center rounded-sm hover:bg-accent hover:text-accent-foreground cursor-pointer"
                          onClick={(e) => {
                            e.stopPropagation();
                            removeTestSession(session.id);
                          }}
                          onKeyDown={(e) => {
                            if (e.key === "Enter" || e.key === " ") {
                              e.stopPropagation();
                              e.preventDefault();
                              removeTestSession(session.id);
                            }
                          }}
                        >
                          <X className="h-3 w-3" />
                        </span>
                      )}
                    </>
                  )}
                </TabsTrigger>
              ))}
            </TabsList>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                onClick={() => navigateTab("next")}
                disabled={
                  testSessions.findIndex((s) => s.id === activeTab) ===
                  testSessions.length - 1
                }
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Next Tab</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" onClick={addNewTestSession}>
                <Plus className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>New Tab</TooltipContent>
          </Tooltip>
        </div>

        {testSessions.map((session) => (
          <TabsContent key={session.id} value={session.id} className="mt-0">
            {session.status === "running" ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Running Tests
                    </div>

                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={cancelTests}
                    >
                      <span className="hidden md:inline">Cancel</span>
                      <X className="h-4 w-4 md:mr-2" />
                    </Button>
                  </CardTitle>
                  <CardDescription>
                    Test {session.currentTest} of {session.totalTests}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Progress</span>
                      <span>
                        {Math.round(
                          (session.currentTest / session.totalTests) * 100
                        )}
                        %
                      </span>
                    </div>
                    <Progress
                      value={(session.currentTest / session.totalTests) * 100}
                    />
                  </div>

                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    <span>
                      Elapsed:{" "}
                      {session.startTime
                        ? formatElapsedTime(session.startTime)
                        : "0:00"}
                    </span>
                  </div>

                  {session.results.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Test Results</h4>
                      <ScrollArea className="h-48 border rounded-md">
                        <div className="p-4 space-y-2">
                          {session.results.map((result, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-2 rounded-md bg-muted/50"
                            >
                              <div className="flex items-center gap-2">
                                {result.passed ? (
                                  <CheckCircle2 className="h-4 w-4 shrink-0 text-green-500" />
                                ) : (
                                  <XCircle className="h-4 w-4 shrink-0 text-destructive" />
                                )}
                                <span className="text-sm font-medium">
                                  {formatTestName(result.test_name)}
                                </span>
                              </div>
                              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                                <span>{result.duration.toFixed(2)}s</span>
                                {result.score !== undefined && (
                                  <Badge variant="outline">
                                    {result.score.toFixed(2)}
                                  </Badge>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                    </div>
                  )}
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>Test Configuration</CardTitle>
                  <CardDescription>
                    Select an RNG algorithm or provide custom bits and configure
                    test parameters
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {/* Only render form if this is the active tab */}
                  {session.id === activeTab && (
                    <Form {...form}>
                      <form
                        onSubmit={form.handleSubmit(onSubmit)}
                        className="space-y-6"
                      >
                        {/* Input Type Selection */}
                        <FormField
                          control={form.control}
                          name="input_type"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Input Type</FormLabel>
                              <Select
                                onValueChange={(value) => {
                                  field.onChange(value);
                                  if (value === "algorithm") {
                                    form.setValue("custom_bits", "");
                                  } else {
                                    form.setValue("rng_id", "");
                                  }
                                }}
                                value={field.value} // Use value instead of defaultValue
                              >
                                <FormControl>
                                  <SelectTrigger>
                                    <SelectValue placeholder="Select input type" />
                                  </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                  <SelectItem value="algorithm">
                                    <div className="flex flex-col">
                                      <span className="font-medium">
                                        Algorithm
                                      </span>
                                      <span className="text-xs text-muted-foreground">
                                        Generate bits from an RNG
                                      </span>
                                    </div>
                                  </SelectItem>
                                  <SelectItem value="custom_bits">
                                    <div className="flex flex-col">
                                      <span className="font-medium">
                                        Custom Bits
                                      </span>
                                      <span className="text-xs text-muted-foreground">
                                        Test your own bit sequence
                                      </span>
                                    </div>
                                  </SelectItem>
                                </SelectContent>
                              </Select>
                              <FormDescription>
                                Choose to use an algorithm or provide custom
                                bits
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        {/* RNG Selection */}
                        {inputType === "algorithm" && (
                          <FormField
                            control={form.control}
                            name="rng_id"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>RNG Algorithm</FormLabel>
                                <Select
                                  onValueChange={field.onChange}
                                  value={field.value}
                                >
                                  <FormControl>
                                    <SelectTrigger>
                                      <SelectValue placeholder="Select an RNG algorithm">
                                        {field.value &&
                                          rngs.find(
                                            (rng) =>
                                              rng.id.toString() === field.value
                                          )?.name}
                                      </SelectValue>
                                    </SelectTrigger>
                                  </FormControl>
                                  <SelectContent>
                                    {rngs.map((rng) => (
                                      <SelectItem
                                        key={rng.id}
                                        value={rng.id.toString()}
                                      >
                                        <div className="flex flex-col">
                                          <span className="font-medium">
                                            {rng.name}
                                          </span>
                                          <span className="text-xs text-muted-foreground">
                                            {rng.description}
                                          </span>
                                        </div>
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                                <FormDescription>
                                  Choose the random number generator to test
                                </FormDescription>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        )}

                        {/* Algorithm Parameters Section */}
                        {inputType === "algorithm" &&
                          rngId &&
                          Object.keys(algorithmParams).length > 0 && (
                            <>
                              <Separator />
                              <div className="space-y-3">
                                <FormLabel>Algorithm Parameters</FormLabel>
                                {Object.entries(algorithmParams).map(
                                  ([key, value]) => (
                                    <div key={key} className="space-y-2">
                                      <FormLabel
                                        htmlFor={`algo-${key}`}
                                        className="text-sm capitalize"
                                      >
                                        {key.replace("_", " ")}
                                      </FormLabel>
                                      <Input
                                        id={`algo-${key}`}
                                        value={value}
                                        onChange={(e) =>
                                          setAlgorithmParams({
                                            ...algorithmParams,
                                            [key]: e.target.value,
                                          })
                                        }
                                      />
                                    </div>
                                  )
                                )}
                              </div>

                              <Separator />

                              <div className="space-y-3">
                                <div className="flex items-center space-x-2">
                                  <Checkbox
                                    id="useDefaults"
                                    checked={useDefaults}
                                    onCheckedChange={(checked) =>
                                      setUseDefaults(checked as boolean)
                                    }
                                  />
                                  <FormLabel
                                    htmlFor="useDefaults"
                                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                                  >
                                    Use default advanced parameters
                                  </FormLabel>
                                </div>

                                <div className="space-y-3">
                                  <FormLabel>Advanced Parameters</FormLabel>
                                  {Object.entries(
                                    useDefaults
                                      ? rngId &&
                                        (parseInt(rngId) as AlgorithmId) in
                                          ALGORITHM_PARAMS
                                        ? ALGORITHM_PARAMS[
                                            parseInt(rngId) as AlgorithmId
                                          ].defaults
                                        : {}
                                      : advancedParams
                                  ).map(([key, value]) => (
                                    <div key={key} className="space-y-2">
                                      <FormLabel
                                        htmlFor={`adv-${key}`}
                                        className="text-sm capitalize"
                                      >
                                        {key.replace("_", " ")}
                                      </FormLabel>
                                      <Input
                                        id={`adv-${key}`}
                                        value={value}
                                        onChange={(e) =>
                                          setAdvancedParams({
                                            ...advancedParams,
                                            [key]: e.target.value,
                                          })
                                        }
                                        disabled={useDefaults}
                                      />
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </>
                          )}

                        {/* Custom Bits Input */}
                        {inputType === "custom_bits" && (
                          <FormField
                            control={form.control}
                            name="custom_bits"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Custom Bits</FormLabel>
                                <FormControl>
                                  <ScrollArea className="h-[200px] w-full rounded-md border">
                                    <Textarea
                                      placeholder="Paste your bit sequence here (e.g., 0101101001...)"
                                      className="font-mono text-sm min-h-[200px] border-0 focus-visible:ring-0 focus-visible:ring-offset-0 resize-none break-all whitespace-pre-wrap"
                                      {...field}
                                      onChange={(e) => {
                                        const sanitized =
                                          e.target.value.replace(
                                            /[^01\s]/g,
                                            ""
                                          );
                                        field.onChange(sanitized);
                                      }}
                                    />
                                  </ScrollArea>
                                </FormControl>
                                <FormDescription>
                                  Enter a sequence of 0s and 1s. Spaces and line
                                  breaks will be ignored.
                                  <span className="block mt-1 font-medium">
                                    Bit count: {customBitCount}
                                    {customBitCount < 100 && (
                                      <span className="text-destructive ml-2">
                                        (minimum 100 required)
                                      </span>
                                    )}
                                  </span>
                                </FormDescription>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        )}

                        {/* Test Type Selection */}
                        <FormField
                          control={form.control}
                          name="test_type"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Test Category</FormLabel>
                              <Select
                                onValueChange={field.onChange}
                                value={field.value}
                              >
                                <FormControl>
                                  <SelectTrigger>
                                    <SelectValue placeholder="Select test category" />
                                  </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                  <SelectItem value="single">
                                    <div className="flex flex-col">
                                      <span className="font-medium">
                                        Single Test
                                      </span>
                                      <span className="text-xs text-muted-foreground">
                                        Run one statistical test
                                      </span>
                                    </div>
                                  </SelectItem>
                                  <SelectItem value="nist_suite">
                                    <div className="flex flex-col">
                                      <span className="font-medium">
                                        NIST Test Suite
                                      </span>
                                      <span className="text-xs text-muted-foreground">
                                        Run multiple NIST tests
                                      </span>
                                    </div>
                                  </SelectItem>
                                  <SelectItem value="diehard_suite">
                                    <div className="flex flex-col">
                                      <span className="font-medium">
                                        Diehard Test Suite
                                      </span>
                                      <span className="text-xs text-muted-foreground">
                                        Run multiple Diehard tests
                                      </span>
                                    </div>
                                  </SelectItem>
                                </SelectContent>
                              </Select>
                              <FormDescription>
                                Choose between single test, NIST test suite, or
                                Diehard test suite
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        {/* Single Test Selection */}
                        {testType === "single" && (
                          <FormField
                            control={form.control}
                            name="single_test"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Test Type</FormLabel>
                                <Select
                                  onValueChange={field.onChange}
                                  value={field.value}
                                >
                                  <FormControl>
                                    <SelectTrigger>
                                      <SelectValue>
                                        {field.value === "frequency_test" &&
                                          "Frequency Test"}
                                        {field.value === "uniformity_test" &&
                                          "Uniformity Test"}
                                      </SelectValue>
                                    </SelectTrigger>
                                  </FormControl>
                                  <SelectContent>
                                    <SelectItem value="frequency_test">
                                      <div className="flex flex-col">
                                        <span className="font-medium">
                                          Frequency Test
                                        </span>
                                        <span className="text-xs text-muted-foreground">
                                          Chi-square goodness of fit test
                                        </span>
                                      </div>
                                    </SelectItem>
                                    <SelectItem value="uniformity_test">
                                      <div className="flex flex-col">
                                        <span className="font-medium">
                                          Uniformity Test
                                        </span>
                                        <span className="text-xs text-muted-foreground">
                                          Mean and variance analysis
                                        </span>
                                      </div>
                                    </SelectItem>
                                  </SelectContent>
                                </Select>
                                <FormDescription>
                                  Select the statistical test to run
                                </FormDescription>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        )}

                        {/* NIST Tests Selection */}
                        {testType === "nist_suite" && (
                          <FormField
                            control={form.control}
                            name="nist_tests"
                            render={() => (
                              <FormItem>
                                <div className="mb-4">
                                  <FormLabel className="text-base">
                                    NIST Tests
                                  </FormLabel>
                                  <FormDescription>
                                    Select which NIST tests to run
                                  </FormDescription>
                                </div>
                                <div className="max-h-96 border rounded-md overflow-hidden">
                                  <ScrollArea className="h-full">
                                    <div className="space-y-3 p-4">
                                      {NIST_TESTS.map((test) => (
                                        <FormField
                                          key={test.id}
                                          control={form.control}
                                          name="nist_tests"
                                          render={({ field }) => {
                                            const isChecked =
                                              field.value?.includes(test.id);
                                            return (
                                              <FormItem key={test.id}>
                                                <label
                                                  htmlFor={test.id}
                                                  className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4 cursor-pointer transition-colors hover:bg-accent/50 has-checked:bg-primary/5 has-checked:border-primary dark:has-checked:bg-primary/10"
                                                >
                                                  <FormControl>
                                                    <Checkbox
                                                      id={test.id}
                                                      checked={isChecked}
                                                      onCheckedChange={(
                                                        checked
                                                      ) => {
                                                        return checked
                                                          ? field.onChange([
                                                              ...(field.value ||
                                                                []),
                                                              test.id,
                                                            ])
                                                          : field.onChange(
                                                              field.value?.filter(
                                                                (value) =>
                                                                  value !==
                                                                  test.id
                                                              )
                                                            );
                                                      }}
                                                    />
                                                  </FormControl>
                                                  <div className="flex-1 space-y-1 leading-none">
                                                    <FormLabel
                                                      htmlFor={test.id}
                                                      className="font-medium cursor-pointer"
                                                    >
                                                      {test.name}
                                                    </FormLabel>
                                                    <FormDescription className="text-xs">
                                                      {test.description}
                                                    </FormDescription>
                                                  </div>
                                                </label>
                                              </FormItem>
                                            );
                                          }}
                                        />
                                      ))}
                                    </div>
                                  </ScrollArea>
                                </div>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        )}

                        {/* Diehard Tests Selection */}
                        {testType === "diehard_suite" && (
                          <FormField
                            control={form.control}
                            name="diehard_tests"
                            render={() => (
                              <FormItem>
                                <div className="mb-4">
                                  <FormLabel className="text-base">
                                    Diehard Tests
                                  </FormLabel>
                                  <FormDescription>
                                    Select which Diehard tests to run (some
                                    tests require minimum bit counts)
                                  </FormDescription>
                                </div>
                                <div className="max-h-96 border rounded-md overflow-hidden">
                                  <ScrollArea className="h-full">
                                    <div className="space-y-3 p-4">
                                      {DIEHARD_TESTS.map((test) => {
                                        const effectiveBitCount =
                                          inputType === "custom_bits"
                                            ? customBitCount
                                            : samplesCount;
                                        const isDisabled =
                                          effectiveBitCount < test.minSamples;
                                        const isChecked = form
                                          .watch("diehard_tests")
                                          ?.includes(test.id);

                                        return (
                                          <FormField
                                            key={test.id}
                                            control={form.control}
                                            name="diehard_tests"
                                            render={({ field }) => {
                                              return (
                                                <FormItem key={test.id}>
                                                  <label
                                                    htmlFor={test.id}
                                                    className={`flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4 transition-colors ${
                                                      isDisabled
                                                        ? "opacity-50 cursor-not-allowed bg-muted/30"
                                                        : "cursor-pointer hover:bg-accent/50 has-checked:bg-primary/5 has-checked:border-primary dark:has-checked:bg-primary/10"
                                                    }`}
                                                  >
                                                    <FormControl>
                                                      <Checkbox
                                                        id={test.id}
                                                        checked={
                                                          isChecked &&
                                                          !isDisabled
                                                        }
                                                        disabled={isDisabled}
                                                        onCheckedChange={(
                                                          checked
                                                        ) => {
                                                          if (isDisabled)
                                                            return;

                                                          return checked
                                                            ? field.onChange([
                                                                ...(field.value ||
                                                                  []),
                                                                test.id,
                                                              ])
                                                            : field.onChange(
                                                                field.value?.filter(
                                                                  (value) =>
                                                                    value !==
                                                                    test.id
                                                                )
                                                              );
                                                        }}
                                                      />
                                                    </FormControl>
                                                    <div className="flex-1 space-y-1 leading-none">
                                                      <FormLabel
                                                        htmlFor={test.id}
                                                        className={`font-medium ${
                                                          isDisabled
                                                            ? "cursor-not-allowed"
                                                            : "cursor-pointer"
                                                        }`}
                                                      >
                                                        {test.name}
                                                      </FormLabel>
                                                      <FormDescription className="text-xs">
                                                        {test.description}
                                                      </FormDescription>
                                                      {isDisabled && (
                                                        <p className="text-xs text-destructive font-medium mt-1 flex items-center gap-1">
                                                          <AlertCircle className="h-3 w-3" />
                                                          Requires minimum{" "}
                                                          {test.minSamples.toLocaleString()}{" "}
                                                          {inputType ===
                                                          "custom_bits"
                                                            ? "bits"
                                                            : "samples"}
                                                        </p>
                                                      )}
                                                    </div>
                                                  </label>
                                                </FormItem>
                                              );
                                            }}
                                          />
                                        );
                                      })}
                                    </div>
                                  </ScrollArea>
                                </div>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        )}

                        {/* Samples Count */}
                        {inputType === "algorithm" && (
                          <FormField
                            control={form.control}
                            name="samples_count"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Samples Count</FormLabel>
                                <FormControl>
                                  <Input
                                    type="number"
                                    placeholder="100000"
                                    value={field.value}
                                    onChange={(e) =>
                                      field.onChange(Number(e.target.value))
                                    }
                                    onBlur={field.onBlur}
                                    name={field.name}
                                    ref={field.ref}
                                  />
                                </FormControl>
                                <FormDescription>
                                  Number of random samples to generate (100 -
                                  10,000,000)
                                </FormDescription>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        )}

                        {/* Seed */}
                        {inputType === "algorithm" && (
                          <FormField
                            control={form.control}
                            name="seed"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Random Seed</FormLabel>
                                <FormControl>
                                  <Input
                                    type="number"
                                    placeholder="42"
                                    value={field.value}
                                    onChange={(e) =>
                                      field.onChange(Number(e.target.value))
                                    }
                                    onBlur={field.onBlur}
                                    name={field.name}
                                    ref={field.ref}
                                  />
                                </FormControl>
                                <FormDescription>
                                  Initial seed value for reproducible results
                                </FormDescription>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        )}

                        {/* Submit Button */}
                        <Button type="submit" className="w-full" size="lg">
                          <Sparkles className="mr-2 h-4 w-4" />
                          Run{" "}
                          {testType === "nist_suite" ||
                          testType === "diehard_suite"
                            ? "Tests"
                            : "Test"}
                        </Button>
                      </form>
                    </Form>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};
