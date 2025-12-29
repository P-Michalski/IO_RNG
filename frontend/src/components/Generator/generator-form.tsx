import { type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

const ALGORITHM_PARAMS = {
  1: {
    name: "AWCG",
    params: {
      seed: 123456789,
      r: 24,
      s: 10,
      base: 4294967296,
    },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  2: {
    name: "SplitMix64",
    params: { seed: 123456789 },
    defaults: {
      bits_per_value: 64,
      msb_first: 1,
    },
  },
  3: {
    name: "LCG",
    params: {
      seed: 123456789,
      a: 1664525,
      c: 1013904223,
      m: 4294967296,
    },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  4: {
    name: "Park-Miller",
    params: { seed: 123456789 },
    defaults: {
      bits_per_value: 31,
      msb_first: 1,
    },
  },
  5: {
    name: "PCG32",
    params: { initstate: 42, seq: 54 },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  6: {
    name: "Mersenne Twister (Python random)",
    params: { seed: 12345 },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  7: {
    name: "OS /dev/urandom",
    params: {},
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  10: {
    name: "LCG with GLIBC parameters",
    params: {
      seed: 123456789,
      a: 1103515245,
      c: 12345,
      m: 2147483648,
    },
    defaults: {
      bits_per_value: 31,
      msb_first: 1,
    },
  },
  11: {
    name: "AWCG (r=24, s=10)",
    params: {
      seed: 123456789,
      r: 24,
      s: 10,
      base: 4294967296,
    },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
  },
  16: {
    name: "Blum Blum Shub",
    params: { seed: 12345, p: 383, q: 503 },
    defaults: {
      bits_per_value: 1,
      msb_first: 1,
    },
  },
};

export type AlgorithmId = keyof typeof ALGORITHM_PARAMS;
export { ALGORITHM_PARAMS };

interface GeneratorFormProps {
  title: string;
  description: string;
  selectedAlgo: AlgorithmId;
  onAlgorithmChange: (value: string) => void;
  params: Record<string, any>;
  onParamChange: (key: string, value: string) => void;
  useDefaults: boolean;
  onUseDefaultsChange: (checked: boolean) => void;
  advancedParams: Record<string, any>;
  onAdvancedParamChange: (key: string, value: string) => void;
  loading: boolean;
  onGenerate: () => void;
  customInputs?: ReactNode;
  buttonText?: string;
}

export const GeneratorForm = ({
  title,
  description,
  selectedAlgo,
  onAlgorithmChange,
  params,
  onParamChange,
  useDefaults,
  onUseDefaultsChange,
  advancedParams,
  onAdvancedParamChange,
  loading,
  onGenerate,
  customInputs,
  buttonText = "Generate",
}: GeneratorFormProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="algorithm">Algorithm</Label>
          <Select
            value={selectedAlgo.toString()}
            onValueChange={onAlgorithmChange}
          >
            <SelectTrigger id="algorithm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(ALGORITHM_PARAMS).map(([id, { name }]) => (
                <SelectItem key={id} value={id}>
                  {name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {customInputs}

        <Separator />

        {Object.keys(params).length > 0 && (
          <div className="space-y-3">
            <Label>Algorithm Parameters</Label>
            {Object.entries(params).map(([key, value]) => (
              <div key={key} className="space-y-2">
                <Label htmlFor={key} className="text-sm capitalize">
                  {key.replace("_", " ")}
                </Label>
                <Input
                  id={key}
                  value={value}
                  onChange={(e) => onParamChange(key, e.target.value)}
                />
              </div>
            ))}
          </div>
        )}

        <Separator />

        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="useDefaults"
              checked={useDefaults}
              onCheckedChange={(checked) =>
                onUseDefaultsChange(checked as boolean)
              }
            />
            <Label
              htmlFor="useDefaults"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              Use default advanced parameters
            </Label>
          </div>

          <div className="space-y-3">
            <Label>Advanced Parameters</Label>
            {Object.entries(
              useDefaults
                ? ALGORITHM_PARAMS[selectedAlgo].defaults
                : advancedParams
            ).map(([key, value]) => (
              <div key={key} className="space-y-2">
                <Label htmlFor={key} className="text-sm capitalize">
                  {key.replace("_", " ")}
                </Label>
                <Input
                  id={key}
                  value={value}
                  onChange={(e) => onAdvancedParamChange(key, e.target.value)}
                  disabled={useDefaults}
                />
              </div>
            ))}
          </div>
        </div>

        <Button onClick={onGenerate} disabled={loading} className="w-full">
          {loading ? "Generating..." : buttonText}
        </Button>
      </CardContent>
    </Card>
  );
};
