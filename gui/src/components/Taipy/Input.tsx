import React, { useState, useEffect, useCallback, useContext } from "react";
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

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const handleInput = useCallback(
        (e) => {
            setValue(e.target.value);
            dispatch(createSendUpdateAction(updateVarName, e.target.value, props.tp_onChange, propagate));
        },
        [updateVarName, dispatch, propagate, props.tp_onChange]
    );

    useEffect(() => {
        if (props.value !== undefined && value !== props.value) {
            setValue(props.value);
        }
    }, [props.value, value]);

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
