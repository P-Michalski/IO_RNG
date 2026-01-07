import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Award } from "lucide-react";
import { PerformanceTrendsChart } from "./PerformanceTrendsChart";

interface AlgorithmPerformanceDialogProps {
  rngComparison: Array<{
    name: string;
    passRate: number;
    avgTime: number;
    totalTests: number;
    avgScore: number;
  }>;
  rngPerformanceBySamples: Array<{
    rngName: string;
    rngId: number;
    data: Array<{ samples: number; passRate: number; score: number }>;
  }>;
}

export const AlgorithmPerformanceDialog = ({
  rngComparison,
  rngPerformanceBySamples,
}: AlgorithmPerformanceDialogProps) => {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Card className="cursor-pointer hover:shadow-lg transition-shadow flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              Algorithm Performance
            </CardTitle>
            <CardDescription>
              Pass rates and metrics for each algorithm
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col grow">
            <div className="space-y-2 grow">
              {rngComparison.slice(0, 3).map((rng, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-sm font-medium truncate max-w-[150px] sm:max-w-[200px]">
                    {rng.name}
                  </span>
                  <Badge
                    variant={rng.passRate > 70 ? "default" : "destructive"}
                  >
                    {rng.passRate.toFixed(1)}%
                  </Badge>
                </div>
              ))}
            </div>
            <Button variant="ghost" className="w-full mt-4">
              View Detailed Analysis →
            </Button>
          </CardContent>
        </Card>
      </DialogTrigger>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle>Algorithm Performance Analysis</DialogTitle>
          <DialogDescription>
            Comprehensive metrics for all tested algorithms
          </DialogDescription>
        </DialogHeader>
        <Tabs defaultValue="overview" className="w-full min-w-0">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="trends">Performance Trends</TabsTrigger>
          </TabsList>
          <TabsContent value="overview" className="min-w-0">
            <ScrollArea className="h-[500px] pr-4">
              <div className="space-y-4">
                {rngComparison.map((rng, idx) => (
                  <Card key={idx}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-base md:text-lg">
                          #{idx + 1} {rng.name}
                        </CardTitle>
                        <Badge
                          variant={
                            rng.passRate > 70
                              ? "default"
                              : rng.passRate > 50
                              ? "secondary"
                              : "destructive"
                          }
                        >
                          {rng.passRate.toFixed(1)}% Pass Rate
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Total Tests</p>
                          <p className="text-xl font-bold">{rng.totalTests}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">
                            Avg Execution Time
                          </p>
                          <p className="text-xl font-bold">
                            {rng.avgTime.toFixed(1)}ms
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Avg Score</p>
                          <p className="text-xl font-bold">
                            {rng.avgScore.toFixed(3)}
                          </p>
                        </div>
                      </div>
                      <Progress value={rng.passRate} className="mt-4" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </TabsContent>
          <TabsContent value="trends" className="min-w-0">
            <ScrollArea className="h-[500px] pr-4">
              <div className="space-y-6 min-w-0 ">
                {rngPerformanceBySamples.map((rng, idx) => (
                  <PerformanceTrendsChart
                    key={idx}
                    title={rng.rngName}
                    data={rng.data}
                  />
                ))}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};
