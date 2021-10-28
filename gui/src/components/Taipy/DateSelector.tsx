import React, { useState, useEffect, useCallback, useContext } from "react";
import AdapterDateFns from "@mui/lab/AdapterDateFns";
import LocalizationProvider from "@mui/lab/LocalizationProvider";
import DatePicker from "@mui/lab/DatePicker";
import DateTimePicker from "@mui/lab/DateTimePicker";
import TextField from "@mui/material/TextField";

import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import { TaipyInputProps } from "./utils";
import { getDateTime, getClientServerTimeZoneOffset } from "../../utils/index";

interface DateSelectorProps extends TaipyInputProps {
    withTime?: boolean;
    format?: string;
}

const DateSelector = (props: DateSelectorProps) => {
    const [value, setValue] = useState(new Date());
    const { dispatch } = useContext(TaipyContext);

    const { className, tp_varname, withTime, id } = props;

    const handleChange = useCallback(
        (v) => {
            setValue(v);
            // dispatch new date which offset by the timeZone differences between client and server
            const hours = getClientServerTimeZoneOffset() / 60;
            const minutes = getClientServerTimeZoneOffset() % 60;
            const newDate = new Date(v);
            if (withTime) {
                // Parse data with selected time if it is a datetime selector
                newDate.setHours(newDate.getHours() + hours);
                newDate.setMinutes(newDate.getMinutes() + minutes);
                newDate.setSeconds(0);
                newDate.setMilliseconds(0);
            } else {
                // Parse data with 00:00 UTC time if it is a date selector
                newDate.setHours(hours);
                newDate.setMinutes(minutes);
                newDate.setSeconds(0);
                newDate.setMilliseconds(0);
            }
            dispatch(createSendUpdateAction(tp_varname, newDate.toISOString()));
        },
        [tp_varname, dispatch, withTime]
    );

    const renderInput = useCallback((params) => <TextField {...params} />, []);

    // Run once when component is loaded
    useEffect(() => {
        if (props.defaultvalue !== undefined) {
            if (withTime) setValue(getDateTime(props.defaultvalue));
            else handleChange(getDateTime(props.defaultvalue));
        }
    }, [props.defaultvalue, handleChange, withTime]);

    // Run every time props.value get updated
    useEffect(() => {
        if (props.value !== undefined) setValue(getDateTime(props.value))
    }, [props.value]);

    return (
        <LocalizationProvider id={id} dateAdapter={AdapterDateFns}>
            {withTime ? (
                <DateTimePicker onChange={handleChange} renderInput={renderInput} value={value} className={className} />
            ) : (
                <DatePicker value={value} onChange={handleChange} renderInput={renderInput} className={className} />
            )}
        </LocalizationProvider>
    );
};

export default DateSelector;
