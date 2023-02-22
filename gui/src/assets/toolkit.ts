export const toolkitTheme = {
    palette: {
        // Primary and secondary colors
        primary: {
            main: window.taipyConfig.toolkit?.colorPrimary,
        },
        secondary: {
            main: window.taipyConfig.toolkit?.colorSecondary,
        },
        error: {
            main: window.taipyConfig.toolkit?.colorError,
        },
        warning: {
            main: window.taipyConfig.toolkit?.colorWarning,
        },
        success: {
            main: window.taipyConfig.toolkit?.colorSuccess,
        },
    },
    typography: {
        // Custom font
        fontFamily: window.taipyConfig.toolkit?.fontFamily,
        h6: {
            fontSize: "1rem",
        },
    },
    shape: {
        borderRadius: window.taipyConfig.toolkit?.borderRadius,
    },
    // Components normalization
    components: {
        // Form control
        MuiFormControl: {
            styleOverrides: {
                root: {
                    // Fill the available width
                    display: "flex",

                    "&.taipy-selector": {
                        marginLeft: 0,
                        marginRight: 0,
                    },

                    ".taipy-tree &": {
                        marginBottom: "1rem",
                        paddingLeft: "1rem",
                        paddingRight: "1rem",
                    },

                    // Removing vertical margins if placed in a layout to avoid y-alignment issues
                    ".taipy-layout > .taipy-part > .md-para > &": {
                        "&:first-child": {
                            marginTop: 0,
                        },
                        "&:last-child": {
                            marginBottom: 0,
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
                    height: window.taipyConfig.toolkit?.inputButtonHeight,
                    boxSizing: "border-box",

                    ".MuiInputBase-root &": {
                        paddingTop: 4,
                        paddingBottom: 4,
                    },
                },
            },
        },
        MuiSelect: {
            styleOverrides: {
                select: {
                    display: "flex",
                    alignItems: "center",
                    height: window.taipyConfig.toolkit?.inputButtonHeight,
                    lineHeight: window.taipyConfig.toolkit?.inputButtonHeight,
                    boxSizing: "border-box",

                    "&.MuiInputBase-input": {
                        paddingTop: 0,
                        paddingBottom: 0,
                    },
                },
            },
        },
        // Button
        MuiButtonBase: {
            styleOverrides: {
                root: {
                    height: "auto",
                    minHeight: window.taipyConfig.toolkit?.inputButtonHeight,
                },
            },
        },
        // Floating action button
        MuiFab: {
            styleOverrides: {
                root: {
                    ".taipy-file-download &, .taipy-file-selector &": {
                        height: window.taipyConfig.toolkit?.inputButtonHeight,
                        paddingLeft: "1em",
                        paddingRight: "1em",
                        gap: "0.5em",
                        backgroundColor: "transparent",
                        borderWidth: 1,
                        borderColor: window.taipyConfig.toolkit?.colorPrimary,
                        borderStyle: "solid",
                        borderRadius: window.taipyConfig.toolkit?.borderRadius,
                        boxShadow: "none",
                        color: window.taipyConfig.toolkit?.colorPrimary,
                        zIndex: "auto",
                    },
                },
            },
        },
        // Toggle button group
        MuiToggleButtonGroup: {
            styleOverrides: {
                root: {
                    verticalAlign: "middle",
                },
            },
        },
        // Mui paper
        MuiPaper: {
            styleOverrides: {
                root: {
                    ".taipy-tree &": {
                        overflow: "hidden",
                        paddingTop: "1rem",
                        paddingBottom: "1rem",
                    },
                },
            },
        },
        // Mui list
        MuiList: {
            styleOverrides: {
                root: {
                    ".taipy-selector .MuiPaper-root &": {
                        maxWidth: "100%",
                        backgroundColor: "transparent",
                    },
                },
            },
        },
        // Mui treeview
        MuiTreeView: {
            styleOverrides: {
                root: {
                    ".taipy-tree .MuiPaper-root &": {
                        maxWidth: "100%",
                        backgroundColor: "transparent",
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
                            window.taipyConfig.toolkit?.colorError +
                            " 0%, " +
                            window.taipyConfig.toolkit?.colorSuccess +
                            " 100%)",
                    },
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
    },
};

export const toolkitModeThemes = {
    light: {
        palette: {
            background: {
                // Main background
                default: window.taipyConfig.toolkit?.colorBackgroundLight,
                // Cards background
                paper: window.taipyConfig.toolkit?.colorPaperLight,
            },
        },
        components: {
            // Give MuiSlider disabled thumb a fill color matching the theme
            MuiSlider: {
                styleOverrides: {
                    thumb: {
                        ".Mui-disabled &::before": {
                            backgroundColor: window.taipyConfig.toolkit?.colorPaperLight,
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
                default: window.taipyConfig.toolkit?.colorBackgroundDark,
                // Cards background
                paper: window.taipyConfig.toolkit?.colorPaperDark,
            },
        },
        components: {
            // Give MuiSlider disabled thumb a fill color matching the theme
            MuiSlider: {
                styleOverrides: {
                    thumb: {
                        ".Mui-disabled &::before": {
                            backgroundColor: window.taipyConfig.toolkit?.colorPaperDark,
                        },
                    },
                },
            },
        },
    },
};
