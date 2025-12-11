export interface TestResult {
  id: number;
  rng_id: number;
  test_name: string;
  passed: boolean;
  score: number;
  execution_time_ms: number;
  samples_count: number;
  statistics: Record<string, any>;
  error_message: string | null;
  created_at: string;
}

export interface RNG {
  id: number;
  name: string;
  language: string;
  algorithm: string;
  description: string;
  code_path: string;
  parameters: Record<string, any>;
  is_active: boolean;
}
