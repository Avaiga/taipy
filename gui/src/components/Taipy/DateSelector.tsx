/*
 * Copyright 2023 Avaiga Private Limited
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

import React, { useState, useEffect, useCallback, useContext } from "react";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { BaseDateTimePickerSlotsComponentsProps } from "@mui/x-date-pickers/DateTimePicker/shared";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import { isValid } from "date-fns";
import { ErrorBoundary } from "react-error-boundary";

import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import { getSuffixedClassNames, TaipyActiveProps, TaipyChangeProps } from "./utils";
import { getDateTime, getClientServerTimeZoneOffset } from "../../utils";
import { useClassNames, useDynamicProperty, useFormatConfig } from "../../utils/hooks";
import Field from "./Field";
import ErrorFallback from "../../utils/ErrorBoundary";

interface DateSelectorProps extends TaipyActiveProps, TaipyChangeProps {
    withTime?: boolean;
    format?: string;
    date: string;
    defaultDate?: string;
    defaultEditable?: boolean;
    editable?: boolean;
}

const boxSx = { display: "inline-block" };
const textFieldProps = {textField: {margin:"dense"}} as BaseDateTimePickerSlotsComponentsProps<Date>;

const DateSelector = (props: DateSelectorProps) => {
    const { updateVarName, withTime = false, id, propagate = true } = props;
    const { dispatch } = useContext(TaipyContext);
    const formatConfig = useFormatConfig();
    const tz = formatConfig.timeZone;
    const [value, setValue] = useState(() => getDateTime(props.defaultDate, tz));

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const editable = useDynamicProperty(props.editable, props.defaultEditable, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const handleChange = useCallback(
        (v: Date | null) => {
            setValue(v);
            if (v !== null && isValid(v)) {
                const newDate = v;
                // dispatch new date which offset by the timeZone differences between client and server
                const hours = getClientServerTimeZoneOffset(tz) / 60;
                const minutes = getClientServerTimeZoneOffset(tz) % 60;
                newDate.setSeconds(0);
                newDate.setMilliseconds(0);
                if (withTime) {
                    // Parse data with selected time if it is a datetime selector
                    newDate.setHours(newDate.getHours() + hours);
                    newDate.setMinutes(newDate.getMinutes() + minutes);
                } else {
                    // Parse data with 00:00 UTC time if it is a date selector
                    newDate.setHours(hours);
                    newDate.setMinutes(minutes);
                }
                dispatch(createSendUpdateAction(updateVarName, newDate.toISOString(), props.onChange, propagate));
            }
        },
        [updateVarName, dispatch, withTime, propagate, tz, props.onChange]
    );

    // Run every time props.value get updated
    useEffect(() => {
        if (props.date !== undefined) {
            setValue(getDateTime(props.date, tz));
        }
    }, [props.date, tz]);

    return (
        <ErrorBoundary FallbackComponent={ErrorFallback}>
            <Tooltip title={hover || ""}>
                <Box id={id} className={className} sx={boxSx}>
                    {editable ? (
                        withTime ? (
                            <DateTimePicker
                                value={value}
                                onChange={handleChange}
                                className={getSuffixedClassNames(className, "-picker")}
                                disabled={!active}
                                slotProps={textFieldProps}
                            />
                        ) : (
                            <DatePicker
                                value={value}
                                onChange={handleChange}
                                className={getSuffixedClassNames(className, "-picker")}
                                disabled={!active}
                                slotProps={textFieldProps}
                            />
                        )
                    ) : (
                        <Field
                            dataType="datetime"
                            defaultValue={props.defaultDate}
                            value={props.date}
                            format={props.format}
                            id={id && id + "-field"}
                            className={getSuffixedClassNames(className, "-text")}
                        />
                    )}
                </Box>
            </Tooltip>
        </ErrorBoundary>
    );
};

export default DateSelector;
