import { useState } from "react";
import { Copy, TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { toast } from "sonner";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { extractBitsFromResponse } from "@/utils/compression";
import { GeneratorForm } from "../generator-form";
import { useGenerator } from "@/hooks/use-generator";

export const BitGenerator = () => {
  const [n, setN] = useState(1000);
  const [result, setResult] = useState<{
    bits: number[];
    execution_time_ms: number;
    count: number;
    rng_id: number;
    rng_name: string;
    seed: number | null;
  } | null>(null);

  const generator = useGenerator();

  const handleGenerate = async () => {
    generator.setLoading(true);
    try {
      const data = await generator.generateBits(n);
      const bits = extractBitsFromResponse(data);

      setResult({ ...data, bits });

      toast.success("Success", {
        description: `Generated ${
          bits.length
        } bits in ${data.execution_time_ms.toFixed(3)}ms`,
      });
    } catch (error) {
      toast.error("Error", {
        description: "Failed to generate bits",
      });
    } finally {
      generator.setLoading(false);
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

  return (
    <div className="space-y-6">
      <GeneratorForm
        title="Bit Generator"
        description="Generate random bits using various algorithms"
        selectedAlgo={generator.selectedAlgo}
        onAlgorithmChange={generator.handleAlgorithmChange}
        params={generator.params}
        onParamChange={generator.handleParamChange}
        useDefaults={generator.useDefaults}
        onUseDefaultsChange={generator.setUseDefaults}
        advancedParams={generator.advancedParams}
        onAdvancedParamChange={generator.handleAdvancedParamChange}
        loading={generator.loading}
        onGenerate={handleGenerate}
        buttonText="Generate Bits"
        customInputs={
          <div className="space-y-2">
            <Label htmlFor="n">Number of bits (N)</Label>
            <Input
              id="n"
              type="number"
              value={n}
              onChange={(e) => setN(parseInt(e.target.value) || 1)}
              min={1}
            />
          </div>
        }
      />

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
