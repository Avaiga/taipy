import React, { useState, useEffect, useCallback, useContext } from "react";
import TextField from "@mui/material/TextField";

import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import { TaipyInputProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

const Input = (props: TaipyInputProps) => {
    const { className, type, id, tp_varname, propagate = true, defaultValue = "" } = props;
    const [value, setValue] = useState(defaultValue);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    const handleInput = useCallback(
        (e) => {
            setValue(e.target.value);
            dispatch(createSendUpdateAction(tp_varname, e.target.value, propagate));
        },
        [tp_varname, dispatch, propagate]
    );

    useEffect(() => {
        if (props.value !== undefined && value !== props.value) {
            setValue(props.value);
        }
    }, [props.value, value]);

    return (
        <TextField
            margin="dense"
            hiddenLabel
            value={value}
            className={className}
            type={type}
            id={id}
            onChange={handleInput}
            disabled={!active}
        />
    );
};

export default Input;
