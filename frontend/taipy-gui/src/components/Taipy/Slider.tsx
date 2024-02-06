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

import React, { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { SxProps } from "@mui/material";
import MuiSlider from "@mui/material/Slider";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Tooltip from "@mui/material/Tooltip";

import { createSendUpdateAction } from "../../context/taipyReducers";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";
import { LovImage, LovProps, useLovListMemo } from "./lovUtils";
import { getCssSize, getUpdateVar } from "./utils";
import { Icon } from "../../utils/icon";
import { SyntheticEvent } from "react";

interface SliderProps extends LovProps<number | string | number[] | string[], number | string | number[] | string[]> {
    width?: string;
    height?: string;
    min?: number;
    max?: number;
    step?:number;
    textAnchor?: string;
    continuous?: boolean;
    labels?: string | boolean;
    orientation?: string;
    changeDelay?: number;
}

const emptyString = () => ""

const Slider = (props: SliderProps) => {
    const {
        id,
        updateVarName,
        propagate = true,
        defaultValue,
        lov,
        defaultLov = "",
        textAnchor = "bottom",
        width = "300px",
        updateVars = "",
        valueById,
    } = props;
    const [value, setValue] = useState<number|number[]>(0);
    const dispatch = useDispatch();
    const delayCall = useRef(-1);
    const lastVal = useRef<number|string|number[]|string[]>(0);
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const lovList = useLovListMemo(lov, defaultLov);

    const update = props.continuous === undefined ? lovList.length === 0 : props.continuous;
    const changeDelay = (typeof props.changeDelay === "number" && props.changeDelay > 0) ? props.changeDelay : 0;

    const min = lovList.length ? 0 : props.min;
    const max = lovList.length ? lovList.length - 1 : props.max;
    const step = props.step === undefined ? 1 : props.step;
    const horizontalOrientation = props.orientation ? props.orientation.charAt(0).toLowerCase() !== "v" : true;

    // Converts the slider value (number or array of numbers) to a proper backend value
    // depending on whether we're dealing with a lov or not
    const convertValue = useCallback(
        (v: number | number[]): number | string | number[] | string[] =>
            Array.isArray(v)
            ? (lovList.length
                ? v.map((i) => lovList.length > (i as number) ? lovList[i as number].id : lovList[0].id)
                : v)
                : (lovList.length && lovList.length > (v as number) ? lovList[v as number].id : v),
        [lovList])

    const handleChange = useCallback(
        (e: Event, val: number | number[]) => {
            setValue(val);
            if (update) {
                lastVal.current = convertValue(val)
                // Similar invocations of createSendUpdateAction(), but they happen at different
                // points in time.
                if (changeDelay) {
                    if (delayCall.current < 0) {
                        delayCall.current = window.setTimeout(() => {
                            dispatch(createSendUpdateAction(updateVarName, lastVal.current, module, props.onChange, propagate, valueById ? undefined : getUpdateVar(updateVars, "lov")));
                            delayCall.current = -1;
                        }, changeDelay);
                    }
                } else {
                    dispatch(createSendUpdateAction(updateVarName, lastVal.current, module, props.onChange, propagate, valueById ? undefined : getUpdateVar(updateVars, "lov")));
                }
                delayCall.current = 0;
            }
        },
        [update, updateVarName, dispatch, propagate, updateVars, valueById, props.onChange, changeDelay, module, convertValue]
    );

    const handleChangeCommitted = useCallback(
        (e: Event | SyntheticEvent, val: number | number[]) => {
            setValue(val);
            if (!update) {
                const converted_value = convertValue(val)
                dispatch(createSendUpdateAction(updateVarName, converted_value, module, props.onChange, propagate, valueById ? undefined : getUpdateVar(updateVars, "lov")))
            }
        },
        [update, updateVarName, dispatch, propagate, updateVars, valueById, props.onChange, module, convertValue]
    );

    const getLabel = useCallback(
        (value: number | number[] | null) =>
            value === null || Array.isArray(value) ? null :
            lovList.length && lovList.length > value ? (
                typeof lovList[value].item === "string" ? (
                    <Typography>{lovList[value].item as string}</Typography>
                ) : (
                    <LovImage item={lovList[value].item as Icon} />
                )
            ) : (
                <>{value}</>
            ),
        [lovList]
    );

    const getText = useCallback(
        (value: number|number[], before: boolean) => {
            if (lovList.length) {
                if (before && (textAnchor === "top" || textAnchor === "left")) {
                    return getLabel(value);
                }
                if (!before && (textAnchor === "bottom" || textAnchor === "right")) {
                    return getLabel(value);
                }
            }
            return null;
        },
        [lovList, textAnchor, getLabel]
    );


    const marks = useMemo(() => {
        if (props.labels) {
            if (typeof props.labels === "boolean") {
                if (lovList.length) {
                    return lovList.map((it, idx) => ({ value: idx, label: getLabel(idx) }));
                }
            } else {
                try {
                    const labels = JSON.parse(props.labels);
                    const marks: Array<{ value: number; label: string }> = [];
                    Object.keys(labels).forEach((key) => {
                        if (labels[key]) {
                            let idx = lovList.findIndex((it) => it.id === key);
                            if (idx == -1) {
                                try {
                                    idx = parseInt(key, 10);
                                } catch (e) {
                                    // too bad
                                }
                            }
                            if (idx != -1) {
                                marks.push({ value: idx, label: labels[key] });
                            }
                        }
                    });
                    if (marks.length) {
                        return marks;
                    }
                } catch (e) {
                    // won't happen
                }
            }
        }
        return lovList.length > 0;
    }, [props.labels, lovList, getLabel]);

    const textAnchorSx = useMemo(() => {
        const sx = horizontalOrientation ? { width: getCssSize(width) } : { height: getCssSize(props.height || width) };
        if (lovList.length) {
            if (textAnchor === "top" || textAnchor === "bottom") {
                return { ...sx, display: "inline-grid", gap: "0.5em", textAlign: "center" } as SxProps;
            }
            if (textAnchor === "left" || textAnchor === "right") {
                return {
                    ...sx,
                    display: "inline-grid",
                    gap: "1em",
                    gridTemplateColumns: textAnchor === "left" ? "auto 1fr" : "1fr auto",
                    alignItems: "center",
                } as SxProps;
            }
        }
        return { ...sx, display: "inline-block" };
    }, [lovList, horizontalOrientation, textAnchor, width, props.height]);

    // Parse the default value once and for all
    const parsedDefaultValue = useMemo(() => {
        if (defaultValue === undefined) {
            return 0
        }
        if (typeof defaultValue === "string") {
            if (lovList.length) {
                try {
                    const arr = JSON.parse(defaultValue) as string[];
                    if (arr.length > 1) {
                        return arr.map((i) => lovList.findIndex((j) => j.id === i))
                            // Force unknown values to index 0
                            .map((v) => v === -1 ? 0 : v)
                    }
                    else {
                        const val = lovList.findIndex((item) => item.id === arr[0])
                        return val === -1 ? 0 : val
                    }
                } catch (e) {
                    throw new Error("Slider lov value couldn't be parsed");
                }
            }
            else {
                const val = Number(defaultValue)
                if (isNaN(val)) {
                    try {
                        const arr = JSON.parse(defaultValue) as number[]
                        if (arr.some(isNaN)) {
                            throw new Error("Slider values should all be numbers")
                        }
                        return arr
                    } catch (e) {
                        // Invalid values
                        return 0
                    }
                }
                else {
                    return val
                }
            }
        }
        return defaultValue as number
    }, [defaultValue, lovList])

    useEffect(() => {
        if (props.value === undefined) {
            if (parsedDefaultValue !== undefined) {
                setValue(parsedDefaultValue)
            }
        } else {
            if (lovList.length) {
                if (Array.isArray(props.value)) {
                    setValue(props.value.map((i) => lovList.findIndex((j) => j.id === i))
                        // Force unknown values to index 0
                        .map((v) => v === -1 ? 0 : v))
                }
                else {
                    const val = lovList.findIndex((item) => item.id === props.value);
                    setValue(val === -1 ? 0 : val);
                }
            } else {
                setValue(Array.isArray(props.value) ? props.value as number[] : props.value as number);
            }
        }
    }, [props.value, lovList, parsedDefaultValue, convertValue]);

    return (
        <Box sx={textAnchorSx} className={className}>
            {getText(value, true)}
            <Tooltip title={hover || ""}>
                {Array.isArray(parsedDefaultValue)
                    ?
                    <MuiSlider
                        id={id}
                        value={value}
                        onChange={handleChange}
                        onChangeCommitted={handleChangeCommitted}
                        disabled={!active}
                        valueLabelDisplay="auto"
                        min={min}
                        max={max}
                        step={step}
                        marks={marks}
                        valueLabelFormat={getLabel}
                        orientation={horizontalOrientation ? undefined : "vertical"}
                        getAriaLabel={emptyString}
                        aria-label={undefined}
                    />
                    :
                    <MuiSlider
                        id={id}
                        value={value ? value : 0}
                        onChange={handleChange}
                        onChangeCommitted={handleChangeCommitted}
                        disabled={!active}
                        valueLabelDisplay="auto"
                        min={min}
                        max={max}
                        step={step}
                        marks={marks}
                        valueLabelFormat={getLabel}
                        orientation={horizontalOrientation ? undefined : "vertical"}
                    />
                }
            </Tooltip>
            {getText(value, false)}
        </Box>
    );
};

export default Slider;
