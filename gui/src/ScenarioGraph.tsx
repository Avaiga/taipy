import React, { useMemo } from "react";
import { CanvasWidget } from "@projectstorm/react-canvas-core";

import { DisplayModel } from "./utils/types";

interface ScenarioGraphProps {
  id?: string;
  scenario?: DisplayModel;
  coreChanged?: Record<string, unknown>;
  error?: string;
}

const ScenarioGraph = (props: ScenarioGraphProps) => {
  const displayModel = useMemo(() => {
    if (!props.scenario) {
      return undefined;
    }
    if (Array.isArray(props.scenario)) {
      if (props.scenario.length === 1) {
        return props.scenario[0];
      }
      return undefined;
    }
    return props.scenario;
  }, []);

  if (!displayModel) {
    return null;
  }

  return <CanvasWidget engine={null}></CanvasWidget>;
};

export default ScenarioGraph;
