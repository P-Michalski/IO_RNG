import {
  Empty,
  EmptyDescription,
  EmptyMedia,
  EmptyTitle,
  EmptyHeader,
} from "@/components/ui/empty";
import { Button } from "@/components/ui/button";
import { BookDashed, ArrowUpRight } from "lucide-react";
import { Link } from "react-router-dom";

export const NotFound = () => {
  return (
    <div className="flex items-center justify-center min-h-screen w-full">
      <Empty className="max-w-md border border-solid from-muted/50 to-background bg-linear-to-b from-30%">
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <BookDashed />
          </EmptyMedia>
          <EmptyTitle>404 Page Not Found</EmptyTitle>
          <EmptyDescription>
            The page you are looking for does not exist. Please check the URL or
            go back to the homepage.
          </EmptyDescription>
        </EmptyHeader>
        <Button
          variant="link"
          asChild
          className="text-muted-foreground"
          size="sm"
        >
          <Link to="/" rel="noreferrer noopener">
            Return to Dashboard <ArrowUpRight />
          </Link>
        </Button>
      </Empty>
    </div>
  );
};
