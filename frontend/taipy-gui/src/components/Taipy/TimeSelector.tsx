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
import React, { useState, useMemo, useCallback, useEffect } from "react";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import { ErrorBoundary } from "react-error-boundary";
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { isValid, format } from "date-fns";
import { MobileTimePicker } from '@mui/x-date-pickers/MobileTimePicker';
import { getSuffixedClassNames, TaipyActiveProps, TaipyChangeProps, getCssSize } from "./utils";
import { createSendUpdateAction } from "../../context/taipyReducers";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";
import ErrorFallback from "../../utils/ErrorBoundary";
import Field from "./Field";
import { getTime } from "../../utils";

interface TimeSelectorProps extends TaipyActiveProps, TaipyChangeProps {
  analogic?: boolean;
  format?: string;
  defaultTime?: string;
  defaultEditable?: boolean;
  editable?: boolean;
  label?: string;
  time: string;
  width?: string | number;
}

const boxSx = { display: "inline-block" };
const TimeSelector = (props: TimeSelectorProps) => {
  const { analogic = false, id, updateVarName, propagate = true } = props;
  const [value, setValue] = useState(() => getTime(props.defaultTime));
  const dispatch = useDispatch();
  const module = useModule();
  const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
  const active = useDynamicProperty(props.active, props.defaultActive, true);
  const editable = useDynamicProperty(props.editable, props.defaultEditable, true);
  const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
  const timeSx = useMemo(() => (props.width ? { maxWidth: getCssSize(props.width) } : undefined), [props.width]);

  const handleChange = useCallback(
    (v: Date | null) => {
        setValue(v);
        if (v !== null && isValid(v)) {
            // Have to format the picked time value since it comes with timezone
            const newDateTime = format(v, "yyyy-MM-dd'T'HH:mm:ss")

            dispatch(
              createSendUpdateAction(
                  updateVarName,
                  newDateTime,
                  module,
                  props.onChange,
                  propagate
              )
            );
        }
    },
    [updateVarName, dispatch, propagate, props.onChange, module]
  );

  useEffect(() => {
    try {
        if (props.time !== undefined) {
            setValue(getTime(props.time));
        }
    } catch (error) {
        console.error(error);
    }
  }, [props.time]);

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <Tooltip title={hover || ""}>
        <Box id={id} className={className} sx={boxSx}>
          {editable ? (
            analogic ? (
              <MobileTimePicker
                value={value}
                onChange={handleChange}
                className={getSuffixedClassNames(className, "-picker")}
                disabled={!active}
                label={props.label}
                format={props.format}
                sx={timeSx}
              />
            ):(
              <TimePicker 
                value={value}
                onChange={handleChange}
                className={getSuffixedClassNames(className, "-picker")}
                disabled={!active}
                label={props.label}
                format={props.format}
                sx={timeSx}
              />
            )
          ):(
            <Field 
              dataType="time"
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