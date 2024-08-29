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

import React, { useState, useEffect, useCallback, useMemo } from "react";
import Stack from "@mui/material/Stack";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { DatePicker, DatePickerProps } from "@mui/x-date-pickers/DatePicker";
import { BaseDateTimePickerSlotProps } from "@mui/x-date-pickers/DateTimePicker/shared";
import { DateTimePicker, DateTimePickerProps } from "@mui/x-date-pickers/DateTimePicker";
import { isValid } from "date-fns";
import { ErrorBoundary } from "react-error-boundary";

import { createSendUpdateAction } from "../../context/taipyReducers";
import { getCssSize, getSuffixedClassNames, TaipyActiveProps, TaipyChangeProps, DateProps, getProps } from "./utils";
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
    separator?: string;
    width?: string | number;
}

const baseBoxSx = { display: "inline-flex", alignItems: "center", gap: "0.5em" };
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

const DateRange = (props: DateRangeProps) => {
    const { updateVarName, withTime = false, id, propagate = true, separator = "-" } = props;
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

    const dateSx = useMemo(() => (props.width ? { maxWidth: "100%" } : undefined), [props.width]);

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
                <Stack
                    id={id}
                    className={className}
                    gap={0.5}
                    direction="row"
                    display="inline-flex"
                    alignItems="center"
                    width={props.width ? getCssSize(props.width) : undefined}
                >
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
                                    sx={dateSx}
                                />
                                <Typography>{separator}</Typography>
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
                                    sx={dateSx}
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
                                    sx={dateSx}
                                />
                                <Typography>{separator}</Typography>
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
                                    sx={dateSx}
                                />
                            </>
                        )
                    ) : (
                        <>
                            <Field
                                dataType="datetime"
                                value={value[0] && isValid(value[0]) ? value[0].toISOString() : ""}
                                format={props.format}
                                id={id && id + "-field"}
                                className={getSuffixedClassNames(className, "-text")}
                                width={props.width && "100%"}
                            />
                            <Typography>{separator}</Typography>
                            <Field
                                dataType="datetime"
                                value={value[1] && isValid(value[1]) ? value[1].toISOString() : ""}
                                format={props.format}
                                id={id && id + "-field"}
                                className={getSuffixedClassNames(className, "-text")}
                                width={props.width && "100%"}
                            />
                        </>
                    )}
                </Stack>
            </Tooltip>
        </ErrorBoundary>
    );
};

export default DateRange;
