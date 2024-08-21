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

import React from "react";

import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";

import { useClassNames, useDynamicProperty } from "../../utils/hooks";
import { TaipyBaseProps } from "./utils";

interface ProgressBarProps extends TaipyBaseProps {
    color?: string; //color of the progress indicator
    linear?: boolean; //by default - false
    showValue?: boolean; //by default - false
    value?: number; //progress value
    defaultValue?: number; //default progress value
    render?: boolean;
    defaultRender?: boolean;
    title?: string;
    defaultTitle?: string;
    titleAnchor?: "top" | "bottom" | "left" | "right" | "none";
}

const linearSx = { display: "flex", alignItems: "center" };
const linearPrgSx = { width: "100%", mr: 1 };
const linearTxtSx = { minWidth: 35 };
const circularSx = { position: "relative", display: "inline-flex" };
const circularPrgSx = {
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
    position: "absolute",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
};

export const getFlexDirection = (titleAnchor: string) => {
    switch (titleAnchor) {
        case "top":
            return "column";
        case "bottom":
            return "column-reverse";
        case "left":
            return "row";
        case "right":
            return "row-reverse";
        default:
            return "row";
    }
};

export const getBoxWidth = (title?: string, titleAnchor?: string) => (title && titleAnchor ? "100%" : "");

const Progress = (props: ProgressBarProps) => {
    const { linear = false, showValue = false, titleAnchor = "bottom" } = props;

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const value = useDynamicProperty(props.value, props.defaultValue, undefined, "number", true);
    const render = useDynamicProperty(props.render, props.defaultRender, true);
    const title = useDynamicProperty(props.title, props.defaultTitle, undefined);

    if (!render) {
        return null;
    }

    return showValue && value !== undefined ? (
        linear ? (
            <Box sx={{ ...linearSx, flexDirection: getFlexDirection(titleAnchor) }}>
                {title && titleAnchor !== "none" ? (
                    <Typography sx={{ margin: 1 }} variant="caption">
                        {title}
                    </Typography>
                ) : null}
                <Box sx={{ ...linearSx, width: getBoxWidth(title, titleAnchor) }} className={className} id={props.id}>
                    <Box sx={linearPrgSx}>
                        <LinearProgress
                            sx={{
                                "& .MuiLinearProgress-bar": {
                                    background: props.color ? props.color : undefined,
                                },
                            }}
                            data-progress={value}
                            variant="determinate"
                            value={value}
                        />
                    </Box>
                    <Box sx={linearTxtSx}>
                        <Typography variant="body2" color="text.secondary">{`${Math.round(value)}%`}</Typography>
                    </Box>
                </Box>
            </Box>
        ) : (
            <Box
                sx={{
                    ...circularSx,
                    flexDirection: getFlexDirection(titleAnchor),
                    alignItems: title && titleAnchor ? "center" : "",
                }}
            >
                {title && titleAnchor !== "none" ? (
                    <Typography sx={{ margin: 1 }} variant="caption">
                        {title}
                    </Typography>
                ) : null}
                <Box sx={{ ...circularSx, width: getBoxWidth(title, titleAnchor) }} className={className} id={props.id}>
                    <CircularProgress data-progress={value} variant="determinate" value={value} />
                    <Box sx={circularPrgSx}>
                        <Typography variant="caption" component="div" color="text.secondary">
                            {`${Math.round(value)}%`}
                        </Typography>
                    </Box>
                </Box>
            </Box>
        )
    ) : linear ? (
        <Box sx={{ ...linearSx, flexDirection: getFlexDirection(titleAnchor) }}>
            {title && titleAnchor !== "none" ? (
                <Typography sx={{ margin: 1 }} variant="caption">
                    {title}
                </Typography>
            ) : null}
            <LinearProgress
                id={props.id}
                sx={{
                    width: "100%",
                    "& .MuiLinearProgress-bar": {
                        background: props.color ? props.color : undefined,
                    },
                }}
                variant={value === undefined ? "indeterminate" : "determinate"}
                value={value}
                className={className}
                data-progress={value}
            />
        </Box>
    ) : (
        <Box
            sx={{
                ...circularSx,
                flexDirection: getFlexDirection(titleAnchor),
                alignItems: title && titleAnchor ? "center" : "",
            }}
        >
            {title && titleAnchor !== "none" ? (
                <Typography sx={{ margin: 1 }} variant="caption">
                    {title}
                </Typography>
            ) : null}
            <CircularProgress
                id={props.id}
                variant={value === undefined ? "indeterminate" : "determinate"}
                value={value}
                className={className}
                data-progress={value}
            />
        </Box>
    );
};

export default Progress;
