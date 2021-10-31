import React, { CSSProperties, MouseEvent, useCallback, useContext } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Avatar from "@mui/material/Avatar";

import { TaipyImage } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createSendUpdateAction } from "../../context/taipyReducers";
import ThemeToggle from "./ThemeToggle";
import { LovProps, useLovListMemo } from "./lovUtils";
import { useDynamicProperty } from "../../utils/hooks";

interface ToggleProps extends LovProps {
    style?: CSSProperties;
    label: string;
    theme: boolean;
}

const Toggle = (props: ToggleProps) => {
    const {
        id,
        style = {},
        theme = false,
        label,
        tp_varname = "",
        propagate = true,
        className,
        lov,
        defaultLov = "",
    } = props;
    const { dispatch } = useContext(TaipyContext);

    const active = useDynamicProperty(props.active, props.defaultActive, true);

    const lovList = useLovListMemo(lov, defaultLov);

    const changeValue = useCallback(
        (evt: MouseEvent, val: string) => dispatch(createSendUpdateAction(tp_varname, val, propagate)),
        [tp_varname, propagate, dispatch]
    );

    return theme ? (
        <ThemeToggle {...props} />
    ) : (
        <Box id={id} sx={style} className={className}>
            {label ? <Typography>{label}</Typography> : null}
            <ToggleButtonGroup
                value={props.value || props.defaultValue}
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
                                <Avatar alt={(v.item as TaipyImage).text || v.id} src={(v.item as TaipyImage).path} />
                            )}
                        </ToggleButton>
                    ))}
            </ToggleButtonGroup>
        </Box>
    );
};

export default Toggle;
