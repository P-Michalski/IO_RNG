import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import {
  FileText,
  Download,
  Loader2,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { generatePDFReport } from "./PDFReport";
import type { ReportData } from "./types";
import { chartsToImages, waitForChartRender } from "./chartToImage";
import { toast } from "sonner";

interface ReportGeneratorProps {
  data: Omit<ReportData, "generatedAt" | "testPeriod" | "chartImages">;
  results: any[]; // TestResult array from context
}

export const ReportGenerator: React.FC<ReportGeneratorProps> = ({
  data,
  results,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<
    "idle" | "preparing" | "charts" | "generating" | "success" | "error"
  >("idle");
  const [error, setError] = useState<string | null>(null);

  // Refs for chart elements - will be populated from parent component
  const chartRefs = useRef<Record<string, HTMLElement>>({});

  const handleGenerateReport = async () => {
    try {
      setIsGenerating(true);
      setProgress(0);
      setStatus("preparing");
      setError(null);

      // Step 1: Prepare data (10%)
      setProgress(10);
      await new Promise((resolve) => setTimeout(resolve, 300));

      // Calculate test period
      const dates = results.map((r) => new Date(r.created_at));
      const testPeriod = {
        from: new Date(Math.min(...dates.map((d) => d.getTime()))),
        to: new Date(Math.max(...dates.map((d) => d.getTime()))),
      };

      // Step 2: Capture charts (30%)
      setStatus("charts");
      setProgress(30);

      // Wait for charts to fully render
      await waitForChartRender(800);

      // Collect chart elements
      const chartElements: Array<{ id: string; element: HTMLElement }> = [];

      // Try to find charts by common selectors
      const performanceChart = document.querySelector(
        '[data-chart-id="performance-vs-sample"]'
      ) as HTMLElement;
      const sampleDistChart = document.querySelector(
        '[data-chart-id="sample-distribution"]'
      ) as HTMLElement;

      if (performanceChart) {
        chartElements.push({
          id: "performanceVsSampleSize",
          element: performanceChart,
        });
      }
      if (sampleDistChart) {
        chartElements.push({
          id: "sampleDistribution",
          element: sampleDistChart,
        });
      }

      setProgress(40);

      // Collect dynamic trend charts for algorithms
      const algorithmTrendElements = document.querySelectorAll(
        '[data-chart-id^="algorithm-trend-"]'
      );
      const algorithmTrends: Array<{
        id: string;
        title: string;
        image: string;
      }> = [];

      // Collect dynamic trend charts for tests
      const testTrendElements = document.querySelectorAll(
        '[data-chart-id^="test-trend-"]'
      );
      const testTrends: Array<{ id: string; title: string; image: string }> =
        [];

      setProgress(50);

      // Convert charts to images
      let chartImages: any = {};
      if (chartElements.length > 0) {
        try {
          chartImages = await chartsToImages(chartElements, {
            scale: 2,
            backgroundColor: "#ffffff",
          });
        } catch (chartError) {
          console.warn("Could not capture some charts:", chartError);
          // Continue without charts
        }
      }

      setProgress(60);

      // Convert algorithm trend charts
      if (algorithmTrendElements.length > 0) {
        try {
          for (const element of Array.from(algorithmTrendElements)) {
            const htmlElement = element as HTMLElement;
            const chartId = htmlElement.getAttribute("data-chart-id") || "";
            const chartTitle =
              htmlElement.getAttribute("data-chart-title") || "";

            const image = await chartsToImages(
              [{ id: chartId, element: htmlElement }],
              { scale: 2, backgroundColor: "#ffffff" }
            );

            algorithmTrends.push({
              id: chartId,
              title: chartTitle,
              image: image[chartId],
            });
          }
        } catch (error) {
          console.warn("Could not capture algorithm trend charts:", error);
        }
      }

      setProgress(65);

      // Convert test trend charts
      if (testTrendElements.length > 0) {
        try {
          for (const element of Array.from(testTrendElements)) {
            const htmlElement = element as HTMLElement;
            const chartId = htmlElement.getAttribute("data-chart-id") || "";
            const chartTitle =
              htmlElement.getAttribute("data-chart-title") || "";

            const image = await chartsToImages(
              [{ id: chartId, element: htmlElement }],
              { scale: 2, backgroundColor: "#ffffff" }
            );

            testTrends.push({
              id: chartId,
              title: chartTitle,
              image: image[chartId],
            });
          }
        } catch (error) {
          console.warn("Could not capture test trend charts:", error);
        }
      }

      // Add trend charts to chartImages
      if (algorithmTrends.length > 0) {
        chartImages.algorithmTrends = algorithmTrends;
      }
      if (testTrends.length > 0) {
        chartImages.testTrends = testTrends;
      }

      // Get chart colors from CSS variables
      // Create canvas element to properly convert oklch colors to hex
      const getColorAsHex = (varName: string): string => {
        const canvas = document.createElement("canvas");
        canvas.width = 1;
        canvas.height = 1;
        const ctx = canvas.getContext("2d");
        if (!ctx) return "#3b82f6";

        // Get the CSS variable value
        const rootStyles = getComputedStyle(document.documentElement);
        const colorValue = rootStyles.getPropertyValue(varName).trim();

        // Draw with the color and read back the RGB value
        ctx.fillStyle = colorValue;
        ctx.fillRect(0, 0, 1, 1);
        const imageData = ctx.getImageData(0, 0, 1, 1).data;

        // Convert to hex
        const r = imageData[0];
        const g = imageData[1];
        const b = imageData[2];
        return `#${((1 << 24) + (r << 16) + (g << 8) + b)
          .toString(16)
          .slice(1)}`;
      };

      chartImages.chartColors = {
        chart1: getColorAsHex("--chart-1"),
        chart2: getColorAsHex("--chart-2"),
      };

      // Get theme colors
      chartImages.themeColors = {
        primary: getColorAsHex("--primary"),
        primaryForeground: getColorAsHex("--primary-foreground"),
        muted: getColorAsHex("--muted"),
        border: getColorAsHex("--border"),
      };

      setProgress(70);

      // Step 3: Generate PDF (20%)
      setStatus("generating");

      const reportData: ReportData = {
        ...data,
        generatedAt: new Date(),
        testPeriod,
        chartImages,
      };

      await generatePDFReport(
        reportData,
        `rng-test-report-${new Date().toISOString().split("T")[0]}.pdf`
      );

      setProgress(100);
      setStatus("success");

      toast.success("Report Generated", {
        description: "PDF report has been downloaded successfully.",
      });

      // Reset after 2 seconds
      setTimeout(() => {
        setIsGenerating(false);
        setStatus("idle");
        setProgress(0);
      }, 2000);
    } catch (err) {
      console.error("Error generating report:", err);
      setStatus("error");
      setError(err instanceof Error ? err.message : "Unknown error");

      toast.error("Report Generation Failed", {
        description: "Could not generate PDF report. Please try again.",
      });

      // Reset after 3 seconds
      setTimeout(() => {
        setIsGenerating(false);
        setStatus("idle");
        setProgress(0);
        setError(null);
      }, 3000);
    }
  };

  const getStatusMessage = () => {
    switch (status) {
      case "preparing":
        return "Preparing data...";
      case "charts":
        return "Capturing charts...";
      case "generating":
        return "Generating PDF...";
      case "success":
        return "Report generated successfully!";
      case "error":
        return error || "Error generating report";
      default:
        return "Ready to generate";
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case "success":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "error":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "idle":
        return <FileText className="h-5 w-5" />;
      default:
        return <Loader2 className="h-5 w-5 animate-spin" />;
    }
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="whitespace-normal h-auto py-2"
        >
          <FileText className="mr-2 h-4 w-4 shrink-0" />
          <span className="wrap-break-word">Generate Report</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Generate PDF Report</DialogTitle>
          <DialogDescription>
            Create a comprehensive PDF report with all test statistics and
            charts.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Status */}
          <div className="flex items-center gap-3">
            {getStatusIcon()}
            <span className="text-sm text-muted-foreground">
              {getStatusMessage()}
            </span>
          </div>

          {/* Progress bar */}
          {isGenerating && (
            <div className="space-y-2">
              <Progress value={progress} className="h-2" />
              <p className="text-xs text-center text-muted-foreground">
                {progress}%
              </p>
            </div>
          )}

          {/* Report info */}
          {!isGenerating && status === "idle" && (
            <div className="rounded-lg bg-muted p-4 space-y-2">
              <p className="text-sm font-medium">Report will include:</p>
              <ul className="text-xs text-muted-foreground space-y-1 ml-4 list-disc">
                <li>Executive summary with key metrics</li>
                <li>Algorithm performance analysis & comparison</li>
                <li>Test type performance breakdown</li>
                <li>Sample size distribution</li>
                <li>Performance trends across sample sizes</li>
                <li>Detailed tables with all statistics</li>
              </ul>
            </div>
          )}

          {/* Error details */}
          {status === "error" && error && (
            <div className="rounded-lg bg-destructive/10 p-4 text-sm text-destructive">
              {error}
            </div>
          )}

          {/* Generate button */}
          <Button
            onClick={handleGenerateReport}
            disabled={isGenerating}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : status === "success" ? (
              <>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                Generated
              </>
            ) : (
              <>
                <Download className="mr-2 h-4 w-4" />
                Generate Report
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
