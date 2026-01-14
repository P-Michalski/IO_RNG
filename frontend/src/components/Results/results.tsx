import { useState, useEffect, useMemo } from "react";
import { NoResults } from "./NoResults/no-results";
import { TestResultCard } from "./test-result-card";
import { type TestResult, type RNG } from "@/types/test-results";
import { Loading } from "../Loading/loading";
import { Error as ErrorComponent } from "../Error/error";
import { toast } from "sonner";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { X, Trash2 } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

export const Results = () => {
  const [results, setResults] = useState<TestResult[]>([]);
  const [rngs, setRngs] = useState<RNG[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [selectedTest, setSelectedTest] = useState<string>("all");
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [resultsPerPage, setResultsPerPage] = useState(10);

  // Multi-select state
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [resultsRes, rngsRes] = await Promise.all([
        fetch("http://localhost:8000/api/test-results"),
        fetch("http://localhost:8000/api/rngs"),
      ]);

      if (!resultsRes.ok || !rngsRes.ok) {
        throw new Error("Failed to fetch data");
      }

      const resultsData = await resultsRes.json();
      const rngsData = await rngsRes.json();

      setResults(resultsData);
      setRngs(rngsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      toast.error("Failed to load results. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Helper function to get RNG name
  const getRngName = (rngId: number) => {
    const rng = rngs.find((r) => r.id === rngId);
    return rng?.name || `RNG #${rngId}`;
  };

  // Get unique tests and algorithms from results
  const availableTests = useMemo(() => {
    const tests = new Set(results.map((r) => r.test_name));
    return Array.from(tests).sort();
  }, [results]);

  const availableAlgorithms = useMemo(() => {
    const algorithms = new Set(results.map((r) => r.rng_id));
    return Array.from(algorithms)
      .map((id) => ({
        id,
        name: getRngName(id),
      }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [results, rngs]);

  // Get filtered results
  const filteredResults = useMemo(() => {
    return results.filter((result) => {
      if (selectedTest !== "all" && result.test_name !== selectedTest) {
        return false;
      }
      if (
        selectedAlgorithm !== "all" &&
        result.rng_id !== Number(selectedAlgorithm)
      ) {
        return false;
      }
      if (selectedStatus !== "all") {
        if (selectedStatus === "passed" && !result.passed) return false;
        if (selectedStatus === "failed" && result.passed) return false;
      }
      return true;
    });
  }, [results, selectedTest, selectedAlgorithm, selectedStatus]);

  // Get tests available for selected algorithm
  const getAvailableTestsForAlgorithm = useMemo(() => {
    if (selectedAlgorithm === "all") return new Set(availableTests);
    return new Set(
      results
        .filter((r) => r.rng_id === Number(selectedAlgorithm))
        .map((r) => r.test_name)
    );
  }, [results, selectedAlgorithm, availableTests]);

  // Get algorithms available for selected test
  const getAvailableAlgorithmsForTest = useMemo(() => {
    if (selectedTest === "all")
      return new Set(availableAlgorithms.map((a) => a.id));
    return new Set(
      results.filter((r) => r.test_name === selectedTest).map((r) => r.rng_id)
    );
  }, [results, selectedTest, availableAlgorithms]);

  // Pagination
  const totalPages = Math.ceil(filteredResults.length / resultsPerPage);
  const startIndex = (currentPage - 1) * resultsPerPage;
  const paginatedResults = filteredResults.slice(
    startIndex,
    startIndex + resultsPerPage
  );

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedTest, selectedAlgorithm, selectedStatus, resultsPerPage]);

  const clearFilters = () => {
    setSelectedTest("all");
    setSelectedAlgorithm("all");
    setSelectedStatus("all");
    setCurrentPage(1);
  };

  const hasActiveFilters =
    selectedTest !== "all" ||
    selectedAlgorithm !== "all" ||
    selectedStatus !== "all";

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const handleBulkDelete = async () => {
    const deletePromises = Array.from(selectedIds).map((id) =>
      fetch(`http://localhost:8000/api/test-results/${id}`, {
        method: "DELETE",
      })
    );

    try {
      await Promise.all(deletePromises);
      toast.success(`${selectedIds.size} test result(s) deleted successfully`);
      setResults((prev) => prev.filter((r) => !selectedIds.has(r.id)));
      setSelectedIds(new Set());
      setBulkDeleteOpen(false);
    } catch (error) {
      console.error("Error deleting test results:", error);
      toast.error("Failed to delete some test results");
      setBulkDeleteOpen(false);
    }
  };

  const handleDelete = (id: number) => {
    setResults((prevResults) =>
      prevResults.filter((result) => result.id !== id)
    );
    setSelectedIds((prev) => {
      const newSet = new Set(prev);
      newSet.delete(id);
      return newSet;
    });
  };

  if (loading) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <Loading message="Loading Results..." fullScreen />
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

  if (results.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen w-full">
        <NoResults />
      </div>
    );
  }

  const formatTestName = (name: string) => {
    return name
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const renderPaginationItems = () => {
    const items = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink
              onClick={() => setCurrentPage(i)}
              isActive={currentPage === i}
            >
              {i}
            </PaginationLink>
          </PaginationItem>
        );
      }
    } else {
      // Always show first page
      items.push(
        <PaginationItem key={1}>
          <PaginationLink
            onClick={() => setCurrentPage(1)}
            isActive={currentPage === 1}
          >
            1
          </PaginationLink>
        </PaginationItem>
      );

      if (currentPage > 3) {
        items.push(<PaginationEllipsis key="ellipsis-start" />);
      }

      // Show pages around current
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink
              onClick={() => setCurrentPage(i)}
              isActive={currentPage === i}
            >
              {i}
            </PaginationLink>
          </PaginationItem>
        );
      }

      if (currentPage < totalPages - 2) {
        items.push(<PaginationEllipsis key="ellipsis-end" />);
      }

      // Always show last page
      items.push(
        <PaginationItem key={totalPages}>
          <PaginationLink
            onClick={() => setCurrentPage(totalPages)}
            isActive={currentPage === totalPages}
          >
            {totalPages}
          </PaginationLink>
        </PaginationItem>
      );
    }

    return items;
  };

  return (
    <div className="container mx-auto p-4 md:p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Test Results</h1>
        <p className="text-muted-foreground">
          View and analyze your RNG test results
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-end gap-4">
          <div className="flex-1 grid gap-3 grid-cols-2 lg:grid-cols-4">
            {/* Test Filter */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">
                Test Type
              </label>
              <Select value={selectedTest} onValueChange={setSelectedTest}>
                <SelectTrigger className="h-9 w-full">
                  <SelectValue placeholder="All Tests" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Tests</SelectItem>
                  {availableTests.map((test) => {
                    const isDisabled =
                      selectedAlgorithm !== "all" &&
                      !getAvailableTestsForAlgorithm.has(test);
                    return (
                      <SelectItem key={test} value={test} disabled={isDisabled}>
                        {formatTestName(test)}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>

            {/* Algorithm Filter */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">
                Algorithm
              </label>
              <Select
                value={selectedAlgorithm}
                onValueChange={setSelectedAlgorithm}
              >
                <SelectTrigger className="h-9 w-full">
                  <SelectValue placeholder="All Algorithms" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Algorithms</SelectItem>
                  {availableAlgorithms.map((algo) => {
                    const isDisabled =
                      selectedTest !== "all" &&
                      !getAvailableAlgorithmsForTest.has(algo.id);
                    return (
                      <SelectItem
                        key={algo.id}
                        value={String(algo.id)}
                        disabled={isDisabled}
                      >
                        {algo.name}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>

            {/* Status Filter */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">
                Status
              </label>
              <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                <SelectTrigger className="h-9 w-full">
                  <SelectValue placeholder="All Results" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="passed">Passed</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Results Per Page */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">
                Per Page
              </label>
              <Select
                value={String(resultsPerPage)}
                onValueChange={(val) => setResultsPerPage(Number(val))}
              >
                <SelectTrigger className="h-9 w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="20">20</SelectItem>
                  <SelectItem value="40">40</SelectItem>
                  <SelectItem value="80">80</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Filter Actions */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <p className="text-sm text-muted-foreground">
              Showing {startIndex + 1}-
              {Math.min(startIndex + resultsPerPage, filteredResults.length)} of{" "}
              {filteredResults.length} results
            </p>
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="gap-2"
              >
                <X className="h-4 w-4" />
                Clear Filters
              </Button>
            )}
          </div>

          {selectedIds.size > 0 && (
            <AlertDialog open={bulkDeleteOpen} onOpenChange={setBulkDeleteOpen}>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setBulkDeleteOpen(true)}
                className="gap-2"
              >
                <Trash2 className="h-4 w-4" />
                Delete ({selectedIds.size})
              </Button>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>
                    Delete {selectedIds.size} test result
                    {selectedIds.size > 1 ? "s" : ""}?
                  </AlertDialogTitle>
                  <AlertDialogDescription>
                    This action cannot be undone. This will permanently delete
                    the selected test result{selectedIds.size > 1 ? "s" : ""}{" "}
                    and remove {selectedIds.size > 1 ? "them" : "it"} from the
                    database.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleBulkDelete}>
                    Delete
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          )}
        </div>
      </div>

      {/* Results Grid */}
      {filteredResults.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground text-lg mb-4">
            No results match your filters
          </p>
          <Button variant="outline" onClick={clearFilters}>
            Clear Filters
          </Button>
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 mb-8">
            {paginatedResults.map((result) => (
              <TestResultCard
                key={result.id}
                result={result}
                rngName={getRngName(result.rng_id)}
                onDelete={handleDelete}
                isSelected={selectedIds.has(result.id)}
                onToggleSelect={() => toggleSelect(result.id)}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    className={
                      currentPage === 1 ? "pointer-events-none opacity-50" : ""
                    }
                  />
                </PaginationItem>

                {renderPaginationItems()}

                <PaginationItem>
                  <PaginationNext
                    onClick={() =>
                      setCurrentPage((p) => Math.min(totalPages, p + 1))
                    }
                    className={
                      currentPage === totalPages
                        ? "pointer-events-none opacity-50"
                        : ""
                    }
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          )}
        </>
      )}
    </div>
  );
};
