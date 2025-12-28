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
import { FlaskConical, Loader2, Sparkles, AlertCircle } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loading } from "../Loading/loading";
import { Error as ErrorComponent } from "../Error/error";
import {
  extractBitsFromResponse,
  compressBitsToBase64,
} from "@/utils/compression";
import { Textarea } from "@/components/ui/textarea";

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

type TestFormValues = z.infer<typeof testFormSchema>;

export const Tests = () => {
  const [rngs, setRngs] = useState<RNG[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<TestFormValues>({
    resolver: zodResolver(testFormSchema),
    defaultValues: {
      input_type: "algorithm",
      rng_id: "",
      custom_bits: "",
      test_type: "single",
      single_test: "frequency_test",
      nist_tests: [],
      diehard_tests: [],
      samples_count: 100000,
      seed: 42,
    },
  });

  const testType = form.watch("test_type");
  const samplesCount = form.watch("samples_count");
  const inputType = form.watch("input_type");
  const customBits = form.watch("custom_bits");

  const customBitCount = customBits?.replace(/\s/g, "").length || 0;

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

  const onSubmit = async (values: TestFormValues) => {
    setIsSubmitting(true);
    try {
      if (values.test_type === "single" && values.single_test) {
        await runSingleTest(values, values.single_test);
      } else if (values.test_type === "nist_suite" && values.nist_tests) {
        let passed = 0;
        let failed = 0;

        for (const testName of values.nist_tests) {
          const result = await runSingleTest(values, testName);
          if (result.passed) passed++;
          else failed++;
        }

        toast.success("NIST Test Suite Completed", {
          description: `Passed: ${passed}, Failed: ${failed} out of ${values.nist_tests.length} tests`,
        });
      } else if (values.test_type === "diehard_suite" && values.diehard_tests) {
        let passed = 0;
        let failed = 0;

        for (const testName of values.diehard_tests) {
          const result = await runSingleTest(values, testName);
          if (result.passed) passed++;
          else failed++;
        }

        toast.success("Diehard Test Suite Completed", {
          description: `Passed: ${passed}, Failed: ${failed} out of ${values.diehard_tests.length} tests`,
        });
      }
    } catch (error) {
      toast.error("Error", {
        description:
          error instanceof Error ? error.message : "Failed to run tests",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const runSingleTest = async (values: TestFormValues, testName: string) => {
    let result;

    if (values.input_type === "custom_bits") {
      // Parse custom bits
      const bitsString = values.custom_bits!.replace(/\s/g, ""); // Remove whitespace
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

      // Compress bits to base64
      const bitsCompressed = compressBitsToBase64(bits);

      // Call custom bits endpoint
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
        }
      );

      if (!response.ok) {
        throw new Error("Test execution failed");
      }

      result = await response.json();
    } else {
      // Use algorithm endpoint
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
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Test execution failed");
      }

      result = await response.json();

      // Automatically decompress bits if they're in the response
      if (result.generated_bits || result.bits_compressed) {
        const bits = extractBitsFromResponse(result);
        result.generated_bits = bits;
      }
    }

    if (values.test_type === "single") {
      if (result.passed) {
        toast.success("Test Passed! ✓", {
          description: `${formatTestName(
            result.test_name
          )} completed with score: ${result.score.toFixed(2)}`,
        });
      } else {
        toast.error("Test Failed ✗", {
          description: `${formatTestName(
            result.test_name
          )} completed with score: ${result.score.toFixed(2)}`,
        });
      }
    }

    return result;
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

  return (
    <div className="container mx-auto p-8 max-w-2xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <FlaskConical className="h-8 w-8" />
          Run RNG Tests
        </h1>
        <p className="text-muted-foreground">
          Test your random number generators with statistical tests
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Test Configuration</CardTitle>
          <CardDescription>
            Select an RNG algorithm or provide custom bits and configure test
            parameters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
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
                        // Reset related fields when switching input type
                        if (value === "algorithm") {
                          form.setValue("custom_bits", "");
                        } else {
                          form.setValue("rng_id", "");
                        }
                      }}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="algorithm">
                          <div className="flex flex-col">
                            <span className="font-medium">Algorithm</span>
                            <span className="text-xs text-muted-foreground">
                              Generate bits from an RNG
                            </span>
                          </div>
                        </SelectItem>
                        <SelectItem value="custom_bits">
                          <div className="flex flex-col">
                            <span className="font-medium">Custom Bits</span>
                            <span className="text-xs text-muted-foreground">
                              Test your own bit sequence
                            </span>
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Choose to use an algorithm or provide custom bits
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
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select an RNG algorithm">
                              {field.value &&
                                rngs.find(
                                  (rng) => rng.id.toString() === field.value
                                )?.name}
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
                      <FormDescription>
                        Choose the random number generator to test
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              {/* Custom Bits Input (only for custom_bits input) */}
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
                              const sanitized = e.target.value.replace(
                                /[^01\s]/g,
                                ""
                              );
                              field.onChange(sanitized);
                            }}
                          />
                        </ScrollArea>
                      </FormControl>
                      <FormDescription>
                        Enter a sequence of 0s and 1s. Spaces and line breaks
                        will be ignored.
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
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="single">
                          <div className="flex flex-col">
                            <span className="font-medium">Single Test</span>
                            <span className="text-xs text-muted-foreground">
                              Run one statistical test
                            </span>
                          </div>
                        </SelectItem>
                        <SelectItem value="nist_suite">
                          <div className="flex flex-col">
                            <span className="font-medium">NIST Test Suite</span>
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
                      Choose between single test, NIST test suite, or Diehard
                      test suite
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
                        defaultValue={field.value}
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
                        <FormLabel className="text-base">NIST Tests</FormLabel>
                        <FormDescription>
                          Select which NIST tests to run
                        </FormDescription>
                      </div>
                      <ScrollArea className="h-96 border rounded-md">
                        <div className="space-y-3 p-4">
                          {NIST_TESTS.map((test) => (
                            <FormField
                              key={test.id}
                              control={form.control}
                              name="nist_tests"
                              render={({ field }) => {
                                const isChecked = field.value?.includes(
                                  test.id
                                );
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
                                          onCheckedChange={(checked) => {
                                            return checked
                                              ? field.onChange([
                                                  ...(field.value || []),
                                                  test.id,
                                                ])
                                              : field.onChange(
                                                  field.value?.filter(
                                                    (value) => value !== test.id
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
                          Select which Diehard tests to run (some tests require
                          minimum bit counts)
                        </FormDescription>
                      </div>
                      <ScrollArea className="h-96 border rounded-md">
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
                                            checked={isChecked && !isDisabled}
                                            disabled={isDisabled}
                                            onCheckedChange={(checked) => {
                                              if (isDisabled) return;

                                              return checked
                                                ? field.onChange([
                                                    ...(field.value || []),
                                                    test.id,
                                                  ])
                                                : field.onChange(
                                                    field.value?.filter(
                                                      (value) =>
                                                        value !== test.id
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
                                              {inputType === "custom_bits"
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
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              {/* Samples Count (only for algorithm input type) */}
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
                        Number of random samples to generate (100 - 10,000,000)
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              {/* Seed (only for algorithm input type) */}
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
              <Button
                type="submit"
                className="w-full"
                disabled={isSubmitting}
                size="lg"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Running{" "}
                    {testType === "nist_suite" || testType === "diehard_suite"
                      ? "Tests"
                      : "Test"}
                    ...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Run{" "}
                    {testType === "nist_suite" || testType === "diehard_suite"
                      ? "Tests"
                      : "Test"}
                  </>
                )}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
};
