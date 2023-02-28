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

export const stylekitTheme = {
    palette: {
        // Primary and secondary colors
        primary: {
            main: window.taipyConfig?.stylekit?.colorPrimary,
        },
        secondary: {
            main: window.taipyConfig?.stylekit?.colorSecondary,
        },
        error: {
            main: window.taipyConfig?.stylekit?.colorError,
        },
        warning: {
            main: window.taipyConfig?.stylekit?.colorWarning,
        },
        success: {
            main: window.taipyConfig?.stylekit?.colorSuccess,
        },
    },
    typography: {
        // Custom font
        fontFamily: window.taipyConfig?.stylekit?.fontFamily,
        h6: {
            fontSize: "1rem",
        },
    },
    shape: {
        borderRadius: window.taipyConfig?.stylekit?.borderRadius,
    },
    // Components normalization
    components: {
        // Form control
        MuiFormControl: {
            styleOverrides: {
                root: {
                    // Fill the available width
                    display: "flex",

                    // Removing vertical margins if placed in a layout to avoid y-alignment issues
                    ".taipy-layout > .taipy-part > .md-para > &": {
                        "&:first-child": {
                            mt: 0,
                        },
                        "&:last-child": {
                            mb: 0,
                        },
                    },
                },
            },
        },
        // Form label
        MuiInputLabel: {
            styleOverrides: {
                outlined: {
                    zIndex: "0",
                    // Properly position floating label on Y axis (second translate value) as the input height changes
                    "&:not(.MuiInputLabel-shrink)": {
                        transform: "translate(14px, 12px) scale(1)",
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
                    height: window.taipyConfig?.stylekit?.inputButtonHeight,
                    boxSizing: "border-box",

                    ".MuiInputBase-root &": {
                        py: 4
                    },
                },
            },
        },
        MuiSelect: {
            styleOverrides: {
                select: {
                    display: "flex",
                    alignItems: "center",
                    height: window.taipyConfig?.stylekit?.inputButtonHeight,
                    lineHeight: window.taipyConfig?.stylekit?.inputButtonHeight,
                    boxSizing: "border-box",

                    "&.MuiInputBase-input": {
                        py: 0
                    },
                },
            },
        },
        // Button
        MuiButtonBase: {
            styleOverrides: {
                root: {
                    height: "auto",
                    minHeight: window.taipyConfig?.stylekit?.inputButtonHeight,
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
                            window.taipyConfig?.stylekit?.colorError +
                            " 0%, " +
                            window.taipyConfig?.stylekit?.colorSuccess +
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
            }
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
    },
};

export const stylekitModeThemes = {
    light: {
        palette: {
            background: {
                // Main background
                default: window.taipyConfig?.stylekit?.colorBackgroundLight,
                // Cards background
                paper: window.taipyConfig?.stylekit?.colorPaperLight,
            },
        },
        components: {
            // Give MuiSlider disabled thumb a fill color matching the theme
            MuiSlider: {
                styleOverrides: {
                    thumb: {
                        ".Mui-disabled &::before": {
                            backgroundColor: window.taipyConfig?.stylekit?.colorPaperLight,
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
                default: window.taipyConfig?.stylekit?.colorBackgroundDark,
                // Cards background
                paper: window.taipyConfig?.stylekit?.colorPaperDark,
            },
        },
        components: {
            // Give MuiSlider disabled thumb a fill color matching the theme
            MuiSlider: {
                styleOverrides: {
                    thumb: {
                        ".Mui-disabled &::before": {
                            backgroundColor: window.taipyConfig?.stylekit?.colorPaperDark,
                        },
                    },
                },
            },
        },
    },
};
