import React, { useState, useEffect, useCallback, useContext } from "react";
import AdapterDateFns from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import DatePicker from "@mui/lab/DatePicker";
import DateTimePicker from "@mui/lab/DateTimePicker";
import TextField from "@mui/material/TextField";

import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import { TaipyInputProps } from "./utils";

interface DateSelectorProps extends TaipyInputProps {
    withTime?: string;
    format?: string;
}

const DateSelector = (props: DateSelectorProps) => {
    const [value, setValue] = useState(() => new Date(props.defaultvalue));
    const { dispatch } = useContext(TaipyContext);

    const { className, tp_varname, withTime } = props;

    const handleChange = useCallback(v => {
        setValue(v);
        dispatch(createSendUpdateAction(tp_varname, v.toISOString()));
    }, [tp_varname, dispatch]);

    const renderInput = useCallback((params) => <TextField {...params} />, []);

    useEffect(() => {
        if (props.value !== undefined) {
            setValue(new Date(props.value))
        }
    }, [props.value]);

    return <LocalizationProvider dateAdapter={AdapterDateFns}>
        {withTime && withTime.toLowerCase() === 'true' ?
            <DateTimePicker 
                onChange={handleChange} 
                renderInput={renderInput}
                value={value} 
                className={className}
            />
            :
            <DatePicker
                value={value}
                onChange={handleChange}
                renderInput={renderInput}
                className={className}
            />
}
        </LocalizationProvider>;
}

export default DateSelector
