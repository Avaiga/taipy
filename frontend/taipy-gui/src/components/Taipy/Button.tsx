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

import React, { useState, useEffect, useCallback, useMemo, useRef } from "react";
import CardHeader from "@mui/material/CardHeader";
import MuiButton from "@mui/material/Button";
import Tooltip from "@mui/material/Tooltip";

import { getCssSize, getSuffixedClassNames, TaipyActiveProps } from "./utils";
import { useClassNames, useDynamicProperty } from "../../utils/hooks";
import { stringIcon, Icon, IconAvatar } from "../../utils/icon";
import { getComponentClassName } from "./TaipyStyle";
import { useActions } from "../../hooks";

interface ButtonProps extends TaipyActiveProps {
    onAction?: string;
    label: string;
    defaultLabel?: string;
    width?: string | number;
    size?: "small" | "medium" | "large";
    variant?: "text" | "outlined" | "contained";
    autoRepeat?: number;
}

const cardSx = { p: 0 };
const initialRepeatDelay = 500; // Initial delay before auto-repeat starts (in ms)

const Button = (props: ButtonProps) => {
    // TODO: Allow default value for auto_repeat in the builder
    const { id, onAction = "", defaultLabel, size = "medium", variant = "outlined" } = props;
    const [value, setValue] = useState<stringIcon>("");
    const { sendAction } = useActions();
    const autoRepeatInitialRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const autoRepeatIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const buttonSx = useMemo(() => (props.width ? { width: getCssSize(props.width) } : undefined), [props.width]);

    const handleClick = useCallback(() => {
        sendAction(id, onAction);
    }, [id, onAction, sendAction]);

    // Handle auto-repeat
    const autoRepeatDelay = useMemo(() => {
        if (props.autoRepeat && props.autoRepeat > 0) {
            return props.autoRepeat;
        }
        return 0; // No auto-repeat delay by default
    }, [props.autoRepeat]);

    const startRepeating = useCallback(() => {
        if (autoRepeatInitialRef.current || autoRepeatIntervalRef.current) {
            // Prevent simultaneous repeats
            return;
        }
        handleClick(); // Trigger immediately
        autoRepeatInitialRef.current = setTimeout(() => {
            autoRepeatIntervalRef.current = setInterval(handleClick, autoRepeatDelay);
            autoRepeatInitialRef.current = null;
        }, initialRepeatDelay);
    }, [handleClick, autoRepeatDelay]);

    const stopRepeating = () => {
        if (autoRepeatInitialRef.current) {
            clearTimeout(autoRepeatInitialRef.current);
            autoRepeatInitialRef.current = null;
        }
        if (autoRepeatIntervalRef.current) {
            clearInterval(autoRepeatIntervalRef.current);
            autoRepeatIntervalRef.current = null;
        }
    };

    useEffect(() => {
        setValue((val) => {
            if (props.label === undefined && defaultLabel) {
                try {
                    return JSON.parse(defaultLabel) as Icon;
                } catch {
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
        <Tooltip title={hover || ""}>
            <MuiButton
                id={id}
                variant={variant}
                size={size}
                className={`${className} ${getComponentClassName(props.children)}`}
                onClick={handleClick}
                disabled={!active}
                sx={buttonSx}
                onMouseDown={autoRepeatDelay ? startRepeating : undefined}
                onPointerDown={autoRepeatDelay ? startRepeating : undefined}
                onMouseUp={autoRepeatDelay ? stopRepeating : undefined}
                onMouseLeave={autoRepeatDelay ? stopRepeating : undefined}
                onTouchStart={autoRepeatDelay ? startRepeating : undefined}
                onTouchEnd={autoRepeatDelay ? stopRepeating : undefined}
            >
                {typeof value === "string" ? (
                    value
                ) : (value as Icon).text ? (
                    <CardHeader
                        sx={cardSx}
                        avatar={
                            <IconAvatar img={value as Icon} className={getSuffixedClassNames(className, "-image")} />
                        }
                        title={(value as Icon).text}
                        disableTypography={true}
                        className={getSuffixedClassNames(className, "-image-text")}
                    />
                ) : (
                    <IconAvatar img={value as Icon} className={getSuffixedClassNames(className, "-image")} />
                )}
                {props.children}
            </MuiButton>
        </Tooltip>
    );
};

export default Button;
