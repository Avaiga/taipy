/*
 * Copyright 2021-2025 Avaiga Private Limited
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
import { getComponentClassName } from "./TaipyStyle";

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
const noPaddingYSx = { py: 0 };
const IsInteger = 2;

// numberType: 0 -> not a number, 1 -> number, 2 -> integer
const valToNumber = (val: string, numberType: number) =>
    numberType ? (numberType === IsInteger ? Math.round(Number(val)) : Number(val)) : val;

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
        actionOnBlur = false,
        linesShown = 5,
        size = "medium",
    } = props;

    const [value, setValue] = useState(defaultValue);
    const dispatch = useDispatch();
    const delayCall = useRef<ReturnType<typeof setTimeout> | null>(null);
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
        [props.width],
    );

    // 0 if value is not a number, 1 means general number, 2 means integer
    const numberType = useMemo<number>(() => {
        return type === "number" ? (props.integer === true ? IsInteger : 1) : 0;
    }, [type, props.integer]);

    const updateValueWithDelay = useCallback(
        (value: number | string) => {
            if (changeDelay === -1) {
                return;
            }
            if (numberType) {
                value = numberType === IsInteger ? Math.round(Number(value)) : Number(value);
            }
            if (changeDelay === 0) {
                // Workaround using microtask to ensure the value is updated before the next action to avoid the bad setState behavior
                Promise.resolve().then(() => {
                    dispatch(createSendUpdateAction(updateVarName, value, module, onChange, propagate));
                });
                return;
            }
            if (delayCall.current !== null) {
                clearTimeout(delayCall.current);
            }
            delayCall.current = setTimeout(() => {
                delayCall.current = null;
                dispatch(createSendUpdateAction(updateVarName, value, module, onChange, propagate));
            }, changeDelay);
        },
        [changeDelay, numberType, dispatch, updateVarName, module, onChange, propagate],
    );

    const handleInput = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const val = e.target.value;
            if (numberType === IsInteger && !/^-?\d*$/.test(val)) {
                return;
            }
            setValue(val);
            if (changeDelay === -1) {
                return;
            }
            if (changeDelay === 0) {
                Promise.resolve().then(() => {
                    dispatch(
                        createSendUpdateAction(
                            updateVarName,
                            valToNumber(val, numberType),
                            module,
                            onChange,
                            propagate,
                        ),
                    );
                });
            }
            if (delayCall.current !== null) {
                clearTimeout(delayCall.current);
            }
            delayCall.current = setTimeout(() => {
                delayCall.current = null;
                dispatch(
                    createSendUpdateAction(updateVarName, valToNumber(val, numberType), module, onChange, propagate),
                );
            }, changeDelay);
        },
        [changeDelay, numberType, dispatch, updateVarName, module, onChange, propagate],
    );

    const handleBlur = useCallback(
        (evt: React.FocusEvent<HTMLInputElement>) => {
            let val = numberType
                ? numberType === IsInteger
                    ? Math.round(Number(evt.currentTarget.value))
                    : Number(evt.currentTarget.value)
                : evt.currentTarget.value;
            if (numberType) {
                if (min !== undefined && (val as number) < min) {
                    val = min;
                }
                if (max !== undefined && (val as number) > max) {
                    val = max;
                }
            }
            if (delayCall.current !== null || changeDelay === -1) {
                if (delayCall.current !== null && changeDelay > 0) {
                    clearTimeout(delayCall.current);
                    delayCall.current = null;
                }
                dispatch(createSendUpdateAction(updateVarName, val, module, onChange, propagate));
            }
            onAction &&
                Promise.resolve().then(() => {
                    dispatch(createSendActionNameAction(id, module, onAction, "Tab", updateVarName, val));
                });
            evt.preventDefault();
        },
        [dispatch, numberType, min, max, updateVarName, module, onChange, propagate, changeDelay, id, onAction],
    );

    const handleAction = useCallback(
        (evt: KeyboardEvent<HTMLDivElement>) => {
            if (evt.shiftKey && numberType) {
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
                const val = multiline
                    ? evt.currentTarget.querySelector("textarea")?.value
                    : numberType
                      ? numberType === IsInteger
                          ? Math.round(Number(evt.currentTarget.querySelector("input")?.value))
                          : Number(evt.currentTarget.querySelector("input")?.value)
                      : evt.currentTarget.querySelector("input")?.value;

                if (changeDelay > 0 && delayCall.current !== null) {
                    clearTimeout(delayCall.current);
                    delayCall.current = null;
                    dispatch(createSendUpdateAction(updateVarName, val, module, onChange, propagate));
                } else if (changeDelay === -1) {
                    dispatch(createSendUpdateAction(updateVarName, val, module, onChange, propagate));
                }
                onAction && dispatch(createSendActionNameAction(id, module, onAction, evt.key, updateVarName, val));
                evt.preventDefault();
            }
        },
        [
            numberType,
            multiline,
            actionKeys,
            step,
            stepMultiplier,
            min,
            max,
            updateValueWithDelay,
            onAction,
            dispatch,
            id,
            module,
            updateVarName,
            changeDelay,
            onChange,
            propagate,
        ],
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
                    increment,
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
        [calculateNewValue, step, stepMultiplier, min, max, updateValueWithDelay],
    );

    const handleUpStepperMouseDown = useCallback(
        (event: React.MouseEvent<HTMLButtonElement>) => {
            handleStepperMouseDown(event, true);
        },
        [handleStepperMouseDown],
    );

    const handleDownStepperMouseDown = useCallback(
        (event: React.MouseEvent<HTMLButtonElement>) => {
            handleStepperMouseDown(event, false);
        },
        [handleStepperMouseDown],
    );

    // password
    const [showPassword, setShowPassword] = useState(false);
    const handleClickShowPassword = useCallback(() => setShowPassword((show) => !show), []);
    const handleMouseDownPassword = useCallback(
        (event: React.MouseEvent<HTMLButtonElement>) => event.preventDefault(),
        [],
    );
    const inputProps = useMemo(
        () =>
            type == "number"
                ? {
                      htmlInput: {
                          step: step ? step : 1,
                          min: min,
                          max: max,
                      },
                      input: {
                          endAdornment: (
                              <div style={verticalDivStyle}>
                                  <IconButton
                                      aria-label="Increment value"
                                      size="small"
                                      onMouseDown={handleUpStepperMouseDown}
                                      disabled={!active}
                                      sx={noPaddingYSx}
                                  >
                                      <ArrowDropUpIcon fontSize="inherit" />
                                  </IconButton>
                                  <IconButton
                                      aria-label="Decrement value"
                                      size="small"
                                      onMouseDown={handleDownStepperMouseDown}
                                      disabled={!active}
                                      sx={noPaddingYSx}
                                  >
                                      <ArrowDropDownIcon fontSize="inherit" />
                                  </IconButton>
                              </div>
                          ),
                      },
                  }
                : type == "password"
                  ? {
                        htmlInput: { autoComplete: "current-password" },
                        input: {
                            endAdornment: (
                                <IconButton
                                    aria-label="Toggle password visibility"
                                    onClick={handleClickShowPassword}
                                    onMouseDown={handleMouseDownPassword}
                                    edge="end"
                                >
                                    {showPassword ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                            ),
                        },
                    }
                  : undefined,
        [
            active,
            type,
            step,
            min,
            max,
            showPassword,
            handleClickShowPassword,
            handleMouseDownPassword,
            handleUpStepperMouseDown,
            handleDownStepperMouseDown,
        ],
    );

    useEffect(() => {
        if (props.value !== undefined) {
            setValue(props.value);
        }
    }, [props.value]);

    return (
        <>
            <Tooltip title={hover || ""}>
                <TextField
                    sx={textSx}
                    margin="dense"
                    hiddenLabel
                    value={value ?? ""}
                    className={`${className} ${getComponentClassName(props.children)}`}
                    type={showPassword && type == "password" ? "text" : type}
                    id={id}
                    slotProps={inputProps}
                    label={props.label}
                    onChange={handleInput}
                    onBlur={actionOnBlur ? handleBlur : undefined}
                    disabled={!active}
                    onKeyDown={handleAction}
                    multiline={multiline}
                    minRows={linesShown}
                    maxRows={linesShown}
                    size={size}
                />
            </Tooltip>
            {props.children}
        </>
    );
};
export default Input;
