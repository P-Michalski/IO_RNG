import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyMedia,
  EmptyTitle,
  EmptyHeader,
} from "@/components/ui/empty";
import { Button } from "@/components/ui/button";
import { ArrowUpRightIcon, FlaskConicalOff } from "lucide-react";
import { Link } from "react-router-dom";

export const NoResults = () => {
  return (
    <Empty className="max-w-md border border-dashed from-muted/50 to-background bg-linear-to-b from-30%">
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <FlaskConicalOff />
        </EmptyMedia>
        <EmptyTitle>No Tests Results Yet</EmptyTitle>
        <EmptyDescription>
          You haven&apos;t made any tests yet. Get started by creating your
          first test.
        </EmptyDescription>
      </EmptyHeader>

      <EmptyContent>
        <div className="flex gap-2">
          {/* Need to add button functionality later on */}
          <Button>Create Test</Button>
          <Button variant="outline">Import Test</Button>
        </div>
      </EmptyContent>
      <Button
        variant="link"
        asChild
        className="text-muted-foreground"
        size="sm"
      >
        <Link to="/wiki/methodology" rel="noreferrer noopener">
          Learn More <ArrowUpRightIcon />
        </Link>
      </Button>
    </Empty>
  );
};
