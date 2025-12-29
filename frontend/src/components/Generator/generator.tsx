import { useState, useEffect } from "react";
import { Binary, Hash } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loading } from "../Loading/loading";
import { Error as ErrorComponent } from "../Error/error";
import { BitGenerator } from "./BitGenerator/bit-generator";
import { NumberGenerator } from "./NumberGenerator/number-generator";

export const Generator = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/rngs", {
          method: "GET",
        });

        if (!response.ok) {
          throw new Error("Backend API is not responding");
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to connect to backend"
        );
      } finally {
        setLoading(false);
      }
    };

    checkBackendConnection();
  }, []);

  if (loading) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <Loading message="Connecting to backend..." fullScreen />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container flex items-center justify-center min-h-screen mx-auto p-6">
        <ErrorComponent
          title="Backend Connection Error"
          description={`Failed to connect to the backend API: ${error}. Please make sure the backend server is running on http://localhost:8000`}
        />
      </div>
    );
  }

  return (
    <div className="container p-8 mx-auto overflow-hidden max-w-2xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          RNG Generator
        </h1>
        <p className="text-muted-foreground">
          Generate random bits or numbers using various algorithms
        </p>
      </div>

      <Tabs defaultValue="bits" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="bits" className="flex items-center gap-2">
            <Binary className="h-4 w-4" />
            Bits
          </TabsTrigger>
          <TabsTrigger value="numbers" className="flex items-center gap-2">
            <Hash className="h-4 w-4" />
            Numbers
          </TabsTrigger>
        </TabsList>

        <TabsContent value="bits" className="mt-6">
          <BitGenerator />
        </TabsContent>

        <TabsContent value="numbers" className="mt-6">
          <NumberGenerator />
        </TabsContent>
      </Tabs>
    </div>
  );
};
