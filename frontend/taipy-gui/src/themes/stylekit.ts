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

import { lighten } from "@mui/material";
import { TaipyConfig } from "../utils";

export const stylekitTheme = (config?: TaipyConfig) => ({
    palette: {
        // Primary and secondary colors
        primary: {
            main: config?.stylekit?.colorPrimary,
        },
        secondary: {
            main: config?.stylekit?.colorSecondary,
        },
        error: {
            main: config?.stylekit?.colorError,
        },
        warning: {
            main: config?.stylekit?.colorWarning,
        },
        success: {
            main: config?.stylekit?.colorSuccess,
        },
    },
    typography: {
        // Custom font
        fontFamily: config?.stylekit?.fontFamily,
        h6: {
            fontSize: "1rem",
        },
    },
    shape: {
        borderRadius: config?.stylekit?.borderRadius,
    },
    // Components normalization
    components: {
        // Paper element
        MuiPaper: {
            styleOverrides: {
                root: {
                    // Remove the unwanted linear gradient overlay on the paper background color
                    backgroundImage: "none",
                },
            },
        },
        // Form control
        MuiFormControl: {
            styleOverrides: {
                root: {
                    marginTop: 4,
                    width: "100%",
                    maxWidth: "15rem",
                    verticalAlign: "middle",
                },
            },
        },
        // Form label
        MuiInputLabel: {
            styleOverrides: {
                outlined: {
                    zIndex: "0",
                    transition: "all 200ms cubic-bezier(0, 0, 0.2, 1) 0ms",
                    // Properly position floating label on Y axis (second translate value) as the input height changes
                    "&:not(.MuiInputLabel-shrink):not(.static-label)": {
                        top: "50%",
                        transform: "translate(14px, -50%) scale(1)",
                    },
                    "&.static-label": {
                        position: "relative",
                        transform: "none",
                    },
                },
            },
        },
        // Form input
        MuiInputBase: {
            styleOverrides: {
                root: {
                    // Fill the available width
                    display: "flex",
                },
                input: {
                    minHeight: config?.stylekit?.inputButtonHeight,
                    boxSizing: "border-box",

                    // for textarea height calculation
                    "&.MuiInputBase-inputMultiline": {
                        minHeight: "unset",
                    },
                    // for small size
                    "&.MuiInputBase-inputSizeSmall": {
                        minHeight: 'unset',
                    }
                },
            },
        },
        MuiSelect: {
            styleOverrides: {
                select: {
                    display: "flex",
                    alignItems: "center",
                    minHeight: config?.stylekit?.inputButtonHeight,
                    boxSizing: "border-box",
                    paddingTop: 8,
                    paddingBottom: 8,
                },
            },
        },
        // Button
        MuiButton: {
            styleOverrides: {
                root: {
                    height: "auto",
                    marginBottom: 4,
                    "&.MuiButton-sizeMedium": {
                        minHeight: config?.stylekit?.inputButtonHeight,
                    },
                    "&.MuiButton-sizeLarge": {
                        lineHeight: config?.stylekit?.inputButtonHeight,
                    },
                },
            },
        },
        // Mui slider
        MuiSlider: {
            styleOverrides: {
                rail: {
                    ".taipy-indicator &": {
                        // Use success and error color for heat gradient
                        background:
                            "linear-gradient(90deg, " +
                            config?.stylekit?.colorError +
                            " 0%, " +
                            config?.stylekit?.colorSuccess +
                            " 100%)",
                    },
                },
            },
        },
        MuiSwitch: {
            styleOverrides: {
                switchBase: {
                    minHeight: "unset",
                },
            },
        },
        // Mui table
        MuiTable: {
            styleOverrides: {
                root: {
                    "& .MuiTableCell-root": {
                        textAlign: "left",
                    },
                },
            },
        },

        MuiTableRow: {
            styleOverrides: {
                root: {
                    "&:hover": {
                        backgroundColor: "rgba(0, 0, 0, 0.08)",
                    },
                    "&.Mui-selected": {
                        backgroundColor: "rgba(245, 197, 197, 0.86)", // Selected color
                    },
                    "&.Mui-selected:hover": {
                        backgroundColor: "rgba(234, 140, 140, 0.8)", // Selected + hover color
                    },
                },
            },
        },

    },
});

export const stylekitModeThemes = (config: TaipyConfig) => ({
    light: {
        palette: {
            background: {
                // Main background
                default: config?.stylekit?.colorBackgroundLight,
                // Cards background
                paper: config?.stylekit?.colorPaperLight,
            },
        },
        components: {
            // Give popover paper a slightly lighter color to reflect superior elevation
            MuiPopover: {
                styleOverrides: {
                    paper: {
                        backgroundColor: config?.stylekit?.colorPaperLight
                            ? lighten(config?.stylekit.colorPaperLight, 0.5)
                            : undefined,
                    },
                },
            },
            // Give MuiSlider disabled thumb a fill color matching the theme
            MuiSlider: {
                styleOverrides: {
                    thumb: {
                        ".Mui-disabled &::before": {
                            backgroundColor: config?.stylekit?.colorPaperLight,
                        },
                    },
                },
            },
        },
    },
    dark: {
        palette: {
            background: {
                // Main background
                default: config?.stylekit?.colorBackgroundDark,
                // Cards background
                paper: config?.stylekit?.colorPaperDark,
            },
        },
        components: {
            // Give popover paper a slightly lighter color to reflect superior elevation
            MuiPopover: {
                styleOverrides: {
                    paper: {
                        backgroundColor: config?.stylekit?.colorPaperDark
                            ? lighten(config?.stylekit?.colorPaperDark, 0.05)
                            : undefined,
                    },
                },
            },
            // Give MuiSlider disabled thumb a fill color matching the theme
            MuiSlider: {
                styleOverrides: {
                    thumb: {
                        ".Mui-disabled &::before": {
                            backgroundColor: config?.stylekit?.colorPaperDark,
                        },
                    },
                },
            },
        },
    },
});
