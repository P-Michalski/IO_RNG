import {
  Card,
  CardContent,
  CardDescription,
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
  type ChartConfig,
  ChartTooltip,
} from "@/components/ui/chart";
import {
  CartesianGrid,
  XAxis,
  YAxis,
  ScatterChart,
  Scatter,
  LineChart,
  Line,
} from "recharts";
import { Zap } from "lucide-react";
import { type RNG } from "@/types/test-results";

interface PerformanceVsSampleSizeProps {
  performanceData: Array<{
    samples: number;
    executionTime: number;
    score: number;
    passed: boolean;
    testName: string;
    rngName: string;
  }>;
  averagedLineData: Array<{ samples: number; avgTime: number }>;
  selectedRng: string;
  setSelectedRng: (value: string) => void;
  selectedTest: string;
  setSelectedTest: (value: string) => void;
  rngs: RNG[];
  testNames: string[];
}

const performanceChartConfig = {
  executionTime: {
    label: "Execution Time (ms)",
    color: "var(--chart-1)",
  },
  avgTime: {
    label: "Average Time",
    color: "var(--chart-3)",
  },
} satisfies ChartConfig;

export const PerformanceVsSampleSize = ({
  performanceData,
  averagedLineData,
  selectedRng,
  setSelectedRng,
  selectedTest,
  setSelectedTest,
  rngs,
  testNames,
}: PerformanceVsSampleSizeProps) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Performance vs Sample Size
            </CardTitle>
            <CardDescription>
              Execution time correlation with sample count
            </CardDescription>
          </div>
          <div className="flex gap-2 flex-wrap">
            <Select value={selectedRng} onValueChange={setSelectedRng}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Select RNG" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Algorithms</SelectItem>
                {rngs.map((rng) => (
                  <SelectItem key={rng.id} value={rng.id.toString()}>
                    {rng.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedTest} onValueChange={setSelectedTest}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Select Test" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Tests</SelectItem>
                {testNames.map((testName) => (
                  <SelectItem key={testName} value={testName}>
                    {testName}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={performanceChartConfig}
          className="h-[300px] w-full"
          data-chart-id="performance-vs-sample"
        >
          {selectedRng === "all" || selectedTest === "all" ? (
            // Show scatter chart when filtering multiple algorithms/tests
            <ScatterChart accessibilityLayer>
              <CartesianGrid />
              <XAxis
                type="number"
                dataKey="samples"
                name="Sample Count"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <YAxis
                type="number"
                dataKey="executionTime"
                name="Execution Time (ms)"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <ChartTooltip
                cursor={{ strokeDasharray: "3 3" }}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const data = payload[0].payload;
                  return (
                    <div className="rounded-lg border bg-background p-2 shadow-sm">
                      <div className="grid gap-2">
                        <div className="flex flex-col">
                          <span className="text-[0.70rem] uppercase text-muted-foreground">
                            Sample Count
                          </span>
                          <span className="font-bold">
                            {data.samples.toLocaleString()}
                          </span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[0.70rem] uppercase text-muted-foreground">
                            Execution Time
                          </span>
                          <span className="font-bold">
                            {data.executionTime.toFixed(1)}ms
                          </span>
                        </div>
                        {selectedRng === "all" && (
                          <div className="flex flex-col">
                            <span className="text-[0.70rem] uppercase text-muted-foreground">
                              Algorithm
                            </span>
                            <span className="font-bold">{data.rngName}</span>
                          </div>
                        )}
                        {selectedTest === "all" && (
                          <div className="flex flex-col">
                            <span className="text-[0.70rem] uppercase text-muted-foreground">
                              Test
                            </span>
                            <span className="font-bold">{data.testName}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                }}
              />
              <Scatter
                name="Tests"
                data={performanceData}
                fill="var(--color-executionTime)"
              />
            </ScatterChart>
          ) : (
            // Show line chart when filtering specific algorithm AND test
            <LineChart accessibilityLayer data={averagedLineData}>
              <CartesianGrid />
              <XAxis
                type="number"
                dataKey="samples"
                name="Sample Count"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <YAxis
                type="number"
                dataKey="avgTime"
                name="Avg Execution Time (ms)"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <ChartTooltip
                cursor={{ strokeDasharray: "3 3" }}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const data = payload[0].payload;
                  return (
                    <div className="rounded-lg border bg-background p-2 shadow-sm">
                      <div className="grid gap-2">
                        <div className="flex flex-col">
                          <span className="text-[0.70rem] uppercase text-muted-foreground">
                            Sample Count
                          </span>
                          <span className="font-bold">
                            {data.samples.toLocaleString()}
                          </span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[0.70rem] uppercase text-muted-foreground">
                            Avg Execution Time
                          </span>
                          <span className="font-bold">
                            {data.avgTime.toFixed(1)}ms
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                }}
              />
              <Line
                type="monotone"
                dataKey="avgTime"
                stroke="var(--color-avgTime)"
                strokeWidth={3}
                dot={{ fill: "var(--color-avgTime)", r: 4 }}
                name="Average Time"
              />
            </LineChart>
          )}
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
