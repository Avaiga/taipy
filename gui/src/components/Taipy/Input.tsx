import React, { useState, useEffect, useCallback, useContext } from "react";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import { TaipyInputProps } from "./utils";

const Input = (props: TaipyInputProps) => {
    const [value, setValue] = useState(props.defaultvalue);
    const { dispatch } = useContext(TaipyContext);

    const { className, type, id, tp_varname, actionName } = props;

    const hanldeInput = useCallback(e => {
        setValue(e.target.value);
        dispatch(createSendUpdateAction(tp_varname, e.target.value));
    }, [tp_varname, dispatch]);

    const handleClick = useCallback(() => {
        dispatch(createSendActionNameAction(id, actionName));
    }, [id, actionName, dispatch]);

    const actions = {} as Record<string, unknown>;
    if (type === 'button') {
        actions.onClick = handleClick;
    } else {
        actions.onChange= hanldeInput;
    }

    useEffect(() => {
        if (typeof props.value !== 'undefined') {
            setValue(props.value);
        }
    }, [props.value]);

    return <input
            value={value}
            className={className}
            type={type}
            id={id}
            {...actions}
        />
}

export default Input
