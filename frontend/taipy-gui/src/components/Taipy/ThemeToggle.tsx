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

import React, { CSSProperties, MouseEvent, useCallback, useContext, useEffect, useMemo } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { PaletteMode } from "@mui/material";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import WbSunny from "@mui/icons-material/WbSunny";
import Brightness3 from "@mui/icons-material/Brightness3";

import { TaipyActiveProps, emptyStyle } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createThemeAction } from "../../context/taipyReducers";
import { useClassNames } from "../../utils/hooks";
import { getLocalStorageValue } from "../../context/utils";

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

const groupSx = { verticalAlign: "middle" };

const ThemeToggle = (props: ThemeToggleProps) => {
    const { id, label = "Mode", style = emptyStyle, active = true } = props;
    const { state, dispatch } = useContext(TaipyContext);

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    const changeMode = useCallback(
        (evt: MouseEvent, mode: PaletteMode) => mode !== null && dispatch(createThemeAction(mode === "dark")),
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
                sx={groupSx}
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
