import { useState, useRef, useEffect } from "react";
import { Copy, TrendingUp, Volume2, VolumeX } from "lucide-react";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";

interface NumberBlock {
  value: number;
  count: number;
  color: string;
}

export const NumberGenerator = () => {
  const [count, setCount] = useState(100);
  const [minValue, setMinValue] = useState(0);
  const [maxValue, setMaxValue] = useState(100);
  const [animateResults, setAnimateResults] = useState(true);
  const [result, setResult] = useState<{
    numbers: number[];
    execution_time_ms: number;
    count: number;
    rng_id: number;
    rng_name: string;
    range: { min: number; max: number };
  } | null>(null);

  const [showVisualization, setShowVisualization] = useState(false);
  const [numberBlocks, setNumberBlocks] = useState<NumberBlock[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [animatingNumbers, setAnimatingNumbers] = useState<Set<number>>(
    new Set()
  );

  const [volume, setVolume] = useState(50); // 0-100
  const [isMuted, setIsMuted] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const cancelGenerationRef = useRef(false);

  const generator = useGenerator();

  useEffect(() => {
    // Initialize audio
    audioRef.current = new Audio("/sounds/pop.mp3");
    audioRef.current.volume = volume / 100;

    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume / 100;
    }
  }, [volume, isMuted]);

  const playPopSound = () => {
    if (audioRef.current && !isMuted) {
      // Clone audio to allow overlapping sounds
      const sound = audioRef.current.cloneNode() as HTMLAudioElement;
      sound.volume = volume / 100;
      sound.play().catch(() => {});
    }
  };

  const getAccentHueRange = (): { base: number; range: number } => {
    const root = document.documentElement;
    const accent = root.getAttribute("data-accent") || "default";

    const accentHues: Record<string, { base: number; range: number }> = {
      default: { base: 0, range: 360 }, // Full spectrum
      blue: { base: 264, range: 40 }, // 244-304
      green: { base: 131, range: 30 }, // 116-161
      orange: { base: 41, range: 35 }, // 23-76
      red: { base: 27, range: 15 }, // 12-42
      rose: { base: 17, range: 20 }, // 7-27
      violet: { base: 293, range: 25 }, // 280-305
      yellow: { base: 85, range: 30 }, // 70-100
    };

    return accentHues[accent] || accentHues.default;
  };

  // Generate color based on number value (hue based on position in range)
  const getColorForNumber = (num: number): string => {
    const normalizedValue = (num - minValue) / (maxValue - minValue || 1);
    const { base, range } = getAccentHueRange();

    // Calculate hue within the accent range
    const hue = base + normalizedValue * range;

    // Vary saturation and lightness for more variety
    const saturation = 60 + normalizedValue * 20; // 60-80%
    const lightness = 50 + normalizedValue * 20; // 50-70%

    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };

  const calculateBitsNeeded = (min: number, max: number): number => {
    const range = max - min + 1;
    return Math.ceil(Math.log2(range));
  };

  const getGridColumns = (): string => {
    const maxNumber = Math.max(Math.abs(minValue), Math.abs(maxValue));
    const maxDigits = maxNumber.toString().length;

    // Adjust grid based on number length - fewer columns for better aspect ratio
    if (maxDigits <= 2) {
      return "grid-cols-6 sm:grid-cols-8 md:grid-cols-10 lg:grid-cols-12";
    } else if (maxDigits <= 3) {
      return "grid-cols-5 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10";
    } else if (maxDigits <= 4) {
      return "grid-cols-4 sm:grid-cols-5 md:grid-cols-6 lg:grid-cols-8";
    } else if (maxDigits <= 5) {
      return "grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6";
    } else if (maxDigits <= 6) {
      return "grid-cols-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5";
    } else if (maxDigits <= 7) {
      return "grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-4";
    } else {
      return "grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3";
    }
  };

  const bitsToNumberInRange = (
    bits: number[],
    min: number,
    max: number,
    startIndex: number
  ): { value: number; bitsUsed: number } | null => {
    const range = max - min + 1;
    const bitsNeeded = calculateBitsNeeded(min, max);

    const chunk = bits.slice(startIndex, startIndex + bitsNeeded);
    if (chunk.length < bitsNeeded) return null;

    const value = chunk.reduce((acc, bit, i) => acc + bit * Math.pow(2, i), 0);

    if (value >= range) {
      return null;
    }

    return {
      value: value + min,
      bitsUsed: bitsNeeded,
    };
  };

  const addNumberBlock = (num: number) => {
    playPopSound();

    setNumberBlocks((prev) => {
      const existingIndex = prev.findIndex((block) => block.value === num);

      if (existingIndex !== -1) {
        // Animate counter increase
        setAnimatingNumbers((prevSet) => new Set(prevSet).add(num));
        setTimeout(() => {
          setAnimatingNumbers((prevSet) => {
            const newSet = new Set(prevSet);
            newSet.delete(num);
            return newSet;
          });
        }, 300);

        const newBlocks = [...prev];
        newBlocks[existingIndex] = {
          ...newBlocks[existingIndex],
          count: newBlocks[existingIndex].count + 1,
        };
        return newBlocks;
      } else {
        return [
          ...prev,
          {
            value: num,
            count: 1,
            color: getColorForNumber(num),
          },
        ];
      }
    });
  };

  const handleDialogClose = (open: boolean) => {
    if (!open && isGenerating) {
      // User wants to close during generation - continue without animation

      cancelGenerationRef.current = true;
      toast.info("Animation Cancelled", {
        description: "Generation continues without animation",
      });
    }
    setShowVisualization(open);
  };

  const handleGenerate = async () => {
    if (minValue >= maxValue) {
      toast.error("Error", {
        description: "Minimum value must be less than maximum value",
      });
      return;
    }

    if (count < 1 || count > 100000) {
      toast.error("Error", {
        description: "Count must be between 1 and 100,000",
      });
      return;
    }

    // Reset state
    setNumberBlocks([]);
    setAnimatingNumbers(new Set());

    cancelGenerationRef.current = false;

    if (animateResults) {
      setShowVisualization(true);
    }

    setIsGenerating(true);
    generator.setLoading(true);

    try {
      const bitsPerNumber = calculateBitsNeeded(minValue, maxValue);

      const range = maxValue - minValue + 1;
      const maxPossibleValues = Math.pow(2, bitsPerNumber);
      const rejectionRate = (maxPossibleValues - range) / maxPossibleValues;

      const multiplier = Math.max(3, (1 / (1 - rejectionRate)) * 1.5);
      const bitsToRequest = Math.max(
        100,
        Math.ceil(count * bitsPerNumber * multiplier)
      );

      const data = await generator.generateBits(bitsToRequest);
      const bits = extractBitsFromResponse(data);

      const numbers: number[] = [];
      let currentIndex = 0;
      let attempts = 0;
      const maxAttempts = bitsToRequest / bitsPerNumber;

      // Generate numbers with animation delay
      const generateWithDelay = async () => {
        while (numbers.length < count && attempts < maxAttempts) {
          if (currentIndex + bitsPerNumber > bits.length) {
            break;
          }

          const result = bitsToNumberInRange(
            bits,
            minValue,
            maxValue,
            currentIndex
          );

          if (result) {
            numbers.push(result.value);

            // Only animate if animation enabled and not cancelled
            if (animateResults && !cancelGenerationRef.current) {
              addNumberBlock(result.value);

              // Add delay for animation (faster for large counts)
              if (count <= 100) {
                await new Promise((resolve) => setTimeout(resolve, 50));
              } else if (count <= 500) {
                await new Promise((resolve) => setTimeout(resolve, 20));
              } else {
                await new Promise((resolve) => setTimeout(resolve, 10));
              }
            }

            currentIndex += result.bitsUsed;
          } else {
            currentIndex += bitsPerNumber;
          }

          attempts++;
        }

        if (numbers.length < count) {
          toast.error("Error", {
            description: `Only generated ${numbers.length} of ${count} requested numbers. Try a smaller range or fewer numbers.`,
          });
          setIsGenerating(false);
          generator.setLoading(false);
          return;
        }

        // Set final result
        const finalResult = {
          numbers,
          execution_time_ms: data.execution_time_ms,
          count: numbers.length,
          rng_id: data.rng_id,
          rng_name: data.rng_name,
          range: { min: minValue, max: maxValue },
        };

        setResult(finalResult);
        setIsGenerating(false);

        toast.success("Success", {
          description: `Generated ${
            numbers.length
          } numbers in ${data.execution_time_ms.toFixed(3)}ms`,
        });
      };

      await generateWithDelay();
    } catch (error) {
      toast.error("Error", {
        description: "Failed to generate numbers",
      });
      setIsGenerating(false);
    } finally {
      generator.setLoading(false);
    }
  };

  const copyNumbers = () => {
    if (result) {
      navigator.clipboard.writeText(result.numbers.join(", "));
      toast.success("Copied", {
        description: "Numbers copied to clipboard",
      });
    }
  };

  const getChartData = () => {
    if (!result) return [];

    const totalRange = result.range.max - result.range.min + 1;
    const binCount = Math.min(10, totalRange);
    const binSize = Math.floor(totalRange / binCount);

    const bins = Array.from({ length: binCount }, (_, i) => {
      const binStart = result.range.min + i * binSize;
      const binEnd =
        i === binCount - 1 ? result.range.max : binStart + binSize - 1;

      const count = result.numbers.filter(
        (n) => n >= binStart && n <= binEnd
      ).length;

      return {
        range: `${binStart}-${binEnd}`,
        count,
      };
    });

    return bins;
  };

  const chartConfig = {
    count: { label: "Count", color: "var(--chart-1)" },
  } satisfies ChartConfig;

  // Calculate font size based on number length - adjusted for larger blocks
  const getFontSize = (num: number): string => {
    const numStr = num.toString();
    if (numStr.length <= 2) return "text-xl";
    if (numStr.length <= 3) return "text-lg";
    if (numStr.length <= 4) return "text-base";
    if (numStr.length <= 5) return "text-sm";
    if (numStr.length <= 6) return "text-xs";
    return "text-[10px]";
  };

  return (
    <div className="space-y-6">
      <GeneratorForm
        title="Number Generator"
        description="Generate random numbers in a specific range"
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
        buttonText="Generate Numbers"
        customInputs={
          <>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="count">Count (N)</Label>
                <Input
                  id="count"
                  type="number"
                  value={count}
                  onChange={(e) => {
                    const value = parseInt(e.target.value) || 1;
                    setCount(Math.min(Math.max(value, 1), 100000));
                  }}
                  min={1}
                  max={100000}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="min">Min Value</Label>
                <Input
                  id="min"
                  type="number"
                  value={minValue}
                  onChange={(e) => setMinValue(parseInt(e.target.value) || 0)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="max">Max Value</Label>
                <Input
                  id="max"
                  type="number"
                  value={maxValue}
                  onChange={(e) => setMaxValue(parseInt(e.target.value) || 0)}
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="animateResults"
                checked={animateResults}
                onCheckedChange={(checked) =>
                  setAnimateResults(checked as boolean)
                }
              />
              <Label
                htmlFor="animateResults"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Animate Results
              </Label>
            </div>

            {/* Volume Control - DODAJ TO */}
            {animateResults && (
              <div className="flex items-center gap-3">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsMuted(!isMuted)}
                  className="shrink-0"
                >
                  {isMuted ? (
                    <VolumeX className="h-5 w-5" />
                  ) : (
                    <Volume2 className="h-5 w-5" />
                  )}
                </Button>
                <div className="flex items-center gap-2 flex-1">
                  <Slider
                    value={[isMuted ? 0 : volume]}
                    onValueChange={(value) => {
                      setVolume(value[0]);
                      if (value[0] > 0 && isMuted) {
                        setIsMuted(false);
                      }
                    }}
                    max={100}
                    step={1}
                    className="flex-1"
                    disabled={isMuted}
                  />
                  <span className="text-sm text-muted-foreground w-10 text-right">
                    {isMuted ? 0 : volume}%
                  </span>
                </div>
              </div>
            )}
          </>
        }
      />

      {/* Visualization Dialog */}
      <Dialog open={showVisualization} onOpenChange={handleDialogClose}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>Number Generation Visualization</DialogTitle>
            <DialogDescription>
              {isGenerating
                ? "Generating numbers... Watch them appear! (Close to finish without animation)"
                : "Generation complete! View the results below."}
            </DialogDescription>
          </DialogHeader>

          <ScrollArea className="h-[500px] w-full rounded-md border p-4">
            <div className={`grid ${getGridColumns()} gap-3 m-2`}>
              {numberBlocks.map((block, index) => (
                <div
                  key={`${block.value}-${index}`}
                  className="relative animate-in fade-in zoom-in duration-300"
                >
                  <div
                    className={`
            aspect-square rounded-lg shadow-md
            flex flex-col items-center justify-center
            transition-all duration-300 p-2
            ${
              animatingNumbers.has(block.value)
                ? "scale-110 shadow-lg"
                : "scale-100"
            }
          `}
                    style={{
                      backgroundColor: block.color,
                    }}
                  >
                    <div
                      className={`font-bold text-white text-center leading-tight ${getFontSize(
                        block.value
                      )}`}
                    >
                      {block.value}
                    </div>
                    {block.count > 1 && (
                      <Badge
                        variant="secondary"
                        className={`
                absolute -top-2 -right-2 h-5 w-5 
                rounded-full p-0 flex items-center justify-center text-[10px] font-bold
                transition-transform duration-300
                ${animatingNumbers.has(block.value) ? "scale-125" : "scale-100"}
              `}
                      >
                        {block.count}
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <ScrollBar orientation="vertical" />
          </ScrollArea>

          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              Unique numbers: {new Set(numberBlocks.map((b) => b.value)).size}
            </span>
            <span>
              Total generated:{" "}
              {numberBlocks.reduce((sum, block) => sum + block.count, 0)}
            </span>
          </div>
          <DialogFooter className="flex-col items-center sm:items-center">
            <p className="text-xs italic text-muted-foreground text-center">
              Sound effect by{" "}
              <a
                href="https://pixabay.com/users/creatorshome-49707711/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=328170"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-foreground transition-colors"
              >
                CreatorsHome
              </a>{" "}
              from{" "}
              <a
                href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=328170"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-foreground transition-colors"
              >
                Pixabay
              </a>
            </p>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Generated Numbers</CardTitle>
              <CardDescription>
                Execution time: {result.execution_time_ms.toFixed(3)}ms | Total
                numbers: {result.count} | Range: {result.range.min} to{" "}
                {result.range.max}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <ScrollArea className="h-[300px] w-full rounded-md border">
                  <div className="p-4">
                    <div className="text-sm font-mono space-y-1">
                      {result.numbers.map((num, i) => (
                        <div key={i} className="inline-block mr-2">
                          {num}
                          {i < result.numbers.length - 1 && ","}
                        </div>
                      ))}
                    </div>
                  </div>
                  <ScrollBar orientation="vertical" />
                </ScrollArea>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button size="sm" variant="outline" onClick={copyNumbers}>
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
              <CardTitle>Number Distribution</CardTitle>
              <CardDescription>
                Distribution of generated numbers across range
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-[300px] w-full">
                <BarChart accessibilityLayer data={getChartData()}>
                  <CartesianGrid vertical={false} />
                  <XAxis
                    dataKey="range"
                    tickLine={false}
                    tickMargin={10}
                    axisLine={false}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis />
                  <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent />}
                  />
                  <Bar dataKey="count" fill="var(--color-count)" radius={4} />
                </BarChart>
              </ChartContainer>
            </CardContent>
            <CardFooter className="flex-col items-start gap-2 text-sm">
              <div className="flex gap-2 leading-none font-medium">
                <TrendingUp className="h-4 w-4" />
                Average:{" "}
                {(
                  result.numbers.reduce((a, b) => a + b, 0) / result.count
                ).toFixed(2)}
              </div>
              <div className="text-muted-foreground leading-none">
                Min: {Math.min(...result.numbers)}, Max:{" "}
                {Math.max(...result.numbers)}
              </div>
            </CardFooter>
          </Card>
        </>
      )}
    </div>
  );
};
