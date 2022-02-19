import React, { useCallback, useMemo } from "react";
import Slider from "@mui/material/Slider";
import { styled } from "@mui/material/styles";
import { sprintf } from "sprintf-js";

import { TaipyBaseProps } from "./utils";

interface IndicatorProps extends TaipyBaseProps {
    min?: number;
    max?: number;
    value?: number;
    defaultValue: number;
    display?: number | string;
    defaultDisplay: number | string;
    format?: string;
    orientation?: string;
}

const getValue = (value: number, min: number, max: number) => {
    const dir = max - min >= 0;
    value = typeof value === "number" ? value : min;
    return (100 * (Math.max(Math.min(value, dir ? max : min), dir ? min : max) - min)) / (max - min);
};

const Indicator = (props: IndicatorProps) => {
    const { min = 0, max = 100, display, defaultDisplay, format, value, defaultValue = 0 } = props;

    const horizontalOrientation = props.orientation ? props.orientation.charAt(0).toLowerCase() !== "v" : true;

    const getLabel = useCallback(() => {
        const dsp = display === undefined ? (defaultDisplay === undefined ? "" : defaultDisplay) : display;
        return format ? (typeof dsp === "string" ? dsp : sprintf(format, dsp)) : dsp;
    }, [display, defaultDisplay, format]);

    const marks = [
        { value: 0, label: "" + min },
        { value: 100, label: "" + max },
    ];

    const TpSlider = useMemo(
        () =>
            styled(Slider)({
                "&.Mui-disabled": {
                    color: "transparent",
                },
                "& .MuiSlider-markLabel": {
                    transform: "initial",
                },
                "& span:nth-of-type(6)": {
                    transform: horizontalOrientation ? "translateX(-100%)" : "translateY(100%)",
                },
                "& .MuiSlider-rail": {
                    background: `linear-gradient(${
                        horizontalOrientation ? 90 : 0
                    }deg, rgba(255,0,0,1) 0%, rgba(0,255,0,1) 100%)`,
                    opacity: "unset",
                },
                "& .MuiSlider-track": {
                    border: "none",
                    backgroundColor: "transparent",
                },
                "& .MuiSlider-valueLabel": {
                    top: "unset"
                },
                "& .MuiSlider-valueLabel.MuiSlider-valueLabelOpen": {
                    transform: horizontalOrientation ? "": "translate(calc(50% + 10px))"
                },
                "& .MuiSlider-valueLabel:before": {
                    left: horizontalOrientation ? "50%" : "0",
                    bottom: horizontalOrientation ? "0": "50%",
                }
            }),
        [horizontalOrientation]
    );

    return (
        <TpSlider
            min={0}
            max={100}
            value={getValue(value === undefined ? defaultValue : value, min, max)}
            disabled={true}
            valueLabelDisplay="on"
            valueLabelFormat={getLabel}
            marks={marks}
            orientation={horizontalOrientation ? undefined : "vertical"}
        ></TpSlider>
    );
};

export default Indicator;
