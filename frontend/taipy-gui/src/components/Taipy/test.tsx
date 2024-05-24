import React from "react";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";

import { useDynamicProperty } from "../../utils/hooks";

interface ProgressBarProps {
    linear?: boolean; //by default - false
    showValue?: boolean; //by default - false
    value?: number; //progress value
    defaultValue?: number; //default progress value
}

const Progress = (props: ProgressBarProps) => {
    const { linear, showValue } = props;

    const value = useDynamicProperty(props.value, props.defaultValue, undefined);

    return showValue && value !== undefined ? (
        linear ? (
            <Box sx={{ display: "flex", alignItems: "center" }}>
                <Box sx={{ width: "100%", mr: 1 }}>
                    <LinearProgress variant="determinate" value={value} />
                </Box>
                <Box sx={{ minWidth: 35 }}>
                    <Typography variant="body2" color="text.secondary">{`${Math.round(value)}%`}</Typography>
                </Box>
            </Box>
        ) : (
            <Box sx={{ position: "relative", display: "inline-flex" }}>
                <CircularProgress variant="determinate" value={value} />
                <Box
                    sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: "absolute",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                    }}
                >
                    <Typography variant="caption" component="div" color="text.secondary">
                        {`${Math.round(value)}%`}
                    </Typography>
                </Box>
            </Box>
        )
    ) : linear ? (
        <LinearProgress variant={value === undefined ? "indeterminate": "determinate"} value={value} />
    ) : (
        <CircularProgress variant={value === undefined ? "indeterminate": "determinate"} value={value} />
    );
};

export default Progress;
