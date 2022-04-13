import React, { CSSProperties, MouseEvent, useCallback, useContext, useEffect, useMemo } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { PaletteMode } from "@mui/material";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import WbSunny from "@mui/icons-material/WbSunny";
import Brightness3 from "@mui/icons-material/Brightness3";

import { TaipyActiveProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createThemeAction, getLocalStorageValue } from "../../context/taipyReducers";

interface ThemeToggleProps extends TaipyActiveProps {
    style?: CSSProperties;
    label?: string;
}

const boxSx = {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    position: "fixed",
    top: "1rem",
    right: "1rem",
    "& > *": {
        m: 1,
    },
} as CSSProperties;

const ThemeToggle = (props: ThemeToggleProps) => {
    const { id, label = "Mode", style = {}, className, active = true } = props;
    const { state, dispatch } = useContext(TaipyContext);

    const changeMode = useCallback(
        (evt: MouseEvent, mode: PaletteMode) => dispatch(createThemeAction(mode === "dark")),
        [dispatch]
    );

    useEffect(() => {
        const localMode = getLocalStorageValue("theme", state.theme.palette.mode, ["light", "dark"]);
        if (state.theme.palette.mode !== localMode) {
            dispatch(createThemeAction(localMode === "dark"));
        }
    }, [state.theme.palette.mode, dispatch]);

    const mainSx = useMemo(() => ({ ...boxSx, ...style }), [style]);
    return (
        <Box id={id} sx={mainSx} className={className}>
            <Typography>{label}</Typography>
            <ToggleButtonGroup
                value={state.theme.palette.mode}
                exclusive
                onChange={changeMode}
                aria-label="Theme mode"
                disabled={!active}
            >
                <ToggleButton value="light" aria-label="light" title="Light">
                    <WbSunny />
                </ToggleButton>
                <ToggleButton value="dark" aria-label="dark" title="Dark">
                    <Brightness3 />
                </ToggleButton>
            </ToggleButtonGroup>
        </Box>
    );
};

export default ThemeToggle;
