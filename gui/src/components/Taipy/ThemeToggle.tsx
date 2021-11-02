import React, { CSSProperties, MouseEvent, useCallback, useContext, useMemo } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { PaletteMode } from "@mui/material";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import WbSunny from "@mui/icons-material/WbSunny";
import Brightness3 from "@mui/icons-material/Brightness3";

import { TaipyBaseProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createThemeAction } from "../../context/taipyReducers";

interface ThemeToggleProps extends TaipyBaseProps {
    style?: CSSProperties;
    label: string;
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
                <ToggleButton value="light" aria-label="light">
                    <WbSunny />
                </ToggleButton>
                <ToggleButton value="dark" aria-label="dark">
                    <Brightness3 />
                </ToggleButton>
            </ToggleButtonGroup>
        </Box>
    );
};

export default ThemeToggle;
