/*
 * Copyright 2023 Avaiga Private Limited
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

import React, { useState, useEffect, useCallback } from "react";
import MuiButton from "@mui/material/Button";
import Tooltip from "@mui/material/Tooltip";

import { createSendActionNameAction } from "../../context/taipyReducers";
import { getSuffixedClassNames, TaipyActiveProps } from "./utils";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";
import { stringIcon, Icon, IconAvatar } from "../../utils/icon";

interface ButtonProps extends TaipyActiveProps {
    onAction?: string;
    label: string;
    defaultLabel?: string;
}

const Button = (props: ButtonProps) => {
    const { id, onAction = "", defaultLabel } = props;
    const [value, setValue] = useState<stringIcon>("");
    const dispatch = useDispatch();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

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
            <MuiButton id={id} variant="outlined" className={className} onClick={handleClick} disabled={!active}>
                {typeof value === "string" ? (
                    value
                ) : (
                    <IconAvatar img={value as Icon} className={getSuffixedClassNames(className, "-image")} />
                )}
            </MuiButton>
        </Tooltip>
    );
};

export default Button;
