export interface ReportData {
  // Metadata
  generatedAt: Date;
  testPeriod: {
    from: Date;
    to: Date;
  };

  // Overall statistics
  summary: {
    totalTests: number;
    passedTests: number;
    failedTests: number;
    overallPassRate: number;
    totalAlgorithms: number;
    totalTestTypes: number;
    avgExecutionTime: number;
  };

  // Daily activity
  dailyActivity: Array<{
    date: string;
    passed: number;
    failed: number;
    total: number;
  }>;

  // RNG comparison
  rngComparison: Array<{
    name: string;
    passRate: number;
    avgTime: number;
    totalTests: number;
    avgScore: number;
  }>;

  // Test type comparison
  testComparison: Array<{
    name: string;
    passRate: number;
    avgTime: number;
    totalTests: number;
    avgScore: number;
  }>;

  // Sample size distribution
  sampleDistribution: Array<{
    range: string;
    count: number;
    avgTime: number;
  }>;

  // RNG performance trends
  rngPerformanceBySamples: Array<{
    rngName: string;
    rngId: number;
    data: Array<{
      samples: number;
      passRate: number;
      score: number;
    }>;
  }>;

  // Test performance trends
  testPerformanceBySamples: Array<{
    testName: string;
    data: Array<{
      samples: number;
      passRate: number;
      score: number;
    }>;
  }>;

  // Chart images (base64)
  chartImages?: {
    dailyActivity?: string;
    performanceVsSampleSize?: string;
    sampleDistribution?: string;
    rngComparison?: string;
    testComparison?: string;
  };
}
