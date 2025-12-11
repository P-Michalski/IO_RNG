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
import { type TestResult } from "@/types/test-results";
import { CheckCircle2, XCircle, Clock, Hash, ChevronRight } from "lucide-react";

interface TestResultCardProps {
  result: TestResult;
  rngName: string;
}

export const TestResultCard = ({ result, rngName }: TestResultCardProps) => {
  const [open, setOpen] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatTestName = (name: string) => {
    return name
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Card className="hover:border-primary transition-colors cursor-pointer">
        <DialogTrigger asChild>
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
                <Badge variant={result.passed ? "default" : "destructive"}>
                  {result.passed ? "Passed" : "Failed"}
                </Badge>
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

              <Button
                variant="ghost"
                className="w-full mt-4 justify-between"
                size="sm"
              >
                View Details
                <ChevronRight className="h-4 w-4" />
              </Button>
            </CardContent>
          </div>
        </DialogTrigger>
      </Card>

      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
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
              <p className="text-lg font-semibold">{result.score.toFixed(2)}</p>
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
                  <span className="text-sm text-muted-foreground">
                    {key
                      .split("_")
                      .map(
                        (word) => word.charAt(0).toUpperCase() + word.slice(1)
                      )
                      .join(" ")}
                  </span>
                  <span className="text-sm font-medium">
                    {Array.isArray(value)
                      ? `[${value.length} values]`
                      : typeof value === "number"
                      ? value.toFixed(6)
                      : value}
                  </span>
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
      </DialogContent>
    </Dialog>
  );
};
