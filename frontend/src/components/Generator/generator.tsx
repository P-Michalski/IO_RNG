import { useState, useEffect } from "react";
import { Copy, TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { toast } from "sonner";
import { Separator } from "@/components/ui/separator";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Loading } from "../Loading/loading";
import { Error as ErrorComponent } from "../Error/error";

// Definicje parametrów dla każdego algorytmu
const ALGORITHM_PARAMS = {
  1: {
    name: "AWCG",
    params: {
      seed: 123456789,
      r: 24,
      s: 10,
      base: 4294967296,
    },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  2: {
    name: "SplitMix64",
    params: { seed: 123456789 },
    defaults: {
      bits_per_value: 64,
      msb_first: 1,
    },
  },
  3: {
    name: "LCG",
    params: {
      seed: 123456789,
      a: 1664525,
      c: 1013904223,
      m: 4294967296,
    },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  4: {
    name: "Park-Miller",
    params: { seed: 123456789 },
    defaults: {
      bits_per_value: 31,
      msb_first: 1,
    },
  },
  5: {
    name: "PCG32",
    params: { initstate: 42, seq: 54 },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  6: {
    name: "Mersenne Twister (Python random)",
    params: { seed: 12345 },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  7: {
    name: "OS /dev/urandom",
    params: {},
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  10: {
    name: "LCG with GLIBC parameters",
    params: {
      seed: 123456789,
      a: 1103515245,
      c: 12345,
      m: 2147483648,
    },
    defaults: {
      bits_per_value: 31,
      msb_first: 1,
    },
  },
  11: {
    name: "AWCG (r=24, s=10)",
    params: {
      seed: 123456789,
      r: 24,
      s: 10,
      base: 4294967296,
    },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  16: {
    name: "Blum Blum Shub",
    params: { seed: 12345, p: 383, q: 503 },
    defaults: {
      bits_per_value: 1,
      msb_first: 1,
    },
  },
};

type AlgorithmId = keyof typeof ALGORITHM_PARAMS;

export const Generator = () => {
  const [selectedAlgo, setSelectedAlgo] = useState<AlgorithmId>(1);
  const [n, setN] = useState(1000);
  const [params, setParams] = useState<Record<string, any>>(
    ALGORITHM_PARAMS[1].params
  );
  const [useDefaults, setUseDefaults] = useState(true);
  const [advancedParams, setAdvancedParams] = useState<Record<string, any>>(
    ALGORITHM_PARAMS[1].defaults
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initializing, setInitializing] = useState(true);
  const [result, setResult] = useState<{
    bits: number[];
    execution_time_ms: number;
    count: number;
    rng_id: number;
    rng_name: string;
    seed: number | null;
  } | null>(null);

  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/rngs", {
          method: "GET",
        });

        if (!response.ok) {
          throw new Error("Backend API is not responding");
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to connect to backend"
        );
      } finally {
        setInitializing(false);
      }
    };

    checkBackendConnection();
  }, []);

  const handleAlgorithmChange = (value: string) => {
    const algoId = parseInt(value) as AlgorithmId;
    setSelectedAlgo(algoId);
    setParams(ALGORITHM_PARAMS[algoId].params);
    setAdvancedParams(ALGORITHM_PARAMS[algoId].defaults);
    setUseDefaults(true);
  };

  const handleParamChange = (key: string, value: string) => {
    setParams((prev) => ({
      ...prev,
      [key]: isNaN(Number(value)) ? value : Number(value),
    }));
  };

  const handleAdvancedParamChange = (key: string, value: string) => {
    setAdvancedParams((prev) => ({
      ...prev,
      [key]: isNaN(Number(value)) ? value : Number(value),
    }));
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const seed = params.seed;
      const { seed: _removed, ...paramsWithoutSeed } = params;

      const parameters = {
        ...paramsWithoutSeed,
        ...(useDefaults
          ? ALGORITHM_PARAMS[selectedAlgo].defaults
          : advancedParams),
      };

      const requestBody: any = {
        count: n,
        parameters,
      };

      if (seed !== undefined) {
        requestBody.seed = seed;
      }

      console.log("Request body:", requestBody); // Debug

      const response = await fetch(
        `http://localhost:8000/api/rngs/${selectedAlgo}/generate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        }
      );

      if (!response.ok) throw new Error("Failed to generate bits");

      const data = await response.json();
      setResult(data);
      toast.success("Success", {
        description: `Generated ${
          data.bits.length
        } bits in ${data.execution_time_ms.toFixed(3)}ms`,
      });
    } catch (error) {
      toast.error("Error", {
        description: "Failed to generate bits",
      });
    } finally {
      setLoading(false);
    }
  };

  const copyBits = () => {
    if (result) {
      navigator.clipboard.writeText(result.bits.join(""));
      toast.success("Copied", {
        description: "Bits copied to clipboard",
      });
    }
  };

  const getChartData = () => {
    if (!result) return [];
    const chunkSize = Math.ceil(result.bits.length / 10);
    return Array.from({ length: 10 }, (_, i) => {
      const chunk = result.bits.slice(i * chunkSize, (i + 1) * chunkSize);
      const zeros = chunk.filter((b) => b === 0).length;
      const ones = chunk.filter((b) => b === 1).length;
      return { segment: `${i + 1}`, zeros, ones };
    });
  };

  const chartConfig = {
    zeros: { label: "Zeros", color: "var(--chart-1)" },
    ones: { label: "Ones", color: "var(--chart-2)" },
  } satisfies ChartConfig;

  if (initializing) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <Loading message="Connecting to backend..." fullScreen />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <ErrorComponent
          title="Backend Connection Error"
          description={`Failed to connect to the backend API: ${error}. Please make sure the backend server is running on http://localhost:8000`}
        />
      </div>
    );
  }

  return (
    <div className="container p-8 mx-auto overflow-hidden">
      <Card>
        <CardHeader>
          <CardTitle>RNG Bit Generator</CardTitle>
          <CardDescription>
            Generate random bits using various algorithms
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="algorithm">Algorithm</Label>
            <Select
              value={selectedAlgo.toString()}
              onValueChange={handleAlgorithmChange}
            >
              <SelectTrigger id="algorithm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(ALGORITHM_PARAMS).map(([id, { name }]) => (
                  <SelectItem key={id} value={id}>
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="n">Number of bits (N)</Label>
            <Input
              id="n"
              type="number"
              value={n}
              onChange={(e) => setN(parseInt(e.target.value))}
              min={1}
            />
          </div>

          <Separator />

          {Object.keys(params).length > 0 && (
            <div className="space-y-3">
              <Label>Algorithm Parameters</Label>
              {Object.entries(params).map(([key, value]) => (
                <div key={key} className="space-y-2">
                  <Label htmlFor={key} className="text-sm capitalize">
                    {key.replace("_", " ")}
                  </Label>
                  <Input
                    id={key}
                    value={value}
                    onChange={(e) => handleParamChange(key, e.target.value)}
                  />
                </div>
              ))}
            </div>
          )}

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
              <Label
                htmlFor="useDefaults"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Use default advanced parameters
              </Label>
            </div>

            <div className="space-y-3">
              <Label>Advanced Parameters</Label>
              {Object.entries(
                useDefaults
                  ? ALGORITHM_PARAMS[selectedAlgo].defaults
                  : advancedParams
              ).map(([key, value]) => (
                <div key={key} className="space-y-2">
                  <Label htmlFor={key} className="text-sm capitalize">
                    {key.replace("_", " ")}
                  </Label>
                  <Input
                    id={key}
                    value={value}
                    onChange={(e) =>
                      handleAdvancedParamChange(key, e.target.value)
                    }
                    disabled={useDefaults}
                  />
                </div>
              ))}
            </div>
          </div>

          <Button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full"
          >
            {loading ? "Generating..." : "Generate Bits"}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Generated Bits</CardTitle>
              <CardDescription>
                Execution time: {result.execution_time_ms.toFixed(3)}ms | Total
                bits: {result.bits.length}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <ScrollArea className="h-auto min-w-0 w-full rounded-md border">
                  <div className="p-4 flex">
                    <pre className="text-xs font-mono whitespace-nowrap">
                      {result.bits.join("")}
                    </pre>
                  </div>
                  <ScrollBar orientation="horizontal" />
                </ScrollArea>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button size="sm" variant="outline" onClick={copyBits}>
                      <Copy className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Copy</TooltipContent>
                </Tooltip>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Bit Distribution</CardTitle>
              <CardDescription>
                Distribution of 0s and 1s across segments
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-[300px] w-full">
                <BarChart accessibilityLayer data={getChartData()} barSize={30}>
                  <CartesianGrid vertical={false} />
                  <XAxis
                    dataKey="segment"
                    tickLine={false}
                    tickMargin={10}
                    axisLine={false}
                  />
                  <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent indicator="dashed" />}
                  />
                  <Bar dataKey="zeros" fill="var(--color-zeros)" radius={4} />
                  <Bar dataKey="ones" fill="var(--color-ones)" radius={4} />
                </BarChart>
              </ChartContainer>
            </CardContent>
            <CardFooter className="flex-col items-start gap-2 text-sm">
              <div className="flex gap-2 leading-none font-medium">
                <TrendingUp className="h-4 w-4" />
                Balance:{" "}
                {(
                  (result.bits.filter((b) => b === 1).length /
                    result.bits.length) *
                  100
                ).toFixed(2)}
                % ones
              </div>
              <div className="text-muted-foreground leading-none">
                {result.bits.filter((b) => b === 0).length} zeros,{" "}
                {result.bits.filter((b) => b === 1).length} ones
              </div>
            </CardFooter>
          </Card>
        </>
      )}
    </div>
  );
};
