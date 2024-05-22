/*
 * Copyright 2021-2024 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import React, { useCallback, useMemo } from "react";
import Slider from "@mui/material/Slider";
import { sprintf } from "sprintf-js";

import { TaipyBaseProps } from "./utils";
import { useClassNames } from "../../utils/hooks";

interface IndicatorProps extends TaipyBaseProps {
    min?: number;
    max?: number;
    value?: number;
    defaultValue: number;
    display?: number | string;
    defaultDisplay: number | string;
    format?: string;
    orientation?: string;
    width?: string;
    height?: string;
}

const getValue = (value: number, min: number, max: number) => {
    const dir = max - min >= 0;
    value = typeof value === "number" ? value : min;
    return (100 * (Math.max(Math.min(value, dir ? max : min), dir ? min : max) - min)) / (max - min);
};

const Indicator = (props: IndicatorProps) => {
    const { min = 0, max = 100, display, defaultDisplay, format, value, defaultValue = 0, width, height } = props;

    const horizontalOrientation = props.orientation ? props.orientation.charAt(0).toLowerCase() !== "v" : true;
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    const getLabel = useCallback(() => {
        const dsp = display === undefined ? (defaultDisplay === undefined ? "" : defaultDisplay) : display;
        return format ? (typeof dsp === "string" ? dsp : sprintf(format, dsp)) : dsp;
    }, [display, defaultDisplay, format]);

    const marks = [
        { value: 0, label: "" + min },
        { value: 100, label: "" + max },
    ];

    const sliderSx = useMemo(
        () => ({
                "&": {
                    width: horizontalOrientation ? width : undefined,
                    height: horizontalOrientation ? undefined : height,
                },
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
                    top: "unset",
                },
                "& .MuiSlider-valueLabel.MuiSlider-valueLabelOpen": {
                    transform: horizontalOrientation ? "" : "translate(calc(50% + 10px))",
                },
                "& .MuiSlider-valueLabel:before": {
                    left: horizontalOrientation ? "50%" : "0",
                    bottom: horizontalOrientation ? "0" : "50%",
                },
            }),
        [horizontalOrientation, width, height]
    );

    return (
            <Slider
                id={props.id}
                className={className}
                min={0}
                max={100}
                value={getValue(value === undefined ? defaultValue : value, min, max)}
                disabled={true}
                valueLabelDisplay="on"
                valueLabelFormat={getLabel}
                marks={marks}
                orientation={horizontalOrientation ? undefined : "vertical"}
                sx={sliderSx}
            ></Slider>
    );
};

export default Indicator;
