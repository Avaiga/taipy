import React, { useState, useEffect, useCallback, useContext } from "react";
import DatePicker from "react-date-picker";
import DateTimePicker from "react-datetime-picker";

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

    useEffect(() => {
        if (typeof props.value !== 'undefined') {
            setValue(new Date(props.value))
        }
    }, [props.value]);

    return withTime && withTime.toLowerCase() === 'true' ?
        <DateTimePicker onChange={handleChange} value={value} className={className} />
        :
        <DatePicker onChange={handleChange} value={value} className={className} />;
}

export default DateSelector
