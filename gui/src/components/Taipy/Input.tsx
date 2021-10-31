import React, { useState, useEffect, useCallback, useContext } from "react";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import { TaipyInputProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

const Input = (props: TaipyInputProps) => {
    const { className, type, id, tp_varname, tp_onAction, propagate = true } = props;
    const [value, setValue] = useState(props.defaultValue);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    const handleInput = useCallback(
        (e) => {
            setValue(e.target.value);
            dispatch(createSendUpdateAction(tp_varname, e.target.value, propagate));
        },
        [tp_varname, dispatch, propagate]
    );

    const handleClick = useCallback(() => {
        dispatch(createSendActionNameAction(id, tp_onAction));
    }, [id, tp_onAction, dispatch]);

    useEffect(() => {
        if (props.value !== undefined) {
            if (value !== props.value) {
                setValue(props.value);
            }
        }
    }, [props.value, value]);

    return type === "button" ? (
        <Button
            id={id}
            variant="outlined"
            className={className}
            onClick={handleClick}
            disabled={!active}
        >
            {value}
        </Button>
    ) : (
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
