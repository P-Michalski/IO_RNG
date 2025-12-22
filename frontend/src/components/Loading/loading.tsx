import { Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface LoadingProps {
  message?: string;
  fullScreen?: boolean;
  size?: "sm" | "md" | "lg";
}

export const Loading = ({
  message = "Loading...",
  fullScreen = false,
  size = "md",
}: LoadingProps) => {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12",
  };

  const content = (
    <Card className="border-none shadow-none">
      <CardContent className="flex flex-col items-center justify-center p-6 space-y-4">
        <Loader2 className={`${sizeClasses[size]} animate-spin text-primary`} />
        <p className="text-sm text-muted-foreground">{message}</p>
      </CardContent>
    </Card>
  );

  if (fullScreen) {
    return (
      <div className="flex items-center justify-center min-h-screen w-full">
        {content}
      </div>
    );
  }

  return content;
};
