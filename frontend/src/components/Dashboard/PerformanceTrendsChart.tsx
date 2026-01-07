/* filepath: frontend/src/components/Dashboard/PerformanceTrendsChart.tsx */
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { Line, LineChart, CartesianGrid, XAxis, YAxis } from "recharts";

interface PerformanceTrendsChartProps {
  title: string;
  data: Array<{ samples: number; passRate: number; score: number }>;
}

const performanceTrendChartConfig = {
  passRate: {
    label: "Pass Rate (%)",
    color: "var(--chart-1)",
  },
  score: {
    label: "Score",
    color: "var(--chart-2)",
  },
} satisfies ChartConfig;

export const PerformanceTrendsChart = ({
  title,
  data,
}: PerformanceTrendsChartProps) => {
  return (
    <Card className="min-w-0 overflow-hidden">
      <CardHeader>
        <CardTitle className="text-base truncate">{title}</CardTitle>
      </CardHeader>
      <CardContent className="min-w-0 overflow-hidden">
        <div className="w-full min-w-0 overflow-hidden">
          <ChartContainer
            config={performanceTrendChartConfig}
            className="h-[200px] w-full min-w-0"
          >
            <LineChart accessibilityLayer data={data}>
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey="samples"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
              />
              <YAxis
                yAxisId="left"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="passRate"
                stroke="var(--color-passRate)"
                strokeWidth={2}
                dot={false}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="score"
                stroke="var(--color-score)"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ChartContainer>
        </div>
      </CardContent>
    </Card>
  );
};
