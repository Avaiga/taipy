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

import React, { CSSProperties, MouseEvent, useCallback, useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Tooltip from "@mui/material/Tooltip";

import { createSendUpdateAction } from "../../context/taipyReducers";
import ThemeToggle from "./ThemeToggle";
import { LovProps, useLovListMemo } from "./lovUtils";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";
import { getUpdateVar } from "./utils";
import { Icon, IconAvatar } from "../../utils/icon";

const groupSx = {verticalAlign: "middle"};

interface ToggleProps extends LovProps<string> {
    style?: CSSProperties;
    label?: string;
    kind?: string;
    unselectedValue?: string;
    allowUnselect?: boolean;
}

const Toggle = (props: ToggleProps) => {
    const {
        id,
        style = {},
        kind,
        label,
        updateVarName = "",
        propagate = true,
        lov,
        defaultLov = "",
        unselectedValue = "",
        updateVars = "",
        valueById,
    } = props;
    const dispatch = useDispatch();
    const [value, setValue] = useState(props.defaultValue);
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const lovList = useLovListMemo(lov, defaultLov);

    const changeValue = useCallback(
        (evt: MouseEvent, val: string) => {
            if (!props.allowUnselect && val === null ) {
                return;
            }
            dispatch(
                createSendUpdateAction(
                    updateVarName,
                    val === null ? unselectedValue : val,
                    module,
                    props.onChange,
                    propagate,
                    valueById ? undefined : getUpdateVar(updateVars, "lov")
                )
            )},
        [unselectedValue, updateVarName, propagate, dispatch, updateVars, valueById, props.onChange, props.allowUnselect, module]
    );

    useEffect(() => {props.value !== undefined && setValue(props.value)}, [props.value]);

    return kind === "theme" ? (
        <ThemeToggle {...props} />
    ) : (
        <Box id={id} sx={style} className={className}>
            {label ? <Typography>{label}</Typography> : null}
            <Tooltip title={hover || ""}>
                <ToggleButtonGroup
                    value={value}
                    exclusive
                    onChange={changeValue}
                    disabled={!active}
                    sx={groupSx}
                >
                    {lovList &&
                        lovList.map((v) => (
                            <ToggleButton value={v.id} key={v.id}>
                                {typeof v.item === "string" ? (
                                    <Typography>{v.item}</Typography>
                                ) : (
                                    <IconAvatar id={v.id} img={v.item as Icon} />
                                )}
                            </ToggleButton>
                        ))}
                </ToggleButtonGroup>
            </Tooltip>
        </Box>
    );
};

export default Toggle;
