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
import { getSuffixedClassNames, TaipyActiveProps, TaipyChangeProps } from "./utils";
import { dateToString, getDateTime, getTimeZonedDate } from "../../utils";
import { useClassNames, useDispatch, useDynamicProperty, useFormatConfig, useModule } from "../../utils/hooks";
import Field from "./Field";
import ErrorFallback from "../../utils/ErrorBoundary";

interface DateRangeProps extends TaipyActiveProps, TaipyChangeProps {
    withTime?: boolean;
    format?: string;
    dates: string[];
    defaultDates?: string;
    defaultEditable?: boolean;
    editable?: boolean;
    labelStart?: string;
    labelEnd?: string;
}

const boxSx = { display: "inline-flex", alignItems: "center", gap: "0.5em" };
const textFieldProps = { textField: { margin: "dense" } } as BaseDateTimePickerSlotProps<Date>;

const getRangeDateTime = (
    json: string | string[] | undefined,
    tz: string,
    withTime: boolean
): [Date | null, Date | null] => {
    let dates: string[] = [];
    if (typeof json == "string") {
        try {
            dates = JSON.parse(json);
        } catch (e) {}
    } else {
        dates = json as string[];
    }
    if (Array.isArray(dates) && dates.length) {
        return dates.map((d) => getDateTime(d, tz, withTime)) as [Date, Date];
    }
    return [null, null];
};

interface DateProps {
    maxDate?: unknown;
    maxDateTime?: unknown;
    maxTime?: unknown;
    minDate?: unknown;
    minDateTime?: unknown;
    minTime?: unknown;
}

const getProps = (p: DateProps, start: boolean, val: Date | null, withTime: boolean): DateProps => {
    if (!val) {
        return {};
    }
    const propName: keyof DateProps = withTime
        ? start
            ? "minDateTime"
            : "maxDateTime"
        : start
        ? "minDate"
        : "maxDate";
    if (p[propName] == val) {
        return p;
    }
    return { ...p, [propName]: val };
};

const DateRange = (props: DateRangeProps) => {
    const { updateVarName, withTime = false, id, propagate = true } = props;
    const dispatch = useDispatch();
    const formatConfig = useFormatConfig();
    const tz = formatConfig.timeZone;
    const [value, setValue] = useState<[Date | null, Date | null]>([null, null]);
    const [startProps, setStartProps] = useState<DateProps>({});
    const [endProps, setEndProps] = useState<DateProps>({});
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const editable = useDynamicProperty(props.editable, props.defaultEditable, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const handleChange = useCallback(
        (v: Date | null, start: boolean) => {
            setValue((dates) => {
                if (v !== null && isValid(v)) {
                    const newDate = getTimeZonedDate(v, tz, withTime);
                    const otherDate = start
                        ? dates[1] && getTimeZonedDate(dates[1], tz, withTime)
                        : dates[0] && getTimeZonedDate(dates[0], tz, withTime);
                    dispatch(
                        createSendUpdateAction(
                            updateVarName,
                            [
                                start
                                    ? dateToString(newDate, withTime)
                                    : otherDate && dateToString(otherDate, withTime),
                                start
                                    ? otherDate && dateToString(otherDate, withTime)
                                    : dateToString(newDate, withTime),
                            ],
                            module,
                            props.onChange,
                            propagate
                        )
                    );
                    (start ? setEndProps : setStartProps)((p) => getProps(p, start, v, withTime));
                }

                return [start ? v : dates[0], start ? dates[1] : v];
            });
        },
        [updateVarName, dispatch, withTime, propagate, tz, props.onChange, module]
    );

    const handleChangeStart = useCallback((v: Date | null) => handleChange(v, true), [handleChange]);
    const handleChangeEnd = useCallback((v: Date | null) => handleChange(v, false), [handleChange]);

    // Run every time props.value get updated
    useEffect(() => {
        if (props.dates !== undefined || props.defaultDates) {
            const dates = getRangeDateTime(props.dates === undefined ? props.defaultDates : props.dates, tz, withTime);
            setEndProps((p) => getProps(p, true, dates[0], withTime));
            setStartProps((p) => getProps(p, false, dates[1], withTime));
            setValue(dates);
        }
    }, [props.dates, props.defaultDates, tz, withTime]);

    return (
        <ErrorBoundary FallbackComponent={ErrorFallback}>
            <Tooltip title={hover || ""}>
                <Box id={id} className={className} sx={boxSx}>
                    {editable ? (
                        withTime ? (
                            <>
                                <DateTimePicker
                                    {...(startProps as DateTimePickerProps<Date>)}
                                    value={value[0]}
                                    onChange={handleChangeStart}
                                    className={
                                        getSuffixedClassNames(className, "-picker") +
                                        " " +
                                        getSuffixedClassNames(className, "-picker-start")
                                    }
                                    disabled={!active}
                                    slotProps={textFieldProps}
                                    label={props.labelStart}
                                    format={props.format}
                                />
                                -
                                <DateTimePicker
                                    {...(endProps as DateTimePickerProps<Date>)}
                                    value={value[1]}
                                    onChange={handleChangeEnd}
                                    className={
                                        getSuffixedClassNames(className, "-picker") +
                                        " " +
                                        getSuffixedClassNames(className, "-picker-end")
                                    }
                                    disabled={!active}
                                    slotProps={textFieldProps}
                                    label={props.labelEnd}
                                    format={props.format}
                                />
                            </>
                        ) : (
                            <>
                                <DatePicker
                                    {...(startProps as DatePickerProps<Date>)}
                                    value={value[0]}
                                    onChange={handleChangeStart}
                                    className={
                                        getSuffixedClassNames(className, "-picker") +
                                        " " +
                                        getSuffixedClassNames(className, "-picker-start")
                                    }
                                    disabled={!active}
                                    slotProps={textFieldProps}
                                    label={props.labelStart}
                                    format={props.format}
                                />
                                -
                                <DatePicker
                                    {...(endProps as DatePickerProps<Date>)}
                                    value={value[1]}
                                    onChange={handleChangeEnd}
                                    className={
                                        getSuffixedClassNames(className, "-picker") +
                                        " " +
                                        getSuffixedClassNames(className, "-picker-end")
                                    }
                                    disabled={!active}
                                    slotProps={textFieldProps}
                                    label={props.labelEnd}
                                    format={props.format}
                                />
                            </>
                        )
                    ) : (
                        <>
                            <Field
                                dataType="datetime"
                                value={props.dates[0]}
                                format={props.format}
                                id={id && id + "-field"}
                                className={getSuffixedClassNames(className, "-text")}
                            />
                            -
                            <Field
                                dataType="datetime"
                                value={props.dates[1]}
                                format={props.format}
                                id={id && id + "-field"}
                                className={getSuffixedClassNames(className, "-text")}
                            />
                        </>
                    )}
                </Box>
            </Tooltip>
        </ErrorBoundary>
    );
};

export default DateRange;
