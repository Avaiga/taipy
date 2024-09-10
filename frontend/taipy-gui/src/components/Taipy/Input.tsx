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

import React, { useState, useEffect, useCallback, useRef, KeyboardEvent, useMemo, CSSProperties } from "react";
import IconButton from "@mui/material/IconButton";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import ArrowDropUpIcon from "@mui/icons-material/ArrowDropUp";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";

import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import { getCssSize, TaipyInputProps } from "./utils";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";

const AUTHORIZED_KEYS = ["Enter", "Escape", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"];

const getActionKeys = (keys?: string): string[] => {
    const ak = (
        keys
            ? keys
                  .split(";")
                  .map((v) => v.trim().toLowerCase())
                  .filter((v) => AUTHORIZED_KEYS.some((k) => k.toLowerCase() === v))
            : []
    ).map((v) => AUTHORIZED_KEYS.find((k) => k.toLowerCase() == v) as string);
    return ak.length > 0 ? ak : [AUTHORIZED_KEYS[0]];
};

const numberSx = {
    "& input[type=number]::-webkit-outer-spin-button, & input[type=number]::-webkit-inner-spin-button": {
        display: "none",
    },
    "& input[type=number]": {
        MozAppearance: "textfield",
    },
};
const verticalDivStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: 0,
};

const Input = (props: TaipyInputProps) => {
    const {
        type,
        id,
        updateVarName,
        propagate = true,
        defaultValue = "",
        onAction,
        onChange,
        multiline = false,
        linesShown = 5,
    } = props;

    const [value, setValue] = useState(defaultValue);
    const dispatch = useDispatch();
    const delayCall = useRef(-1);
    const [actionKeys] = useState(() => getActionKeys(props.actionKeys));
    const module = useModule();

    const changeDelay = typeof props.changeDelay === "number" ? (props.changeDelay >= 0 ? props.changeDelay : -1) : 300;
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const step = useDynamicProperty(props.step, props.defaultStep, 1);
    const stepMultiplier = useDynamicProperty(props.stepMultiplier, props.defaultStepMultiplier, 10);
    const min = useDynamicProperty(props.min, props.defaultMin, undefined);
    const max = useDynamicProperty(props.max, props.defaultMax, undefined);

    const textSx = useMemo(
        () =>
            props.width
                ? {
                      ...numberSx,
                      maxWidth: getCssSize(props.width),
                  }
                : numberSx,
        [props.width]
    );

    const updateValueWithDelay = useCallback(
        (value: number | string) => {
            if (changeDelay === -1) {
                return;
            }
            if (changeDelay === 0) {
                // Workaround using microtask to ensure the value is updated before the next action to avoid the bad setState behavior
                Promise.resolve().then(() => {
                    dispatch(createSendUpdateAction(updateVarName, value, module, onChange, propagate));
                });
                return;
            }
            if (delayCall.current > 0) {
                clearTimeout(delayCall.current);
            }
            delayCall.current = window.setTimeout(() => {
                delayCall.current = -1;
                dispatch(createSendUpdateAction(updateVarName, value, module, onChange, propagate));
            }, changeDelay);
        },
        [changeDelay, dispatch, updateVarName, module, onChange, propagate]
    );

    const handleInput = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const val = e.target.value;
            setValue(val);
            dispatch(createSendUpdateAction(updateVarName, val, module, onChange, propagate));
        },
        [updateVarName, dispatch, propagate, onChange, module]
    );

    const handleAction = useCallback(
        (evt: KeyboardEvent<HTMLDivElement>) => {
            if (evt.shiftKey && type === "number") {
                if (evt.key === "ArrowUp") {
                    let val =
                        Number(evt.currentTarget.querySelector("input")?.value || 0) +
                        (step || 1) * (stepMultiplier || 10);
                    if (max !== undefined && val > max) {
                        val = max;
                    }
                    setValue(val.toString());
                    updateValueWithDelay(val);
                    evt.preventDefault();
                } else if (evt.key === "ArrowDown") {
                    let val =
                        Number(evt.currentTarget.querySelector("input")?.value || 0) -
                        (step || 1) * (stepMultiplier || 10);
                    if (min !== undefined && val < min) {
                        val = min;
                    }
                    setValue(val.toString());
                    updateValueWithDelay(val);
                    evt.preventDefault();
                }
            } else if (!evt.shiftKey && !evt.ctrlKey && !evt.altKey && actionKeys.includes(evt.key)) {
                const val = multiline ? evt.currentTarget.querySelector("textarea")?.value : evt.currentTarget.querySelector("input")?.value;
                if (changeDelay > 0 && delayCall.current > 0) {
                    clearTimeout(delayCall.current);
                    delayCall.current = -1;
                    dispatch(createSendUpdateAction(updateVarName, val, module, onChange, propagate));
                } else if (changeDelay === -1) {
                    dispatch(createSendUpdateAction(updateVarName, val, module, onChange, propagate));
                }
                onAction && dispatch(createSendActionNameAction(id, module, onAction, evt.key, updateVarName, val));
                evt.preventDefault();
            }
        },
        [
            type,
            multiline,
            actionKeys,
            step,
            stepMultiplier,
            max,
            updateValueWithDelay,
            onAction,
            dispatch,
            id,
            module,
            updateVarName,
            min,
            changeDelay,
            onChange,
            propagate,
        ]
    );

    const roundBasedOnStep = useMemo(() => {
        const stepString = (step || 1).toString();
        const decimalPlaces = stepString.includes(".") ? stepString.split(".")[1].length : 0;
        const multiplier = Math.pow(10, decimalPlaces);
        return (value: number) => Math.round(value * multiplier) / multiplier;
    }, [step]);

    const calculateNewValue = useMemo(() => {
        return (prevValue: string, step: number, stepMultiplier: number, shiftKey: boolean, increment: boolean) => {
            const multiplier = shiftKey ? stepMultiplier : 1;
            const change = step * multiplier * (increment ? 1 : -1);
            return roundBasedOnStep(Number(prevValue) + change).toString();
        };
    }, [roundBasedOnStep]);

    const handleStepperMouseDown = useCallback(
        (event: React.MouseEvent<HTMLButtonElement>, increment: boolean) => {
            setValue((prevValue) => {
                const newValue = calculateNewValue(
                    prevValue,
                    step || 1,
                    stepMultiplier || 10,
                    event.shiftKey,
                    increment
                );

                if (min !== undefined && Number(newValue) < min) {
                    updateValueWithDelay(min);
                    return min.toString();
                }

                if (max !== undefined && Number(newValue) > max) {
                    updateValueWithDelay(max);
                    return max.toString();
                }

                updateValueWithDelay(newValue);
                return newValue;
            });
        },
        [calculateNewValue, step, stepMultiplier, min, max, updateValueWithDelay]
    );

    const handleUpStepperMouseDown = useCallback(
        (event: React.MouseEvent<HTMLButtonElement>) => {
            handleStepperMouseDown(event, true);
        },
        [handleStepperMouseDown]
    );

    const handleDownStepperMouseDown = useCallback(
        (event: React.MouseEvent<HTMLButtonElement>) => {
            handleStepperMouseDown(event, false);
        },
        [handleStepperMouseDown]
    );

    // password
    const [showPassword, setShowPassword] = useState(false);
    const handleClickShowPassword = useCallback(() => setShowPassword((show) => !show), []);
    const handleMouseDownPassword = useCallback(
        (event: React.MouseEvent<HTMLButtonElement>) => event.preventDefault(),
        []
    );
    const muiInputProps = useMemo(
        () =>
            type == "password"
                ? {
                      endAdornment: (
                          <IconButton
                              aria-label="toggle password visibility"
                              onClick={handleClickShowPassword}
                              onMouseDown={handleMouseDownPassword}
                              edge="end"
                          >
                              {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                      ),
                  }
                : type == "number"
                  ? {
                        endAdornment: (
                            <div style={verticalDivStyle}>
                                <IconButton
                                    aria-label="Increment value"
                                    size="small"
                                    onMouseDown={handleUpStepperMouseDown}
                                >
                                    <ArrowDropUpIcon fontSize="inherit" />
                                </IconButton>
                                <IconButton
                                    aria-label="Decrement value"
                                    size="small"
                                    onMouseDown={handleDownStepperMouseDown}
                                >
                                    <ArrowDropDownIcon fontSize="inherit" />
                                </IconButton>
                            </div>
                        ),
                    }
                  : undefined,
        [
            type,
            showPassword,
            handleClickShowPassword,
            handleMouseDownPassword,
            handleUpStepperMouseDown,
            handleDownStepperMouseDown,
        ]
    );

    const inputProps = useMemo(
        () =>
            type == "number"
                ? {
                      step: step ? step : 1,
                      min: min,
                      max: max,
                  }
                : type == "password"
                  ? { autoComplete: "current-password" }
                  : undefined,
        [type, step, min, max]
    );

    useEffect(() => {
        if (props.value !== undefined) {
            setValue(props.value);
        }
    }, [props.value]);

    return (
        <Tooltip title={hover || ""}>
            <TextField
                sx={textSx}
                margin="dense"
                hiddenLabel
                value={value ?? ""}
                className={className}
                type={showPassword && type == "password" ? "text" : type}
                id={id}
                inputProps={inputProps}
                InputProps={muiInputProps}
                label={props.label}
                onChange={handleInput}
                disabled={!active}
                onKeyDown={handleAction}
                multiline={multiline}
                minRows={linesShown}
            />
        </Tooltip>
    );
};
export default Input;
