import React, { CSSProperties, MouseEvent, useCallback, useContext, useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Tooltip from "@mui/material/Tooltip";

import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import ThemeToggle from "./ThemeToggle";
import { LovProps, useLovListMemo } from "./lovUtils";
import { useDynamicProperty } from "../../utils/hooks";
import { getUpdateVar } from "./utils";
import { Icon, IconAvatar } from "../../utils/icon";

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
        className,
        lov,
        defaultLov = "",
        unselectedValue = "",
        updateVars = "",
        valueById,
    } = props;
    const { dispatch } = useContext(TaipyContext);
    const [value, setValue] = useState(props.defaultValue)
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
                    props.tp_onChange,
                    propagate,
                    valueById ? undefined : getUpdateVar(updateVars, "lov")
                )
            )},
        [unselectedValue, updateVarName, propagate, dispatch, updateVars, valueById, props.tp_onChange, props.allowUnselect]
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
