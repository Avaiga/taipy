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

import React, { useState, useEffect, useCallback, useMemo } from "react";
import CardHeader from "@mui/material/CardHeader";
import MuiButton from "@mui/material/Button";
import Tooltip from "@mui/material/Tooltip";

import { createSendActionNameAction } from "../../context/taipyReducers";
import { getCssSize, getSuffixedClassNames, TaipyActiveProps } from "./utils";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";
import { stringIcon, Icon, IconAvatar } from "../../utils/icon";

interface ButtonProps extends TaipyActiveProps {
    onAction?: string;
    label: string;
    defaultLabel?: string;
    width?: string | number;
}

const cardSx = { p: 0 };

const Button = (props: ButtonProps) => {
    const { id, onAction = "", defaultLabel } = props;
    const [value, setValue] = useState<stringIcon>("");
    const dispatch = useDispatch();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const buttonSx = useMemo(() => (props.width ? { width: getCssSize(props.width) } : undefined), [props.width]);

    const handleClick = useCallback(() => {
        dispatch(createSendActionNameAction(id, module, onAction));
    }, [id, onAction, dispatch, module]);

    useEffect(() => {
        setValue((val) => {
            if (props.label === undefined && defaultLabel) {
                try {
                    return JSON.parse(defaultLabel) as Icon;
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
        <Tooltip title={hover || ""}>
            <MuiButton
                id={id}
                variant="outlined"
                className={className}
                onClick={handleClick}
                disabled={!active}
                sx={buttonSx}
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
            </MuiButton>
        </Tooltip>
    );
};

export default Button;
