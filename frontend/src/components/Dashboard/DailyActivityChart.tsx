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
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";
import { Activity } from "lucide-react";

interface DailyTestActivityProps {
  data: Array<{ date: string; passed: number; failed: number; total: number }>;
}

const activityChartConfig = {
  passed: {
    label: "Passed",
    color: "var(--chart-1)",
  },
  failed: {
    label: "Failed",
    color: "var(--chart-2)",
  },
} satisfies ChartConfig;

export const DailyTestActivity = ({ data }: DailyTestActivityProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Daily Test Activity
        </CardTitle>
        <CardDescription>Test execution history over time</CardDescription>
      </CardHeader>
      <CardContent>
        <div data-chart-id="daily-activity">
          <ChartContainer
            config={activityChartConfig}
            className="h-[300px] w-full"
          >
            <AreaChart accessibilityLayer data={data}>
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey="date"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return date.toLocaleDateString("pl-PL", {
                    day: "numeric",
                    month: "numeric",
                  });
                }}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <ChartLegend content={<ChartLegendContent />} />
              <Area
                dataKey="passed"
                type="monotone"
                fill="var(--color-passed)"
                fillOpacity={0.4}
                stroke="var(--color-passed)"
              />
              <Area
                dataKey="failed"
                type="monotone"
                fill="var(--color-failed)"
                fillOpacity={0.4}
                stroke="var(--color-failed)"
              />
            </AreaChart>
          </ChartContainer>
        </div>
      </CardContent>
    </Card>
  );
};
