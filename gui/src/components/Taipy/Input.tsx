import React, { useState, useEffect, useCallback, useContext } from "react";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import { TaipyInputProps } from "./utils";

const Input = (props: TaipyInputProps) => {
    const [value, setValue] = useState(props.defaultvalue);
    const { dispatch } = useContext(TaipyContext);

    const { className, type, id, tp_varname, actionName } = props;

    const handleInput = useCallback(e => {
        setValue(e.target.value);
        dispatch(createSendUpdateAction(tp_varname, e.target.value));
    }, [tp_varname, dispatch]);

    const handleClick = useCallback(() => {
        dispatch(createSendActionNameAction(id, actionName));
    }, [id, actionName, dispatch]);

    useEffect(() => {
        if (props.value !== undefined) {
            setValue(props.value);
        }
    }, [props.value]);

    if (type === 'button') {
        return <Button
            id={id}
            variant="outlined"
            className={className}
            onClick={handleClick}
            >
                {value}
            </Button>
    }
    return <TextField
            margin="dense"
            hiddenLabel
            value={value}
            className={className}
            type={type}
            id={id}
            onChange={handleInput}
        />
}

export default Input
