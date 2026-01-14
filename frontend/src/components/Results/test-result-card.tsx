import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { type TestResult } from "@/types/test-results";
import {
  CheckCircle2,
  XCircle,
  Clock,
  Hash,
  ChevronRight,
  X,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";

interface TestResultCardProps {
  result: TestResult;
  rngName: string;
  onDelete?: (id: number) => void;
  isSelected?: boolean;
  onToggleSelect?: () => void;
}

const renderStatisticValue = (value: unknown) => {
  if (value === null || value === undefined) {
    return (
      <span className="text-sm font-medium text-muted-foreground">N/A</span>
    );
  }

  if (Array.isArray(value)) {
    const height = "h-[110px]";
    return (
      <div className={`text-sm font-medium max-${height}`}>
        <ScrollArea className={`${height} pr-6`}>
          <div className="space-y-1 text-right">
            {value.map((val, idx) => (
              <div key={idx} className="flex items-center justify-end gap-2">
                <span>
                  {typeof val === "number" ? val.toFixed(2) : String(val)}
                </span>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>
    );
  }

  if (typeof value === "object") {
    return (
      <div className="text-sm font-medium space-y-1 text-right">
        {Object.entries(value).map(([key, val]) => (
          <div key={key} className="flex items-center justify-end gap-2">
            <span className="text-muted-foreground text-xs">{key}:</span>
            <span>{String(val)}</span>
          </div>
        ))}
      </div>
    );
  }

  if (typeof value === "number") {
    return <span className="text-sm font-medium">{value.toFixed(6)}</span>;
  }

  return <span className="text-sm font-medium">{String(value)}</span>;
};

export const TestResultCard = ({
  result,
  rngName,
  onDelete,
  isSelected = false,
  onToggleSelect,
}: TestResultCardProps) => {
  const [open, setOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [alertOpen, setAlertOpen] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);

    try {
      const response = await fetch(
        `http://localhost:8000/api/test-results/${result.id}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete test result");
      }

      toast.success("Test result deleted successfully");
      setAlertOpen(false);

      onDelete?.(result.id);
    } catch (error) {
      console.error("Error deleting test result:", error);
      toast.error("Failed to delete test result");
    } finally {
      setIsDeleting(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatTestName = (name: string) => {
    return name
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const formatKey = (key: string) => {
    return key
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Card
        className={`hover:border-primary transition-all cursor-pointer ${
          isSelected ? "ring-2 ring-primary border-primary bg-accent" : ""
        }`}
        onClick={onToggleSelect}
      >
        <div className="p-6">
          <CardHeader className="p-0 mb-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                {result.passed ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                ) : (
                  <XCircle className="h-5 w-5 text-destructive" />
                )}
                <CardTitle className="text-lg">
                  {formatTestName(result.test_name)}
                </CardTitle>
              </div>
              <AlertDialog open={alertOpen} onOpenChange={setAlertOpen}>
                <AlertDialogTrigger
                  asChild
                  onClick={(e) => e.stopPropagation()}
                >
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-destructive"
                    disabled={isDeleting}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>
                      Are you absolutely sure?
                    </AlertDialogTitle>
                    <AlertDialogDescription>
                      This action cannot be undone. This will permanently delete
                      this test result and remove it from the database.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel onClick={(e) => e.stopPropagation()}>
                      Cancel
                    </AlertDialogCancel>
                    <AlertDialogAction
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete();
                      }}
                      disabled={isDeleting}
                    >
                      {isDeleting ? "Deleting..." : "Confirm"}
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
            <CardDescription>{rngName}</CardDescription>
          </CardHeader>

          <CardContent className="p-0 space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Score</span>
              <span className="font-medium">{result.score.toFixed(2)}</span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground flex items-center gap-1">
                <Hash className="h-3 w-3" />
                Samples
              </span>
              <span className="font-medium">
                {result.samples_count.toLocaleString()}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Time
              </span>
              <span className="font-medium">
                {result.execution_time_ms.toFixed(2)}ms
              </span>
            </div>

            <DialogTrigger asChild>
              <Button
                variant="ghost"
                className="w-full mt-4 justify-between"
                size="sm"
                onClick={(e) => e.stopPropagation()}
              >
                View Details
                <ChevronRight className="h-4 w-4" />
              </Button>
            </DialogTrigger>
          </CardContent>
        </div>
      </Card>

      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-2">
            {result.passed ? (
              <CheckCircle2 className="h-6 w-6 text-green-500" />
            ) : (
              <XCircle className="h-6 w-6 text-destructive" />
            )}
            <DialogTitle>{formatTestName(result.test_name)}</DialogTitle>
          </div>
          <DialogDescription>{rngName}</DialogDescription>
        </DialogHeader>

        <ScrollArea className="max-h-[calc(80vh-120px)] pr-6">
          <div className="space-y-6 mt-4">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Status</p>
                <Badge variant={result.passed ? "default" : "destructive"}>
                  {result.passed ? "Passed" : "Failed"}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Score</p>
                <p className="text-lg font-semibold">
                  {result.score.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Samples</p>
                <p className="text-lg font-semibold">
                  {result.samples_count.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">
                  Execution Time
                </p>
                <p className="text-lg font-semibold">
                  {result.execution_time_ms.toFixed(2)}ms
                </p>
              </div>
            </div>

            {/* Statistics */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Statistics</h3>
              <div className="rounded-lg border p-4 space-y-2">
                {Object.entries(result.statistics).map(([key, value]) => (
                  <div
                    key={key}
                    className="flex items-center justify-between py-1 border-b last:border-b-0"
                  >
                    <span className="text-sm text-muted-foreground shrink-0">
                      {formatKey(key)}
                    </span>
                    {renderStatisticValue(value)}
                  </div>
                ))}
              </div>
            </div>

            {/* Error Message */}
            {result.error_message && (
              <div>
                <h3 className="text-lg font-semibold mb-3 text-destructive">
                  Error
                </h3>
                <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
                  <p className="text-sm">{result.error_message}</p>
                </div>
              </div>
            )}

            {/* Test Parameters */}
            {result.test_parameters &&
              Object.keys(result.test_parameters).length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">
                    Algorithm Parameters
                  </h3>
                  <div className="rounded-lg border p-4 space-y-2">
                    {Object.entries(result.test_parameters).map(
                      ([key, value]) => (
                        <div
                          key={key}
                          className="flex items-center justify-between py-1 border-b last:border-b-0"
                        >
                          <span className="text-sm text-muted-foreground capitalize">
                            {formatKey(key)}
                          </span>
                          <span className="text-sm font-medium">
                            {typeof value === "object"
                              ? JSON.stringify(value)
                              : String(value)}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}

            {/* Metadata */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Metadata</h3>
              <div className="rounded-lg border p-4 space-y-2">
                <div className="flex items-center justify-between py-1">
                  <span className="text-sm text-muted-foreground">Test ID</span>
                  <span className="text-sm font-medium">#{result.id}</span>
                </div>
                <div className="flex items-center justify-between py-1">
                  <span className="text-sm text-muted-foreground">RNG ID</span>
                  <span className="text-sm font-medium">#{result.rng_id}</span>
                </div>
                <div className="flex items-center justify-between py-1">
                  <span className="text-sm text-muted-foreground">Created</span>
                  <span className="text-sm font-medium">
                    {formatDate(result.created_at)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};
