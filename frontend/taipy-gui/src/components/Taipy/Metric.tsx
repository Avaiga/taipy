/*
 * Copyright 2021-2024 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import React,
{
  useMemo,
  lazy,
  useState,
  useEffect,
} from 'react';
import {Delta} from "plotly.js";
import {useClassNames, useDynamicProperty} from "../../utils/hooks";
import {TaipyBaseProps, TaipyHoverProps} from "./utils";
import Box from "@mui/material/Box";

const Plot = lazy(() => import("react-plotly.js"));

interface MetricProps extends TaipyBaseProps, TaipyHoverProps {
  type?: string
  min?: number
  max?: number
  value?: number
  defaultValue?: number
  delta?: number
  defaultDelta?: number
  thresholdValue?: number
  defaultThresholdValue?: number
  format?: string
  formatDelta?: string
  testId?: string
}

interface DeltaProps extends Partial<Delta> {
  suffix: string
}

const Metric = (props: MetricProps) => {
  const metricValue = useDynamicProperty(props.value, props.defaultValue, 0)
  const gaugeThresholdValue = useDynamicProperty(props.thresholdValue, props.defaultThresholdValue, undefined)
  const metricDelta = useDynamicProperty(props.delta, props.defaultDelta, undefined)
  const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

  const [metricType, setMetricType] = useState<"angular" | "bullet">("angular");
  const [formatType, setFormatType] = useState<"%" | "">("");
  const [isDeltaFormatPercentage, setIsDeltaFormatPercentage] = useState<"%" | "">("");

  useEffect(() => {
  switch (props.type) {
    case "circular":
      setMetricType("angular");
      break;
    case "linear":
      setMetricType("bullet");
      break;
    default:
      setMetricType("angular");
  }
}, [props.type]);

useEffect(() => {
  switch (props.format) {
    case "%.2f%%":
      setFormatType("%");
      break;
    default:
      setFormatType("");
  }
}, [props.format]);

useEffect(() => {
  switch (props.formatDelta) {
    case "%.2f%%":
      setIsDeltaFormatPercentage("%");
      break;
    default:
      setIsDeltaFormatPercentage("");
  }
}, [props.formatDelta]);

  const refValue = useMemo(() => {
    if (typeof metricValue === 'number' && typeof metricDelta === 'number') {
      return metricValue - metricDelta;
    } else {
      return;
    }
  }, [metricValue, metricDelta]);

  const extendedDelta: DeltaProps = {
    reference: refValue,
    suffix: isDeltaFormatPercentage,
  }

  return (
    <Box data-testid={props.testId} className={className}>
        <Plot
        data={[
          {
            domain: {x: [0, 1], y: [0, 1]},
            value: metricValue,
            type: "indicator",
            mode: "gauge+number+delta",
            number: {
              suffix: formatType
            },
            delta: extendedDelta,
            gauge: {
              axis: {range: [props.min, props.max]},
              shape: metricType,
              threshold: {
                line: {color: "red", width: 4},
                thickness: 0.75,
                value: gaugeThresholdValue
              }
            },
          }
        ]}
        layout={{
          paper_bgcolor: "#fff",
          width: 600,
          height: 600,
        }}
        style={{
          position: "relative",
          display: "inline-block",
          borderRadius: "20px",
          overflow: "hidden",
        }}
      />
    </Box>
  );
}

export default Metric;
