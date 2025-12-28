import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface TestResult {
  test_name: string;
  duration: number;
  score?: number;
  passed: boolean;
}

export interface TestFormValues {
  input_type: "algorithm" | "custom_bits";
  rng_id?: string;
  custom_bits?: string;
  test_type: "single" | "nist_suite" | "diehard_suite";
  single_test?: "frequency_test" | "uniformity_test";
  nist_tests?: string[];
  diehard_tests?: string[];
  samples_count: number;
  seed: number;
}

export interface TestSession {
  id: string;
  name: string;
  config: TestFormValues;
  status: "idle" | "running" | "completed" | "error" | "cancelled";
  startTime?: number;
  endTime?: number;
  currentTest: number;
  totalTests: number;
  results: TestResult[];
  resultsSeen?: boolean;
  abortController?: AbortController;
}

interface TestStore {
  sessions: TestSession[];
  activeTab: string;
  setActiveTab: (id: string) => void;
  addSession: (session?: Partial<TestSession>) => void;
  removeSession: (id: string) => void;
  updateSession: (id: string, updates: Partial<TestSession>) => void;
  updateSessionConfig: (id: string, config: TestFormValues) => void;
  addTestResult: (sessionId: string, result: TestResult) => void;
  setSessionStatus: (
    id: string,
    status: TestSession["status"],
    updates?: Partial<TestSession>
  ) => void;
  incrementCurrentTest: (id: string) => void;
  resetSession: (id: string) => void;
  markResultsSeen: (id: string) => void;
  cancelSession: (id: string) => void;
}

const defaultConfig: TestFormValues = {
  input_type: "algorithm",
  rng_id: "",
  custom_bits: "",
  test_type: "single",
  single_test: "frequency_test",
  nist_tests: [],
  diehard_tests: [],
  samples_count: 100000,
  seed: 42,
};

export const useTestStore = create<TestStore>()(
  persist(
    (set, get) => ({
      sessions: [
        {
          id: "1",
          name: "Test 1",
          config: defaultConfig,
          status: "idle",
          currentTest: 0,
          totalTests: 0,
          results: [],
          resultsSeen: false,
        },
      ],
      activeTab: "1",

      setActiveTab: (id) => set({ activeTab: id }),

      addSession: (sessionData) => {
        const sessions = get().sessions;
        // Find the first available ID (starting from 1)
        let newId = 1;
        const existingIds = new Set(sessions.map((s) => parseInt(s.id)));

        while (existingIds.has(newId)) {
          newId++;
        }

        const newIdString = newId.toString();

        const newSession: TestSession = {
          id: newIdString,
          name: sessionData?.name || `Test ${newId}`,
          config: sessionData?.config || defaultConfig,
          status: "idle",
          currentTest: 0,
          totalTests: 0,
          results: [],
          resultsSeen: false,
          ...sessionData,
        };
        set({
          sessions: [...sessions, newSession],
          activeTab: newIdString,
        });
      },

      updateSession: (id, updates) =>
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === id ? { ...s, ...updates } : s
          ),
        })),

      updateSessionConfig: (id, config) =>
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === id ? { ...s, config } : s
          ),
        })),

      addTestResult: (sessionId, result) =>
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === sessionId ? { ...s, results: [...s.results, result] } : s
          ),
        })),

      setSessionStatus: (id, status, updates = {}) =>
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === id
              ? {
                  ...s,
                  status,
                  // Reset resultsSeen when starting new tests
                  resultsSeen: status === "running" ? false : s.resultsSeen,
                  // Create new AbortController when starting tests
                  abortController:
                    status === "running"
                      ? new AbortController()
                      : s.abortController,
                  ...updates,
                }
              : s
          ),
        })),

      cancelSession: (id) => {
        const session = get().sessions.find((s) => s.id === id);
        if (session?.abortController) {
          // Abort all pending requests
          session.abortController.abort();
        }

        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === id
              ? {
                  ...s,
                  status: "cancelled" as const,
                  endTime: Date.now(),
                  abortController: undefined,
                }
              : s
          ),
        }));
      },

      removeSession: (id) => {
        const sessions = get().sessions;
        if (sessions.length === 1) return;

        // Cancel session if it's running
        const session = sessions.find((s) => s.id === id);
        if (session?.status === "running") {
          get().cancelSession(id);
        }

        const filteredSessions = sessions.filter((s) => s.id !== id);
        const activeTab = get().activeTab;

        if (activeTab === id) {
          const index = sessions.findIndex((s) => s.id === id);
          const newActiveTab = sessions[index === 0 ? 1 : index - 1].id;
          set({
            sessions: filteredSessions,
            activeTab: newActiveTab,
          });
        } else {
          set({ sessions: filteredSessions });
        }
      },

      incrementCurrentTest: (id) =>
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === id ? { ...s, currentTest: s.currentTest + 1 } : s
          ),
        })),

      resetSession: (id) =>
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === id
              ? {
                  ...s,
                  status: "idle" as const,
                  currentTest: 0,
                  totalTests: 0,
                  results: [],
                  startTime: undefined,
                  endTime: undefined,
                  resultsSeen: false,
                }
              : s
          ),
        })),

      markResultsSeen: (id) =>
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === id ? { ...s, resultsSeen: true } : s
          ),
        })),
    }),
    {
      name: "test-sessions-storage",
      partialize: (state) => ({
        sessions: state.sessions.map((s) => ({
          ...s,

          status: s.status === "running" ? "cancelled" : s.status,
          abortController: undefined,
        })),
        activeTab: state.activeTab,
      }),
    }
  )
);
