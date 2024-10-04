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

import React, { lazy, useMemo, Suspense } from "react";
import Typography from "@mui/material/Typography";
import Tooltip from "@mui/material/Tooltip";

import { formatWSValue } from "../../utils";
import { getSuffixedClassNames } from "./utils";
import { useClassNames, useDynamicProperty, useFormatConfig } from "../../utils/hooks";
import { TaipyBaseProps, TaipyHoverProps, getCssSize } from "./utils";

interface TaipyFieldProps extends TaipyBaseProps, TaipyHoverProps {
    dataType?: string;
    value: string | number;
    defaultValue?: string;
    format?: string;
    raw?: boolean;
    mode?: string;
    width?: string | number;
}

const unsetWeightSx = { fontWeight: "unset" };

const Markdown = lazy(() => import("react-markdown"));
const MathJax = lazy(() => import("better-react-mathjax").then(module => ({ default: module.MathJax })));
const MathJaxContext = lazy(() => import("better-react-mathjax").then(module => ({ default: module.MathJaxContext })));

const mathJaxConfig = {
    tex: {
        inlineMath: [["$", "$"], ["\\(", "\\)"]],
        displayMath: [["$$", "$$"], ["\\[", "\\]"]],
    }
}


const Field = (props: TaipyFieldProps) => {
    const { id, dataType, format, defaultValue, raw } = props;
    const formatConfig = useFormatConfig();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const mode = typeof props.mode === "string" ? props.mode.toLowerCase() : undefined;

    const style = useMemo(
        () => ({ overflow: "auto", width: props.width ? getCssSize(props.width) : undefined }),
        [props.width]
    );
    const typoSx = useMemo(
        () =>
            props.width
                ? { ...unsetWeightSx, overflow: "auto", width: getCssSize(props.width), display: "inline-block" }
                : unsetWeightSx,
        [props.width]
    );

    const value = useMemo(() => {
        return formatWSValue(
            props.value !== undefined ? props.value : defaultValue || "",
            dataType,
            format,
            formatConfig
        );
    }, [defaultValue, props.value, dataType, format, formatConfig]);

    return (
        <Tooltip title={hover || ""}>
            {mode == "pre" ? (
                <pre className={`${className} ${getSuffixedClassNames(className, '-' + mode)}`} id={id} style={style}>
                    {value}
                </pre>
            ) : mode == "markdown" || mode == "md" ? (
                <Markdown className={`${className} ${getSuffixedClassNames(className, '-' + mode)}`}>{value}</Markdown>
            ) : raw || mode == "raw" ? (
                <span className={`${className} ${getSuffixedClassNames(className, '-' + mode)}`} id={id} style={style}>
                    {value}
                </span>
            ) : mode == 'latex' ? (
                <Suspense fallback={<div>Loading LaTex...</div>}>
                    <MathJaxContext config={mathJaxConfig}>
                        <MathJax className={`${className} ${getSuffixedClassNames(className, '-' + mode)}`} id={id}>
                            {value}
                        </MathJax>
                    </MathJaxContext>
                </Suspense>
            ) : (
                <Typography className={className} id={id} component="span" sx={typoSx}>
                    {value}
                </Typography>
            )}
        </Tooltip>
    );
};

export default Field;
