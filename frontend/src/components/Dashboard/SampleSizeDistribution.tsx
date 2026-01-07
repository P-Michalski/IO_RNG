import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts";
import { Clock } from "lucide-react";

interface SampleSizeDistributionProps {
  data: Array<{
    range: string;
    count: number;
    avgTime: number;
    totalTime: number;
  }>;
}

const sampleDistributionChartConfig = {
  count: {
    label: "Test Count",
    color: "var(--chart-1)",
  },
  avgTime: {
    label: "Avg Time (ms)",
    color: "var(--chart-2)",
  },
} satisfies ChartConfig;

export const SampleSizeDistribution = ({
  data,
}: SampleSizeDistributionProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Sample Size Distribution
        </CardTitle>
        <CardDescription>Test execution time by sample ranges</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={sampleDistributionChartConfig}
          className="h-[300px] w-full"
          data-chart-id="sample-distribution"
        >
          <BarChart accessibilityLayer data={data}>
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
            <ChartTooltip content={<ChartTooltipContent />} />
            <ChartLegend content={<ChartLegendContent />} />
            <Bar
              dataKey="count"
              fill="var(--color-count)"
              radius={[4, 4, 0, 0]}
            />
            <Bar
              dataKey="avgTime"
              fill="var(--color-avgTime)"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
