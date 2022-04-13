import React, { useState, useEffect, useCallback, useContext, useRef } from "react";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";

import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import { TaipyInputProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

const Input = (props: TaipyInputProps) => {
    const { className, type, id, updateVarName, propagate = true, defaultValue = "" } = props;
    const [value, setValue] = useState(defaultValue);
    const { dispatch } = useContext(TaipyContext);
    const delayCall = useRef(-1);

    const changeDelay = (typeof props.changeDelay === "number" && props.changeDelay >= 0) ? props.changeDelay : 300;
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const handleInput = useCallback(
        (e) => {
            const val = e.target.value;
            setValue(val);
            if (changeDelay) {
                if (delayCall.current > 0) {
                    clearTimeout(delayCall.current);
                }
                delayCall.current = window.setTimeout(() => {
                    dispatch(createSendUpdateAction(updateVarName, val, props.tp_onChange, propagate));
                    delayCall.current = -1;
                }, changeDelay);
            } else {
                dispatch(createSendUpdateAction(updateVarName, val, props.tp_onChange, propagate));
            }
        },
        [updateVarName, dispatch, propagate, props.tp_onChange, changeDelay]
    );

    useEffect(() => {
        if (props.value !== undefined) {
            setValue(props.value);
        }
    }, [props.value]);

    return (
        <Tooltip title={hover || ""}>
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
        </Tooltip>
    );
};

export default Input;
