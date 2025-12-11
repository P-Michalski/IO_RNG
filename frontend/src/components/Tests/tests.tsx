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
import { toast } from "sonner";
import { type RNG } from "@/types/test-results";
import { FlaskConical, Loader2, Sparkles } from "lucide-react";

const testFormSchema = z.object({
  rng_id: z.string().min(1, "Please select an RNG"),
  test_name: z.enum(["frequency_test", "uniformity_test"], {
    message: "Please select a test type",
  }),
  samples_count: z
    .number()
    .min(100, "Minimum 100 samples")
    .max(10000000, "Maximum 10M samples"),
  seed: z.number().int().min(0, "Seed must be positive"),
});

type TestFormValues = z.infer<typeof testFormSchema>;

export const Tests = () => {
  const [rngs, setRngs] = useState<RNG[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<TestFormValues>({
    resolver: zodResolver(testFormSchema),
    defaultValues: {
      rng_id: "",
      test_name: "frequency_test",
      samples_count: 100000,
      seed: 42,
    },
  });

  useEffect(() => {
    const fetchRngs = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/rngs/");
        if (!response.ok) throw new Error("Failed to fetch RNGs");
        const data = await response.json();
        setRngs(data.filter((rng: RNG) => rng.is_active));
      } catch (error) {
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
      const response = await fetch(
        `http://localhost:8000/api/rngs/${values.rng_id}/run_test/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            test_name: values.test_name,
            samples_count: values.samples_count,
            seed: values.seed,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Test execution failed");
      }

      const result = await response.json();

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
    } catch (error) {
      toast.error("Error", {
        description:
          error instanceof Error ? error.message : "Failed to run test",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatTestName = (name: string) => {
    return name
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen w-full">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-2xl">
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
            Select an RNG algorithm and configure test parameters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* RNG Selection */}
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

              {/* Test Type */}
              <FormField
                control={form.control}
                name="test_name"
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
                            <span className="font-medium">Frequency Test</span>
                            <span className="text-xs text-muted-foreground">
                              Chi-square goodness of fit test
                            </span>
                          </div>
                        </SelectItem>
                        <SelectItem value="uniformity_test">
                          <div className="flex flex-col">
                            <span className="font-medium">Uniformity Test</span>
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

              {/* Samples Count */}
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
                        onChange={(e) => field.onChange(Number(e.target.value))}
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

              {/* Seed */}
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
                        onChange={(e) => field.onChange(Number(e.target.value))}
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
                    Running Test...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Run Test
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
