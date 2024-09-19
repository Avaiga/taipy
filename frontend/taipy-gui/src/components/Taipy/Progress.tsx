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
import { getSuffixedClassNames, getCssSize, TaipyBaseProps } from "./utils";
import { SxProps } from "@mui/material/styles";
import { Theme } from "@mui/system";

interface ProgressBarProps extends TaipyBaseProps {
    value?: number;
    defaultValue?: number;
    linear?: boolean;
    showValue?: boolean;
    title?: string;
    defaultTitle?: string;
    titleAnchor?: "top" | "bottom" | "left" | "right" | "none";
    render?: boolean;
    defaultRender?: boolean;
    width?: string | number;
}

const linearSx = { display: "flex", alignItems: "center", width: "100%" };
const linearPrgSx = { width: "100%", mr: 1 };
const titleSx = { margin: 1 };
const linearValueSx = { minWidth: 35 };
const circularSx = { position: "relative", display: "inline-flex" };
const circularValueSx = {
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
            linearProgressFullWidthSx: {
                width: "100%",
            },
        };
    }, [props.width, title, titleAnchor]);

    const circularProgressSize = useMemo(() => {
        return props.width ? getCssSize(props.width) : undefined;
    }, [props.width]);

    const { boxWithFlexDirectionSx, circularBoxSx, linearProgressFullWidthSx } =
        memoizedValues;

    if (!render) {
        return null;
    }

    return <Box sx={linear ? boxWithFlexDirectionSx : circularBoxSx} className={className} id={props.id}>
        {title && titleAnchor !== "none" ? (
            <Typography sx={titleSx} variant="caption" className={getSuffixedClassNames(className, "-title")}>
                {title}
            </Typography>
        ) : null}
        {showValue && value !== undefined ?
            (linear ?
                <Box sx={linearSx}>
                    <Box sx={linearPrgSx}>
                        <LinearProgress variant="determinate" value={value} />
                    </Box>
                    <Box sx={linearValueSx}>
                        <Typography className={getSuffixedClassNames(className, "-value")} variant="body2" color="text.secondary">{`${Math.round(value)}%`}</Typography>
                    </Box>
                </Box>
                :
                <Box sx={circularSx}>
                    <CircularProgress
                        variant="determinate"
                        value={value}
                        size={circularProgressSize}
                    />
                    <Box sx={circularValueSx}>
                        <Typography className={getSuffixedClassNames(className, "-value")} variant="body2" component="div" color="text.secondary">
                            {`${Math.round(value)}%`}
                        </Typography>
                    </Box>
                </Box>)
            :
            (linear ?
                <LinearProgress
                    sx={linearProgressFullWidthSx}
                    variant={value === undefined ? "indeterminate" : "determinate"}
                    value={value}
                />
                :
                <CircularProgress
                    variant={value === undefined ? "indeterminate" : "determinate"}
                    value={value}
                    size={circularProgressSize}
                />)
        }
    </Box>;
};

export default Progress;
