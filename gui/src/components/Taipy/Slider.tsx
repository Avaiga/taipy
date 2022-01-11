import React, { useState, useEffect, useCallback, useContext, useMemo } from "react";
import MuiSlider from "@mui/material/Slider";
import Box from "@mui/material/Box";

import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import { TaipyBaseProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

interface SliderProps extends TaipyBaseProps {
    width?: number | string;
    min?: number;
    max?: number;
    value: number;
    defaultValue?: string|number;
}

const Slider = (props: SliderProps) => {
    const { className, id, tp_varname, propagate = true, min, max, defaultValue, width = 300 } = props;
    const [value, setValue] = useState(0);
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    const handleRange = useCallback(
        (e, val: number | number[]) => {
            setValue(val as number);
            dispatch(createSendUpdateAction(tp_varname, val, propagate));
        },
        [tp_varname, dispatch, propagate]
    );

    useEffect(() => {
        if (props.value === undefined) {
            let val = 0;
            if (defaultValue !== undefined) {
                if (typeof defaultValue === "string") {
                    try {
                        val = parseInt(defaultValue, 10);
                    } catch(e) {
                        // too bad
                    }
                } else {
                    val = defaultValue as number;
                }
            }
            setValue(val);
        } else {
            setValue(props.value);
        }
    }, [props.value, value, defaultValue]);

    const boxSx = useMemo(() => ({width: width, display: 'inline-block'}), [width]);

    return <Box sx={boxSx} className={className}>
                <MuiSlider
                    id={id}
                    value={value as number}
                    onChange={handleRange}
                    disabled={!active}
                    valueLabelDisplay="auto"
                    min={min}
                    max={max}
                />
            </Box>
}

export default Slider;
