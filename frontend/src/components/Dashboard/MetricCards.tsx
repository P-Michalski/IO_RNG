import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Award, AlertCircle } from "lucide-react";

interface MetricCardsProps {
  totalTests: number;
  overallPassRate: number;
  avgScore: number;
  avgExecutionTime: number;
}

export const MetricCards = ({
  totalTests,
  overallPassRate,
  avgScore,
  avgExecutionTime,
}: MetricCardsProps) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">Total Tests</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalTests}</div>
          <p className="text-xs text-muted-foreground">Test executions</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">Pass Rate</CardTitle>
          <Award className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {overallPassRate.toFixed(1)}%
          </div>
          <p className="text-xs text-muted-foreground">Overall success rate</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">Avg Score</CardTitle>
          <AlertCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{avgScore.toFixed(3)}</div>
          <p className="text-xs text-muted-foreground">Average test score</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">Avg Exec Time</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {avgExecutionTime.toFixed(1)}ms
          </div>
          <p className="text-xs text-muted-foreground">Per test execution</p>
        </CardContent>
      </Card>
    </div>
  );
};
