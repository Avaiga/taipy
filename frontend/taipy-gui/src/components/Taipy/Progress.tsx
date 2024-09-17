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

import React, { useMemo } from "react";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";

import { useClassNames, useDynamicProperty } from "../../utils/hooks";
import { getCssSize, TaipyBaseProps } from "./utils";
import { SxProps } from "@mui/material/styles";
import { Theme } from "@mui/system";

interface ProgressBarProps extends TaipyBaseProps {
    color?: string;
    linear?: boolean;
    showValue?: boolean;
    value?: number;
    defaultValue?: number;
    render?: boolean;
    defaultRender?: boolean;
    title?: string;
    defaultTitle?: string;
    titleAnchor?: "top" | "bottom" | "left" | "right" | "none";
    width?: string | number;
}

const linearSx = { display: "flex", alignItems: "center", width: "100%" };
const linearPrgSx = { width: "100%", mr: 1 };
const titleSx = { margin: 1 };
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

const getFlexDirection = (titleAnchor: string) => {
    switch (titleAnchor) {
        case "top":
            return "column";
        case "left":
            return "row";
        case "right":
            return "row-reverse";
        case "bottom":
        default:
            return "column-reverse";
    }
};

const Progress = (props: ProgressBarProps) => {
    const { linear = false, showValue = false, titleAnchor = "bottom" } = props;

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const value = useDynamicProperty(props.value, props.defaultValue, undefined, "number", true);
    const render = useDynamicProperty(props.render, props.defaultRender, true);
    const title = useDynamicProperty(props.title, props.defaultTitle, undefined);

    const memoizedValues = useMemo(() => {
        return {
            boxWithFlexDirectionSx: {
                ...linearSx,
                width: props.width ? getCssSize(props.width) : "100%",
                flexDirection: getFlexDirection(titleAnchor),
            } as SxProps<Theme>,
            circularBoxSx: {
                ...circularSx,
                flexDirection: getFlexDirection(titleAnchor),
                alignItems: title && titleAnchor ? "center" : "",
            },
            linearProgressSx: {
                "& .MuiLinearProgress-bar": {
                    background: props.color ? props.color : undefined,
                },
            },
            circularProgressSx: {
                "& .MuiCircularProgress-circle": {
                    color: props.color ? props.color : undefined,
                },
            },
            linearProgressFullWidthSx: {
                width: "100%",
                "& .MuiLinearProgress-bar": {
                    background: props.color ? props.color : undefined,
                },
            },
        };
    }, [props.color, props.width, title, titleAnchor]);

    const circularProgressSize = useMemo(() => {
        return props.width ? getCssSize(props.width) : undefined;
    }, [props.width]);

    const { boxWithFlexDirectionSx, circularBoxSx, linearProgressSx, circularProgressSx, linearProgressFullWidthSx } =
        memoizedValues;

    if (!render) {
        return null;
    }

    console.log(circularProgressSize);

    return showValue && value !== undefined ? (
        linear ? (
            <Box sx={boxWithFlexDirectionSx} data-testid="linear-progress-container">
                {title && titleAnchor !== "none" ? (
                    <Typography sx={titleSx} variant="caption">
                        {title}
                    </Typography>
                ) : null}
                <Box sx={linearSx} className={className} id={props.id}>
                    <Box sx={linearPrgSx}>
                        <LinearProgress sx={linearProgressSx} variant="determinate" value={value} />
                    </Box>
                    <Box sx={linearTxtSx}>
                        <Typography variant="body2" color="text.secondary">{`${Math.round(value)}%`}</Typography>
                    </Box>
                </Box>
            </Box>
        ) : (
            <Box sx={circularBoxSx}>
                {title && titleAnchor !== "none" ? (
                    <Typography sx={titleSx} variant="caption">
                        {title}
                    </Typography>
                ) : null}
                <Box sx={circularSx} className={className} id={props.id}>
                    <CircularProgress
                        sx={circularProgressSx}
                        variant="determinate"
                        value={value}
                        size={circularProgressSize}
                    />
                    <Box sx={circularPrgSx}>
                        <Typography variant="caption" component="div" color="text.secondary">
                            {`${Math.round(value)}%`}
                        </Typography>
                    </Box>
                </Box>
            </Box>
        )
    ) : linear ? (
        <Box sx={boxWithFlexDirectionSx} data-testid="linear-progress-container">
            {title && titleAnchor !== "none" ? (
                <Typography sx={titleSx} variant="caption">
                    {title}
                </Typography>
            ) : null}
            <LinearProgress
                id={props.id}
                sx={linearProgressFullWidthSx}
                variant={value === undefined ? "indeterminate" : "determinate"}
                value={value}
                className={className}
            />
        </Box>
    ) : (
        <Box sx={circularBoxSx}>
            {title && titleAnchor !== "none" ? (
                <Typography sx={titleSx} variant="caption">
                    {title}
                </Typography>
            ) : null}
            <CircularProgress
                id={props.id}
                sx={circularProgressSx}
                variant={value === undefined ? "indeterminate" : "determinate"}
                value={value}
                className={className}
                size={circularProgressSize}
            />
        </Box>
    );
};

export default Progress;
