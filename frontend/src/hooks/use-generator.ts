import { useState } from "react";
import {
  ALGORITHM_PARAMS,
  type AlgorithmId,
} from "@/components/Generator/generator-form";

export const useGenerator = (initialAlgoId: AlgorithmId = 1) => {
  const [selectedAlgo, setSelectedAlgo] = useState<AlgorithmId>(initialAlgoId);
  const [params, setParams] = useState<Record<string, any>>(
    ALGORITHM_PARAMS[initialAlgoId].params
  );
  const [useDefaults, setUseDefaults] = useState(true);
  const [advancedParams, setAdvancedParams] = useState<Record<string, any>>(
    ALGORITHM_PARAMS[initialAlgoId].defaults
  );
  const [loading, setLoading] = useState(false);

  const handleAlgorithmChange = (value: string) => {
    const algoId = parseInt(value) as AlgorithmId;
    setSelectedAlgo(algoId);
    setParams(ALGORITHM_PARAMS[algoId].params);
    setAdvancedParams(ALGORITHM_PARAMS[algoId].defaults);
    setUseDefaults(true);
  };

  const handleParamChange = (key: string, value: string) => {
    setParams((prev) => ({
      ...prev,
      [key]: isNaN(Number(value)) ? value : Number(value),
    }));
  };

  const handleAdvancedParamChange = (key: string, value: string) => {
    setAdvancedParams((prev) => ({
      ...prev,
      [key]: isNaN(Number(value)) ? value : Number(value),
    }));
  };

  const generateBits = async (count: number) => {
    const seed = params.seed;
    const { seed: _removed, ...paramsWithoutSeed } = params;

    const parameters = {
      ...paramsWithoutSeed,
      ...(useDefaults
        ? ALGORITHM_PARAMS[selectedAlgo].defaults
        : advancedParams),
    };

    const requestBody: any = {
      count,
      parameters,
    };

    if (seed !== undefined) {
      requestBody.seed = seed;
    }

    const response = await fetch(
      `http://localhost:8000/api/rngs/${selectedAlgo}/generate?compressed=true`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      }
    );

    if (!response.ok) throw new Error("Failed to generate bits");

    return response.json();
  };

  return {
    selectedAlgo,
    params,
    useDefaults,
    advancedParams,
    loading,
    setLoading,
    handleAlgorithmChange,
    handleParamChange,
    handleAdvancedParamChange,
    setUseDefaults,
    generateBits,
  };
};
