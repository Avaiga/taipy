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

import React, { useState, useEffect, useCallback, useRef, KeyboardEvent, useMemo } from "react";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import { styled } from "@mui/material/styles";
import IconButton from "@mui/material/IconButton";
import ArrowDropUpIcon from "@mui/icons-material/ArrowDropUp";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";

import { createSendActionNameAction, createSendUpdateAction } from "../../context/taipyReducers";
import { TaipyInputProps } from "./utils";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";

const AUTHORIZED_KEYS = ["Enter", "Escape", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"];

const StyledTextField = styled(TextField)({
    "& input[type=number]::-webkit-outer-spin-button, & input[type=number]::-webkit-inner-spin-button": {
        display: "none",
    },
    "& input[type=number]": {
        MozAppearance: "textfield",
    },
});

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

    const handleInput = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const val = e.target.value;
            setValue(val);
            if (changeDelay === 0) {
                dispatch(createSendUpdateAction(updateVarName, val, module, onChange, propagate));
                return;
            }
            if (changeDelay > 0) {
                if (delayCall.current > 0) {
                    clearTimeout(delayCall.current);
                }
                delayCall.current = window.setTimeout(() => {
                    delayCall.current = -1;
                    dispatch(createSendUpdateAction(updateVarName, val, module, onChange, propagate));
                }, changeDelay);
            }
        },
        [updateVarName, dispatch, propagate, onChange, changeDelay, module],
    );

    const handleAction = useCallback(
        (evt: KeyboardEvent<HTMLDivElement>) => {
            if (evt.shiftKey && type === "number") {
                if (evt.key === "ArrowUp") {
                    let val =
                        Number(evt.currentTarget.querySelector("input")?.value || 0) +
                        (step || 1) * (stepMultiplier || 10) -
                        (step || 1);
                    if (max !== undefined && val > max) {
                        val = max - (step || 1);
                    }
                    setValue(val.toString());
                } else if (evt.key === "ArrowDown") {
                    let val =
                        Number(evt.currentTarget.querySelector("input")?.value || 0) -
                        (step || 1) * (stepMultiplier || 10) +
                        (step || 1);
                    if (min !== undefined && val < min) {
                        val = min + (step || 1);
                    }
                    setValue(val.toString());
                }
            } else if (!evt.shiftKey && !evt.ctrlKey && !evt.altKey && actionKeys.includes(evt.key)) {
                const val = evt.currentTarget.querySelector("input")?.value;
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
            actionKeys,
            step,
            stepMultiplier,
            max,
            min,
            changeDelay,
            onAction,
            dispatch,
            id,
            module,
            updateVarName,
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
                    return min.toString();
                }
                if (max !== undefined && Number(newValue) > max) {
                    return max.toString();
                }
                return newValue;
            });
        },
        [min, max, step, stepMultiplier, calculateNewValue],
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

    useEffect(() => {
        if (props.value !== undefined) {
            setValue(props.value);
        }
    }, [props.value]);

    return (
        <Tooltip title={hover || ""}>
            <StyledTextField
                margin="dense"
                hiddenLabel
                value={value ?? ""}
                className={className}
                type={type}
                id={id}
                inputProps={
                    type !== "text"
                        ? {
                              step: step ? step : 1,
                              min: min,
                              max: max,
                          }
                        : {}
                }
                InputProps={
                    type !== "text"
                        ? {
                              endAdornment: (
                                  <>
                                      <IconButton size="small" onMouseDown={handleUpStepperMouseDown}>
                                          <ArrowDropUpIcon />
                                      </IconButton>
                                      <IconButton size="small" onMouseDown={handleDownStepperMouseDown}>
                                          <ArrowDropDownIcon />
                                      </IconButton>
                                  </>
                              ),
                          }
                        : {}
                }
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
