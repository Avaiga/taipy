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
    linear?: boolean; //by default - false
    showValue?: boolean; //by default - false
    value?: number; //progress value
    defaultValue?: number; //default progress value
    render?: boolean;
    defaultRender?: boolean;
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

const Progress = (props: ProgressBarProps) => {
    const { linear = false, showValue = false } = props;

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const value = useDynamicProperty(props.value, props.defaultValue, undefined, "number", true);
    const render = useDynamicProperty(props.render, props.defaultRender, true);

    if (!render) {
        return null;
    }

    return showValue && value !== undefined ? (
        linear ? (
            <Box sx={linearSx} className={className} id={props.id}>
                <Box sx={linearPrgSx}>
                    <LinearProgress variant="determinate" value={value} />
                </Box>
                <Box sx={linearTxtSx}>
                    <Typography variant="body2" color="text.secondary">{`${Math.round(value)}%`}</Typography>
                </Box>
            </Box>
        ) : (
            <Box sx={circularSx} className={className} id={props.id}>
                <CircularProgress variant="determinate" value={value} />
                <Box sx={circularPrgSx}>
                    <Typography variant="caption" component="div" color="text.secondary">
                        {`${Math.round(value)}%`}
                    </Typography>
                </Box>
            </Box>
        )
    ) : linear ? (
        <LinearProgress
            id={props.id}
            variant={value === undefined ? "indeterminate" : "determinate"}
            value={value}
            className={className}
        />
    ) : (
        <CircularProgress
            id={props.id}
            variant={value === undefined ? "indeterminate" : "determinate"}
            value={value}
            className={className}
        />
    );
};

export default Progress;
