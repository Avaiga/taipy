import React, { useState, useEffect, useCallback, useContext } from "react";
import MuiButton from "@mui/material/Button";

import { TaipyContext } from "../../context/taipyContext";
import { createSendActionNameAction } from "../../context/taipyReducers";
import { getSuffixedClassNames, TaipyActiveProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";
import { stringImage, TaipyImage, TaipyImageComp } from "../../utils/image";

interface ButtonProps extends TaipyActiveProps {
    tp_onAction?: string;
    label: string;
    defaultLabel?: string;
}

const Button = (props: ButtonProps) => {
    const { className, id, tp_onAction, defaultLabel } = props;
    const [value, setValue] = useState<stringImage>("");
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    const handleClick = useCallback(() => {
        dispatch(createSendActionNameAction(id, tp_onAction));
    }, [id, tp_onAction, dispatch]);

    useEffect(() => {
        setValue((val) => {
            if (props.label === undefined && defaultLabel) {
                try {
                    return JSON.parse(defaultLabel) as TaipyImage;
                } catch (e) {
                    return defaultLabel;
                }
            }
            if (props.label !== undefined) {
                return props.label;
            }
            return val;
        });
    }, [props.label, defaultLabel]);

    return (
        <MuiButton id={id} variant="outlined" className={className} onClick={handleClick} disabled={!active}>
            {typeof value === "string" ? (
                value
            ) : (
                <TaipyImageComp img={value as TaipyImage} className={getSuffixedClassNames(className, "-image")} />
            )}
        </MuiButton>
    );
};

export default Button;
