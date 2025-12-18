import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, Play, RotateCcw } from "lucide-react";

export function ThemeShowcase() {
  return (
    <div className="space-y-4">
      {/* Loading State */}
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-full max-w-[200px]" />
          <Skeleton className="h-4 w-full max-w-[280px]" />
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </CardContent>
      </Card>

      {/* Test Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Test Configuration</CardTitle>
          <CardDescription>
            Configure parameters for RNG statistical tests
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="sample-size">Sample Size</Label>
              <Input
                id="sample-size"
                type="number"
                placeholder="1000000"
                defaultValue="1000000"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="seed">Seed Value</Label>
              <Input
                id="seed"
                type="number"
                placeholder="42"
                defaultValue="42"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Statistical Tests</Label>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox id="chi-square" defaultChecked />
                <Label
                  htmlFor="chi-square"
                  className="text-sm font-normal leading-none"
                >
                  Chi-Square Test
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox id="runs-test" />
                <Label
                  htmlFor="runs-test"
                  className="text-sm font-normal leading-none"
                >
                  Runs Test
                </Label>
              </div>
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex flex-col sm:flex-row gap-2">
          <Button variant="outline" className="w-full sm:flex-1">
            <RotateCcw className="mr-2 h-4 w-4" />
            Reset
          </Button>
          <Button className="w-full sm:flex-1">
            <Play className="mr-2 h-4 w-4" />
            Run Tests
          </Button>
        </CardFooter>
      </Card>

      {/* Algorithm Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Random Number Generator</CardTitle>
          <CardDescription>
            Select a pseudorandom number generator algorithm
          </CardDescription>
        </CardHeader>
        <CardContent>
          <RadioGroup defaultValue="xoshiro256" className="space-y-1">
            <label
              htmlFor="xoshiro256"
              className="flex items-center gap-3 rounded-lg border p-4 cursor-pointer transition-colors hover:bg-accent/50 has-data-[state=checked]:bg-primary/5 has-data-[state=checked]:border-primary dark:has-data-[state=checked]:bg-primary/10"
            >
              <RadioGroupItem value="xoshiro256" id="xoshiro256" />
              <div className="flex-1 min-w-0 space-y-1">
                <div className="text-sm font-medium leading-none">
                  Xoshiro256**
                </div>
                <p className="text-sm text-muted-foreground">
                  Fast, high-quality generator. Recommended for most
                  applications.
                </p>
              </div>
              <Badge className="hidden sm:inline-flex">Recommended</Badge>
            </label>

            <label
              htmlFor="chacha20"
              className="flex items-center gap-3 rounded-lg border p-4 cursor-pointer transition-colors hover:bg-accent/50 has-data-[state=checked]:bg-primary/5 has-data-[state=checked]:border-primary dark:has-data-[state=checked]:bg-primary/10"
            >
              <RadioGroupItem value="chacha20" id="chacha20" />
              <div className="flex-1 min-w-0 space-y-1">
                <div className="text-sm font-medium leading-none">ChaCha20</div>
                <p className="text-sm text-muted-foreground">
                  Cryptographically secure stream cipher suitable for security
                  applications.
                </p>
              </div>
              <Badge variant="secondary" className="hidden sm:inline-flex">
                Secure
              </Badge>
            </label>

            <label
              htmlFor="lcg"
              className="flex items-center gap-3 rounded-lg border p-4 cursor-pointer transition-colors hover:bg-accent/50 has-data-[state=checked]:bg-primary/5 has-data-[state=checked]:border-primary dark:has-data-[state=checked]:bg-primary/10"
            >
              <RadioGroupItem value="lcg" id="lcg" />
              <div className="flex-1 min-w-0 space-y-1">
                <div className="text-sm font-medium leading-none">
                  Linear Congruential Generator
                </div>
                <p className="text-sm text-muted-foreground">
                  Simple and fast, but limited statistical quality. For
                  educational purposes.
                </p>
              </div>
              <Badge variant="outline" className="hidden sm:inline-flex">
                Legacy
              </Badge>
            </label>
          </RadioGroup>
        </CardContent>
        <CardFooter>
          <Button className="w-full">
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Generating Results...
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
