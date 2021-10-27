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
    const [value, setValue] = useState(() => getDateTime(props.defaultValue));
    const { dispatch } = useContext(TaipyContext);

    const { className, tp_varname, withTime, id } = props;

    const handleChange = useCallback(
        (v) => {
            setValue(v);
            // dispatch new date which offset by the timeZone differences between client and server
            const hours = getClientServerTimeZoneOffset() / 60;
            const minutes = getClientServerTimeZoneOffset() % 60;
            const newDate = new Date(v);
            newDate.setHours(newDate.getHours() + hours);
            newDate.setMinutes(newDate.getMinutes() + minutes);
            dispatch(createSendUpdateAction(tp_varname, newDate.toISOString()));
        },
        [tp_varname, dispatch]
    );

    const renderInput = useCallback((params) => <TextField {...params} />, []);

    useEffect(() => {
        if (props.value !== undefined) {
            setValue(getDateTime(props.value));
        }
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
