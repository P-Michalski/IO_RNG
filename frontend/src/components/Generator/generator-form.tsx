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
import { type RNG } from "@/types/test-results";
import { Switch } from "@/components/ui/switch";

const ALGORITHM_PARAMS = {
  2: {
    name: "SplitMix64",
    params: { seed: 123456789 },
    defaults: {
      bits_per_value: 64,
      msb_first: 1,
    },
    maxBitsPerValue: 64,
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
    maxBitsPerValue: 32,
  },
  4: {
    name: "Park-Miller",
    params: { seed: 123456789 },
    defaults: {
      bits_per_value: 31,
      msb_first: 1,
    },
    maxBitsPerValue: 31,
  },
  5: {
    name: "PCG32",
    params: { initstate: 42, seq: 54 },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
    maxBitsPerValue: 32,
  },
  6: {
    name: "Mersenne Twister (Python random)",
    params: { seed: 12345 },
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
    maxBitsPerValue: 32,
  },
  7: {
    name: "OS /dev/urandom",
    params: {},
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
    maxBitsPerValue: 32,
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
    maxBitsPerValue: 32,
  },
  16: {
    name: "Blum Blum Shub",
    params: { seed: 12345, p: 383, q: 503 },
    defaults: {
      bits_per_value: 1,
      msb_first: 1,
    },
    maxBitsPerValue: 64,
  },
  23: {
    name: "ChaCha20 (Rust)",
    params: {},
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
    maxBitsPerValue: 64,
  },
  24: {
    name: "Xoshiro256** (C#/.NET)",
    params: {},
    defaults: {
      bits_per_value: 32,
      msb_first: 1,
    },
    maxBitsPerValue: 64,
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
  rngs: RNG[];
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
  rngs,
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
              <SelectValue>
                {rngs.find((rng) => rng.id === selectedAlgo)?.name}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {rngs.map((rng) => (
                <SelectItem key={rng.id} value={rng.id.toString()}>
                  <div className="flex flex-col">
                    <span className="font-medium">{rng.name}</span>
                    <span className="text-xs text-muted-foreground">
                      {rng.description}
                    </span>
                  </div>
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
                : advancedParams,
            ).map(([key, value]) => {
              // Dla bits_per_value używamy Input z walidacją
              if (key === "bits_per_value") {
                const maxBits = ALGORITHM_PARAMS[selectedAlgo].maxBitsPerValue;
                return (
                  <div key={key} className="space-y-2">
                    <Label htmlFor={key} className="text-sm">
                      Bits Per Value
                    </Label>
                    <Input
                      id={key}
                      type="number"
                      min={1}
                      max={maxBits}
                      step={1}
                      value={value}
                      onChange={(e) => {
                        const val = e.target.value;
                        // Prevent non-integer input
                        if (val === "" || /^\d+$/.test(val)) {
                          const numVal = parseInt(val);
                          if (
                            !isNaN(numVal) &&
                            numVal >= 1 &&
                            numVal <= maxBits
                          ) {
                            onAdvancedParamChange(key, val);
                          }
                        }
                      }}
                      onKeyDown={(e) => {
                        // Prevent decimal point, comma, minus, plus, and 'e'
                        if ([".", ",", "-", "+", "e", "E"].includes(e.key)) {
                          e.preventDefault();
                        }
                      }}
                      disabled={useDefaults}
                    />
                    <p className="text-xs text-muted-foreground">
                      Range: 1 - {maxBits}
                    </p>
                  </div>
                );
              }

              // Dla msb_first używamy Switch
              if (key === "msb_first") {
                return (
                  <div key={key} className="space-y-2">
                    <Label htmlFor={key} className="text-sm">
                      Bit Order
                    </Label>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">
                        LSB first
                      </span>
                      <Switch
                        id={key}
                        checked={value === 1}
                        onCheckedChange={(checked) =>
                          onAdvancedParamChange(key, checked ? "1" : "0")
                        }
                        disabled={useDefaults}
                      />
                      <span className="text-sm text-muted-foreground">
                        MSB first
                      </span>
                    </div>
                  </div>
                );
              }

              // Dla pozostałych parametrów zwykły Input
              return (
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
              );
            })}
          </div>
        </div>

        <Button onClick={onGenerate} disabled={loading} className="w-full">
          {loading ? "Generating..." : buttonText}
        </Button>
      </CardContent>
    </Card>
  );
};
