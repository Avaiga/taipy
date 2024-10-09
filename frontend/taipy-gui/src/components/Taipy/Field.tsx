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

import React, { lazy, useMemo } from "react";
import Typography from "@mui/material/Typography";
import Tooltip from "@mui/material/Tooltip";
import { Components } from "react-markdown";

import { formatWSValue } from "../../utils";
import { useClassNames, useDynamicProperty, useFormatConfig } from "../../utils/hooks";
import { TaipyBaseProps, TaipyHoverProps, getCssSize } from "./utils";
import { getComponentClassName } from "./TaipyStyle";

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

const Field = (props: TaipyFieldProps) => {
    const { id, dataType, format, defaultValue, raw } = props;
    const formatConfig = useFormatConfig();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const markdownComponent: Components = {
        h1(props) {
            return <h1 className={`${className} ${getComponentClassName(props.children)}`} {...props} />
        },
        h2(props) {
            return <h2 className={`${className} ${getComponentClassName(props.children)}`} {...props} />
        },
        h3(props) {
            return <h3 className={`${className} ${getComponentClassName(props.children)}`} {...props} />
        },
        h4(props) {
            return <h4 className={`${className} ${getComponentClassName(props.children)}`} {...props} />
        },
        h5(props) {
            return <h5 className={`${className} ${getComponentClassName(props.children)}`}  {...props} />
        },
        h6(props) {
            return <h6 className={`${className} ${getComponentClassName(props.children)}`} {...props} />
        },
        p(props) {
            return <span className={`${className} ${getComponentClassName(props.children)}`} {...props}/>
        }
    }
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
            <>
                {mode == "pre" ? (
                    <pre className={`${className} ${getComponentClassName(props.children)}`} id={id} style={style}>
                        {value}
                    </pre>
                ) : mode == "markdown" || mode == "md" ? (
                    <Markdown components={markdownComponent}>{value}</Markdown>
                ) : raw || mode == "raw" ? (
                    <span className={className} id={id} style={style}>
                        {value}
                    </span>
                ) : (
                    <Typography
                        className={`${className} ${getComponentClassName(props.children)}`}
                        id={id}
                        component="span"
                        sx={typoSx}
                    >
                        {value}
                    </Typography>
                )}
                {props.children}
            </>
        </Tooltip>
    );
};

export default Field;
