import React, { useState, useEffect, useCallback, useContext } from "react";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import { setValueForVarName, TaipyInputProps } from "./utils";

const Input = (props: TaipyInputProps) => {
    const [value, setValue] = useState(props.value);
    const { dispatch } = useContext(TaipyContext);

    const { className, type, id, tp_varname, actionName } = props;

    const hanldeInput = useCallback(e => {
        setValue(e.target.value);
        dispatch(createSendUpdateAction(tp_varname, e.target.value));
    }, [tp_varname, dispatch]);

    const handleClick = useCallback(() => {
        dispatch(createSendActionNameAction(id, actionName));
    }, [id, actionName, dispatch]);

    const actions = {} as any;
    if (type === 'button') {
        actions.onClick = handleClick;
    }

    useEffect(() => {
        setValueForVarName(tp_varname, props, setValue)
    }, [tp_varname, props]);

    return <input
            value={value}
            className={className}
            type={type}
            id={id}
            onChange={hanldeInput}
            {...actions}
        />
}

export default Input
