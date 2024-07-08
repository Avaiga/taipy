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

import React, { useState, useEffect, useCallback } from "react";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import { DatePicker, DatePickerProps } from "@mui/x-date-pickers/DatePicker";
import { BaseDateTimePickerSlotProps } from "@mui/x-date-pickers/DateTimePicker/shared";
import { DateTimePicker, DateTimePickerProps } from "@mui/x-date-pickers/DateTimePicker";
import { isValid } from "date-fns";
import { ErrorBoundary } from "react-error-boundary";

import { createSendUpdateAction } from "../../context/taipyReducers";
import { getSuffixedClassNames, TaipyActiveProps, TaipyChangeProps, DateProps, getProps } from "./utils";
import { dateToString, getDateTime, getTimeZonedDate } from "../../utils";
import { useClassNames, useDispatch, useDynamicProperty, useFormatConfig, useModule } from "../../utils/hooks";
import Field from "./Field";
import ErrorFallback from "../../utils/ErrorBoundary";

interface DateSelectorProps extends TaipyActiveProps, TaipyChangeProps {
    withTime?: boolean;
    format?: string;
    date: string;
    min?: string;
    defaultMin?: string;
    max?: string;
    defaultMax?: string;
    defaultDate?: string;
    defaultEditable?: boolean;
    editable?: boolean;
    label?: string;
}

const boxSx = { display: "inline-block" };
const textFieldProps = { textField: { margin: "dense" } } as BaseDateTimePickerSlotProps<Date>;

const DateSelector = (props: DateSelectorProps) => {
    const { updateVarName, withTime = false, id, propagate = true } = props;
    const dispatch = useDispatch();
    const formatConfig = useFormatConfig();
    const tz = formatConfig.timeZone;
    const [value, setValue] = useState(() => getDateTime(props.defaultDate, tz, withTime));
    const [startProps, setStartProps] = useState<DateProps>({});
    const [endProps, setEndProps] = useState<DateProps>({});
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const editable = useDynamicProperty(props.editable, props.defaultEditable, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const min = useDynamicProperty(props.min, props.defaultMin, undefined);
    const max = useDynamicProperty(props.max, props.defaultMax, undefined);

    const handleChange = useCallback(
        (v: Date | null) => {
            setValue(v);
            if (v !== null && isValid(v)) {
                const newDate = getTimeZonedDate(v, tz, withTime);
                dispatch(
                    createSendUpdateAction(
                        updateVarName,
                        dateToString(newDate, withTime),
                        module,
                        props.onChange,
                        propagate,
                    ),
                );
            }
        },
        [updateVarName, dispatch, withTime, propagate, tz, props.onChange, module],
    );

    const handleConsoleLog = () => {
        console.log("DateSelector: ", value);
    };

    // Run only once

    useEffect(() => {
        handleConsoleLog();
    }, []);

    // Run every time props.value get updated
    useEffect(() => {
        try {
            if (props.date !== undefined) {
                setValue(getDateTime(props.date, tz, withTime));
            }

            if (min !== undefined) {
                setStartProps((p) => getProps(p, true, getDateTime(min, tz, withTime), withTime));
            }

            if (max !== undefined) {
                setEndProps((p) => getProps(p, false, getDateTime(max, tz, withTime), withTime));
            }
        } catch (error) {
            console.error(error);
        }
    }, [props.date, tz, withTime, max, min]);

    return (
        <ErrorBoundary FallbackComponent={ErrorFallback}>
            <Tooltip title={hover || ""}>
                <Box id={id} className={className} sx={boxSx}>
                    {editable ? (
                        withTime ? (
                            <DateTimePicker
                                {...(startProps as DateTimePickerProps<Date>)}
                                {...(endProps as DateTimePickerProps<Date>)}
                                value={value}
                                onChange={handleChange}
                                className={getSuffixedClassNames(className, "-picker")}
                                disabled={!active}
                                slotProps={textFieldProps}
                                label={props.label}
                                format={props.format}
                            />
                        ) : (
                            <DatePicker
                                {...(startProps as DatePickerProps<Date>)}
                                {...(endProps as DatePickerProps<Date>)}
                                value={value}
                                onChange={handleChange}
                                className={getSuffixedClassNames(className, "-picker")}
                                disabled={!active}
                                slotProps={textFieldProps}
                                label={props.label}
                                format={props.format}
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
