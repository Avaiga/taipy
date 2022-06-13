import React, { useState, useEffect, useCallback, useContext, useRef, KeyboardEvent } from "react";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import { TaipyInputProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

const AUTHORIZED_KEYS = ["Enter", "Escape", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"];

const getActionKeys = (keys?: string): string[] => {
    const ak = keys
        ? keys
              .split(";")
              .filter((v) => AUTHORIZED_KEYS.includes(v.trim()))
              .map((v) => v.trim())
        : [];
    return ak.length > 0 ? ak : [AUTHORIZED_KEYS[0]];
};

const Input = (props: TaipyInputProps) => {
    const { className, type, id, updateVarName, propagate = true, defaultValue = "", tp_onAction, tp_onChange } = props;
    const [value, setValue] = useState(defaultValue);
    const { dispatch } = useContext(TaipyContext);
    const delayCall = useRef(-1);
    const [actionKeys] = useState(() => tp_onAction ? getActionKeys(props.actionKeys): []);

    const changeDelay = typeof props.changeDelay === "number" && props.changeDelay >= 0 ? props.changeDelay : 300;
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
                    delayCall.current = -1;
                    dispatch(createSendUpdateAction(updateVarName, val, tp_onChange, propagate));
                }, changeDelay);
            } else {
                dispatch(createSendUpdateAction(updateVarName, val, tp_onChange, propagate));
            }
        },
        [updateVarName, dispatch, propagate, tp_onChange, changeDelay]
    );

    const handleAction = useCallback(
        (evt: KeyboardEvent<HTMLDivElement>) => {
            if (tp_onAction && actionKeys.includes(evt.key)) {
                const val = evt.currentTarget.querySelector("input")?.value;
                if (changeDelay && delayCall.current > 0) {
                    clearTimeout(delayCall.current);
                    delayCall.current = -1;
                    dispatch(createSendUpdateAction(updateVarName, val, tp_onChange, propagate));
                }
                dispatch(createSendActionNameAction(id, tp_onAction, evt.key, updateVarName, val));
                evt.preventDefault();
            }
        },
        [actionKeys, updateVarName, tp_onAction, id, dispatch, tp_onChange, changeDelay, propagate]
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
                label={props.label}
                onChange={handleInput}
                disabled={!active}
                onKeyDown={tp_onAction ? handleAction : undefined}
            />
        </Tooltip>
    );
};

export default Input;
