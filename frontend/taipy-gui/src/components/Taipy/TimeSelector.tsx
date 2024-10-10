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
import React, { useState, useMemo } from "react";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import { ErrorBoundary } from "react-error-boundary";
import { TimePicker } from '@mui/x-date-pickers/TimePicker';

import { MobileTimePicker } from '@mui/x-date-pickers/MobileTimePicker';
import { getSuffixedClassNames, TaipyActiveProps, TaipyChangeProps, getCssSize } from "./utils";
import { getDateTime } from "../../utils";
import { useClassNames, useDynamicProperty, useFormatConfig } from "../../utils/hooks";
import ErrorFallback from "../../utils/ErrorBoundary";
import Field from "./Field";



interface TimeSelectorProps extends TaipyActiveProps, TaipyChangeProps {
  as_clock?: boolean;
  withTime?: boolean;
  format?: string;
  defaultDate?: string;
  defaultTime?: string;
  defaultEditable?: boolean;
  editable?: boolean;
  label?: string;
  time: string;
  width?: string | number;
}

const boxSx = { display: "inline-block" };
const TimeSelector = (props: TimeSelectorProps) => {
  const { withTime = true, as_clock = false, id } = props;
  const formatConfig = useFormatConfig();
  const tz = formatConfig.timeZone;
  const [value] = useState(() => getDateTime(props.defaultDate, tz, withTime));

  const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
  const active = useDynamicProperty(props.active, props.defaultActive, true);
  const editable = useDynamicProperty(props.editable, props.defaultEditable, true);
  const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
  const timeSx = useMemo(() => (props.width ? { maxWidth: getCssSize(props.width) } : undefined), [props.width]);

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <Tooltip title={hover || ""}>
        <Box id={id} className={`${className}`} sx={boxSx}>
          {editable ? (
            as_clock ? (
              <MobileTimePicker  
                value={value}
                className={getSuffixedClassNames(className, "-picker")}
                disabled={!active}
                label={props.label}
                format={props.format}
                sx={timeSx}
              />
            ):(
              <TimePicker 
                value={value}
                className={getSuffixedClassNames(className, "-picker")}
                disabled={!active}
                label={props.label}
                format={props.format}
                sx={timeSx}
              />
            )
          ):(
            <Field 
              dataType="string"
              defaultValue={props.defaultTime}
              id={id && id + "-field"}
              value={props.time}
              className={getSuffixedClassNames(className, "-text")}
              format={props.format}
            />
          )}
        </Box>
      </Tooltip>
    </ErrorBoundary>
  );
}
export default TimeSelector