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

import React, { MouseEvent, SyntheticEvent, useCallback, useEffect, useMemo, useState } from "react";
import Box from "@mui/material/Box";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Tooltip from "@mui/material/Tooltip";

import { createSendUpdateAction } from "../../context/taipyReducers";
import ThemeToggle, { emptyStyle } from "./ThemeToggle";
import { LovProps, useLovListMemo } from "./lovUtils";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";
import { getCssSize, getSuffixedClassNames, getUpdateVar } from "./utils";
import { Icon, IconAvatar } from "../../utils/icon";
import { FormControlLabel, SxProps } from "@mui/material";

const baseGroupSx = { verticalAlign: "middle" };

interface ToggleProps extends LovProps<string> {
    style?: SxProps;
    label?: string;
    unselectedValue?: string;
    allowUnselect?: boolean;
    mode?: string;
    isSwitch?: boolean;
    width?: string | number;
}

const Toggle = (props: ToggleProps) => {
    const {
        id,
        style = emptyStyle,
        label,
        updateVarName = "",
        propagate = true,
        lov,
        defaultLov = "",
        unselectedValue = "",
        updateVars = "",
        valueById,
        mode = "",
        isSwitch = false,
    } = props;
    const dispatch = useDispatch();
    const [value, setValue] = useState(props.defaultValue);
    const [bVal, setBVal] = useState(() =>
        typeof props.defaultValue === "boolean"
            ? props.defaultValue
            : typeof props.value === "boolean"
            ? props.value
            : false
    );
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const lovList = useLovListMemo(lov, defaultLov);

    const boxSx = useMemo(
        () => (props.width ? ({ ...style, width: getCssSize(props.width) } as SxProps) : style),
        [props.width, style]
    );

    const changeValue = useCallback(
        (evt: MouseEvent, val: string) => {
            if (!props.allowUnselect && val === null) {
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
            );
        },
        [
            unselectedValue,
            updateVarName,
            propagate,
            dispatch,
            updateVars,
            valueById,
            props.onChange,
            props.allowUnselect,
            module,
        ]
    );

    const changeSwitchValue = useCallback(
        (evt: SyntheticEvent, checked: boolean) =>
            dispatch(createSendUpdateAction(updateVarName, checked, module, props.onChange, propagate)),
        [updateVarName, dispatch, props.onChange, propagate, module]
    );

    useEffect(() => {
        typeof props.value === "boolean" ? setBVal(props.value) : props.value !== undefined && setValue(props.value);
    }, [props.value]);

    return mode.toLowerCase() === "theme" ? (
        <ThemeToggle {...props} />
    ) : (
        <Box id={id} sx={boxSx} className={className}>
            {label && !isSwitch ? <Typography>{label}</Typography> : null}
            <Tooltip title={hover || ""}>
                {isSwitch ? (
                    <FormControlLabel
                        control={<Switch />}
                        checked={bVal}
                        onChange={changeSwitchValue}
                        disabled={!active}
                        label={label}
                        className={getSuffixedClassNames(className, "-switch")}
                    />
                ) : (
                    <ToggleButtonGroup
                        value={value}
                        exclusive
                        onChange={changeValue}
                        disabled={!active}
                        sx={baseGroupSx}
                        fullWidth={!!props.width}
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
                )}
            </Tooltip>
        </Box>
    );
};

export default Toggle;
