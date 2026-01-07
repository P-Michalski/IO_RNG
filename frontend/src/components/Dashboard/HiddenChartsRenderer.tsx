/**
 * Hidden component that renders trend charts for PDF capture
 * This is mounted during PDF generation to make charts available in DOM
 */
import { PerformanceTrendsChart } from "./PerformanceTrendsChart";

interface HiddenChartsRendererProps {
  rngPerformanceBySamples: Array<{
    rngName: string;
    rngId: number;
    data: Array<{ samples: number; passRate: number; score: number }>;
  }>;
  testPerformanceBySamples: Array<{
    testName: string;
    data: Array<{ samples: number; passRate: number; score: number }>;
  }>;
}

export const HiddenChartsRenderer = ({
  rngPerformanceBySamples,
  testPerformanceBySamples,
}: HiddenChartsRendererProps) => {
  return (
    <div
      className="fixed left-[-9999px] top-0 w-[800px]"
      aria-hidden="true"
      style={{ pointerEvents: "none" }}
    >
      {/* Algorithm trend charts */}
      {rngPerformanceBySamples.map((rng, idx) => (
        <div key={idx} className="mb-4">
          <PerformanceTrendsChart
            title={rng.rngName}
            data={rng.data}
            chartId={`algorithm-trend-${rng.rngId}`}
          />
        </div>
      ))}

      {/* Test type trend charts */}
      {testPerformanceBySamples.map((test, idx) => (
        <div key={idx} className="mb-4">
          <PerformanceTrendsChart
            title={test.testName}
            data={test.data}
            chartId={`test-trend-${idx}`}
          />
        </div>
      ))}
    </div>
  );
};
