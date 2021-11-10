import React, { useState, useEffect, useCallback, useContext } from "react";
import MuiButton from "@mui/material/Button";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction } from "../../context/taipyReducers";
import { TaipyBaseProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

interface ButtonProps extends TaipyBaseProps {
    tp_onAction?: string;
    value: string;
}

const Button = (props: ButtonProps) => {
    const { className, id, tp_onAction, defaultValue } = props;
    const [value, setValue] = useState(defaultValue);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    const handleClick = useCallback(() => {
        dispatch(createSendActionNameAction(id, tp_onAction));
    }, [id, tp_onAction, dispatch]);

    useEffect(() => {
        if (props.value !== undefined && value !== props.value) {
            setValue(props.value);
        }
    }, [props.value, value]);

    return <MuiButton id={id} variant="outlined" className={className} onClick={handleClick} disabled={!active}>
            {value}
        </MuiButton>
}

export default Button;
