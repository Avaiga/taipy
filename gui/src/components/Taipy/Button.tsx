import React, { useState, useEffect, useCallback, useContext } from "react";
import MuiButton from "@mui/material/Button";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction } from "../../context/taipyReducers";
import { TaipyActiveProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

interface ButtonProps extends TaipyActiveProps {
    tp_onAction?: string;
    label: string;
    defaultLabel?: string;
}

const Button = (props: ButtonProps) => {
    const { className, id, tp_onAction, defaultLabel } = props;
    const [value, setValue] = useState(defaultLabel);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    const handleClick = useCallback(() => {
        dispatch(createSendActionNameAction(id, tp_onAction));
    }, [id, tp_onAction, dispatch]);

    useEffect(() => {
        setValue((val) => {
            if (props.label !== undefined && val !== props.label) {
                return props.label;
            }
            return val;
        });
    }, [props.label]);

    return (
        <MuiButton id={id} variant="outlined" className={className} onClick={handleClick} disabled={!active}>
            {value}
        </MuiButton>
    );
};

export default Button;
