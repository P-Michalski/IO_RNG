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
import { FileText } from "lucide-react";
import { PerformanceTrendsChart } from "./PerformanceTrendsChart";

interface TestTypePerformanceDialogProps {
  testComparison: Array<{
    name: string;
    passRate: number;
    avgTime: number;
    totalTests: number;
    avgScore: number;
  }>;
  testPerformanceBySamples: Array<{
    testName: string;
    data: Array<{ samples: number; passRate: number; score: number }>;
  }>;
}

export const TestTypePerformanceDialog = ({
  testComparison,
  testPerformanceBySamples,
}: TestTypePerformanceDialogProps) => {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Card className="cursor-pointer hover:shadow-lg transition-shadow flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Test Type Analysis
            </CardTitle>
            <CardDescription>
              Performance breakdown for each test type
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col grow">
            <div className="space-y-2 grow">
              {testComparison.slice(0, 3).map((test, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-sm font-medium truncate max-w-[150px] sm:max-w-[200px]">
                    {test.name}
                  </span>
                  <Badge
                    variant={test.passRate > 70 ? "default" : "destructive"}
                  >
                    {test.passRate.toFixed(1)}%
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
          <DialogTitle>Test Type Performance Analysis</DialogTitle>
          <DialogDescription>
            Comprehensive metrics for all test types
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
                {testComparison.map((test, idx) => (
                  <Card key={idx}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-base">{test.name}</CardTitle>
                        <Badge
                          variant={
                            test.passRate > 70
                              ? "default"
                              : test.passRate > 50
                              ? "secondary"
                              : "destructive"
                          }
                        >
                          {test.passRate.toFixed(1)}%
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Total Runs</p>
                          <p className="text-xl font-bold">{test.totalTests}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Avg Time</p>
                          <p className="text-xl font-bold">
                            {test.avgTime.toFixed(1)}ms
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Avg Score</p>
                          <p className="text-xl font-bold">
                            {test.avgScore.toFixed(3)}
                          </p>
                        </div>
                      </div>
                      <Progress value={test.passRate} className="mt-4" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </TabsContent>
          <TabsContent value="trends" className="min-w-0">
            <ScrollArea className="h-[500px] pr-4">
              <div className="space-y-6 min-w-0">
                {testPerformanceBySamples.map((test, idx) => (
                  <div
                    key={idx}
                    data-chart-id={`test-trend-${idx}`}
                    data-chart-title={test.testName}
                  >
                    <PerformanceTrendsChart
                      title={test.testName}
                      data={test.data}
                    />
                  </div>
                ))}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};
