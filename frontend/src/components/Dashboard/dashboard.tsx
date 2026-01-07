import { useMemo, useState, useEffect } from "react";
import { useTestResults } from "@/contexts/test-results-context";
import { Loading } from "../Loading/loading";
import { Error as ErrorComponent } from "../Error/error";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Target,
  AlertCircle,
  Layers,
  FileText,
  Sparkles,
  Loader2,
} from "lucide-react";
import { DailyTestActivity } from "./DailyActivityChart";
import { PerformanceVsSampleSize } from "./PerformanceVsSampleSize";
import { AlgorithmPerformanceDialog } from "./AlgorithmPerformanceDialog";
import { TestTypePerformanceDialog } from "./TestTypePerformanceDialog";
import { SampleSizeDistribution } from "./SampleSizeDistribution";
import { ReportGenerator } from "./reports";
import { HiddenChartsRenderer } from "./HiddenChartsRenderer";

export const Dashboard = () => {
  const { results, rngs, loading, error, refetch } = useTestResults();
  const [selectedRng, setSelectedRng] = useState<string>("all");
  const [selectedTest, setSelectedTest] = useState<string>("all");

  // Refetch data when component mounts to ensure fresh data
  useEffect(() => {
    refetch();
  }, []);

  const statistics = useMemo(() => {
    if (results.length === 0) return null;

    // Overall metrics
    const totalTests = results.length;
    const passedTests = results.filter((r) => r.passed).length;
    const overallPassRate = (passedTests / totalTests) * 100;

    // Daily activity data
    const dailyActivity = results.reduce((acc, result) => {
      const dateObj = new Date(result.created_at);
      // Use ISO format YYYY-MM-DD for proper sorting and parsing
      const date = dateObj.toISOString().split("T")[0];
      if (!acc[date]) {
        acc[date] = { date, passed: 0, failed: 0, total: 0 };
      }
      acc[date].total += 1;
      if (result.passed) {
        acc[date].passed += 1;
      } else {
        acc[date].failed += 1;
      }
      return acc;
    }, {} as Record<string, { date: string; passed: number; failed: number; total: number }>);

    const activityData = Object.values(dailyActivity).sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
    );

    // Performance vs Sample Size (for selected RNG and Test)
    const performanceData = results
      .filter(
        (r) =>
          (selectedRng === "all" || r.rng_id.toString() === selectedRng) &&
          (selectedTest === "all" || r.test_name === selectedTest)
      )
      .map((r) => ({
        samples: r.samples_count,
        executionTime: r.execution_time_ms,
        score: r.score,
        passed: r.passed,
        testName: r.test_name,
        rngName: rngs.find((rng) => rng.id === r.rng_id)?.name || "Unknown",
      }))
      .sort((a, b) => a.samples - b.samples);

    // Calculate averaged line data if filtering by specific RNG AND Test
    let averagedLineData: { samples: number; avgTime: number }[] = [];
    if (selectedRng !== "all" && selectedTest !== "all") {
      // Group by sample size and calculate average
      const sampleGroups = performanceData.reduce((acc, point) => {
        if (!acc[point.samples]) {
          acc[point.samples] = { total: 0, count: 0 };
        }
        acc[point.samples].total += point.executionTime;
        acc[point.samples].count += 1;
        return acc;
      }, {} as Record<number, { total: number; count: number }>);

      averagedLineData = Object.entries(sampleGroups)
        .map(([samples, data]) => ({
          samples: parseInt(samples),
          avgTime: data.total / data.count,
        }))
        .sort((a, b) => a.samples - b.samples);
    }

    // RNG comparison data with pass rate by sample count
    const rngComparison = rngs
      .map((rng) => {
        const rngResults = results.filter((r) => r.rng_id === rng.id);
        const passed = rngResults.filter((r) => r.passed).length;
        return {
          name: rng.name,
          passRate:
            rngResults.length > 0 ? (passed / rngResults.length) * 100 : 0,
          avgTime:
            rngResults.length > 0
              ? rngResults.reduce((acc, r) => acc + r.execution_time_ms, 0) /
                rngResults.length
              : 0,
          totalTests: rngResults.length,
          avgScore:
            rngResults.length > 0
              ? rngResults.reduce((acc, r) => acc + r.score, 0) /
                rngResults.length
              : 0,
        };
      })
      .filter((r) => r.totalTests > 0)
      .sort((a, b) => b.passRate - a.passRate);

    // Test type comparison with pass rate by sample count
    const testNames = [...new Set(results.map((r) => r.test_name))];
    const testComparison = testNames
      .map((testName) => {
        const testResults = results.filter((r) => r.test_name === testName);
        const passed = testResults.filter((r) => r.passed).length;
        return {
          name: testName,
          passRate: (passed / testResults.length) * 100,
          avgTime:
            testResults.reduce((acc, r) => acc + r.execution_time_ms, 0) /
            testResults.length,
          totalTests: testResults.length,
          avgScore:
            testResults.reduce((acc, r) => acc + r.score, 0) /
            testResults.length,
        };
      })
      .sort((a, b) => b.passRate - a.passRate);

    // RNG performance by sample count
    const rngPerformanceBySamples = rngs
      .map((rng) => {
        const rngResults = results.filter((r) => r.rng_id === rng.id);

        // Group by sample count and average
        const sampleGroups = rngResults.reduce((acc, r) => {
          if (!acc[r.samples_count]) {
            acc[r.samples_count] = {
              passedCount: 0,
              totalCount: 0,
              scoreSum: 0,
            };
          }
          acc[r.samples_count].totalCount += 1;
          if (r.passed) acc[r.samples_count].passedCount += 1;
          acc[r.samples_count].scoreSum += r.score;
          return acc;
        }, {} as Record<number, { passedCount: number; totalCount: number; scoreSum: number }>);

        const data = Object.entries(sampleGroups)
          .map(([samples, data]) => ({
            samples: parseInt(samples),
            passRate: (data.passedCount / data.totalCount) * 100,
            score: data.scoreSum / data.totalCount,
          }))
          .sort((a, b) => a.samples - b.samples);

        return {
          rngName: rng.name,
          rngId: rng.id,
          data,
        };
      })
      .filter((r) => r.data.length > 0);

    // Test performance by sample count
    const testPerformanceBySamples = testNames
      .map((testName) => {
        const testResults = results.filter((r) => r.test_name === testName);

        // Group by sample count and average
        const sampleGroups = testResults.reduce((acc, r) => {
          if (!acc[r.samples_count]) {
            acc[r.samples_count] = {
              passedCount: 0,
              totalCount: 0,
              scoreSum: 0,
            };
          }
          acc[r.samples_count].totalCount += 1;
          if (r.passed) acc[r.samples_count].passedCount += 1;
          acc[r.samples_count].scoreSum += r.score;
          return acc;
        }, {} as Record<number, { passedCount: number; totalCount: number; scoreSum: number }>);

        const data = Object.entries(sampleGroups)
          .map(([samples, data]) => ({
            samples: parseInt(samples),
            passRate: (data.passedCount / data.totalCount) * 100,
            score: data.scoreSum / data.totalCount,
          }))
          .sort((a, b) => a.samples - b.samples);

        return {
          testName,
          data,
        };
      })
      .filter((t) => t.data.length > 0);

    // Sample size distribution
    const sampleSizeDistribution = results.reduce((acc, result) => {
      const bucket = Math.floor(result.samples_count / 1000) * 1000;
      const key = `${bucket}-${bucket + 999}`;
      if (!acc[key]) {
        acc[key] = { range: key, count: 0, avgTime: 0, totalTime: 0 };
      }
      acc[key].count += 1;
      acc[key].totalTime += result.execution_time_ms;
      acc[key].avgTime =
        Math.round((acc[key].totalTime / acc[key].count) * 10) / 10;
      return acc;
    }, {} as Record<string, { range: string; count: number; avgTime: number; totalTime: number }>);

    const sampleDistribution = Object.values(sampleSizeDistribution).sort(
      (a, b) => {
        const aStart = parseInt(a.range.split("-")[0]);
        const bStart = parseInt(b.range.split("-")[0]);
        return aStart - bStart;
      }
    );

    return {
      overallPassRate,
      totalTests,
      passedTests,
      activityData,
      performanceData,
      averagedLineData,
      rngComparison,
      testComparison,
      sampleDistribution,
      rngPerformanceBySamples,
      testPerformanceBySamples,
    };
  }, [results, rngs, selectedRng, selectedTest]);

  if (loading) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <Loading message="Loading Dashboard..." fullScreen />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <ErrorComponent />
      </div>
    );
  }

  if (!statistics || results.length === 0) {
    return (
      <div className="container mx-auto p-8">
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
          <AlertCircle className="h-16 w-16 text-muted-foreground mb-4" />
          <h2 className="text-2xl font-bold mb-2">No Test Results Available</h2>
          <p className="text-muted-foreground">
            Run some tests to see analytics and statistics.
          </p>
        </div>
      </div>
    );
  }

  const testNames = [...new Set(results.map((r) => r.test_name))];

  return (
    <div className="container mx-auto p-4 md:p-8 space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-bold mb-2">
          Test Results Dashboard
        </h1>
        <p className="text-muted-foreground text-base md:text-lg">
          Comprehensive analysis of {statistics.totalTests} test executions
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Overall Pass Rate
            </CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl md:text-3xl font-bold">
              {statistics.overallPassRate.toFixed(1)}%
            </div>
            <Progress value={statistics.overallPassRate} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-2">
              {statistics.passedTests} / {statistics.totalTests} tests passed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Algorithms
            </CardTitle>
            <Layers className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl md:text-3xl font-bold">
              {statistics.rngComparison.length}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Tested algorithms
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Test Types</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl md:text-3xl font-bold">
              {statistics.testComparison.length}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Unique test configurations
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">PDF Report</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-2 mt-2">
              <p className="text-xs text-muted-foreground">
                Generate comprehensive PDF with charts & statistics
              </p>
              <ReportGenerator
                data={{
                  summary: {
                    totalTests: statistics.totalTests,
                    passedTests: statistics.passedTests,
                    failedTests: statistics.totalTests - statistics.passedTests,
                    overallPassRate: statistics.overallPassRate,
                    totalAlgorithms: rngs.length,
                    totalTestTypes: testNames.length,
                    avgExecutionTime:
                      results.reduce((acc, r) => acc + r.execution_time_ms, 0) /
                      results.length,
                  },
                  dailyActivity: statistics.activityData,
                  rngComparison: statistics.rngComparison,
                  testComparison: statistics.testComparison,
                  sampleDistribution: statistics.sampleDistribution,
                  rngPerformanceBySamples: statistics.rngPerformanceBySamples,
                  testPerformanceBySamples: statistics.testPerformanceBySamples,
                }}
                results={results}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Activity Chart */}
      <DailyTestActivity data={statistics.activityData} />

      {/* Performance Analysis */}
      <PerformanceVsSampleSize
        performanceData={statistics.performanceData}
        averagedLineData={statistics.averagedLineData}
        selectedRng={selectedRng}
        setSelectedRng={setSelectedRng}
        selectedTest={selectedTest}
        setSelectedTest={setSelectedTest}
        rngs={rngs}
        testNames={testNames}
      />

      {/* RNG vs Test Comparison Dialog */}
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
        <AlgorithmPerformanceDialog
          rngComparison={statistics.rngComparison}
          rngPerformanceBySamples={statistics.rngPerformanceBySamples}
        />

        <TestTypePerformanceDialog
          testComparison={statistics.testComparison}
          testPerformanceBySamples={statistics.testPerformanceBySamples}
        />
      </div>

      {/* Sample Size Distribution */}
      <SampleSizeDistribution data={statistics.sampleDistribution} />

      {/* Hidden charts for PDF generation */}
      <HiddenChartsRenderer
        rngPerformanceBySamples={statistics.rngPerformanceBySamples}
        testPerformanceBySamples={statistics.testPerformanceBySamples}
      />
    </div>
  );
};
