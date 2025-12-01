import {
  Empty,
  EmptyDescription,
  EmptyMedia,
  EmptyTitle,
  EmptyHeader,
  EmptyContent,
} from "@/components/ui/empty";
import { TriangleAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Spinner } from "../ui/spinner";

export const Error = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setInterval(() => window.location.reload(), 1000);
  };

  return (
    <div className="flex items-center justify-center min-h-screen w-full">
      <Empty className="max-w-md border border-dashed from-muted/50 to-background bg-linear-to-b from-30%">
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <TriangleAlert />
          </EmptyMedia>
          <EmptyTitle>Error</EmptyTitle>
          <EmptyDescription>
            An internal error has occurred. Please try again later.
          </EmptyDescription>
        </EmptyHeader>

        <EmptyContent>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleRefresh}
              disabled={isRefreshing}
            >
              {isRefreshing ? (
                <>
                  <Spinner /> Refreshing...
                </>
              ) : (
                "Refresh"
              )}
            </Button>
          </div>
        </EmptyContent>
      </Empty>
    </div>
  );
};
