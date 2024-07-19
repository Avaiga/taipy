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

import React, {CSSProperties, lazy, Suspense, useMemo} from 'react';
import {Data, Delta, Layout} from "plotly.js";
import Box from "@mui/material/Box";
import Skeleton from "@mui/material/Skeleton";
import Tooltip from "@mui/material/Tooltip";
import {useTheme} from "@mui/material";
import {useClassNames, useDynamicJsonProperty, useDynamicProperty} from "../../utils/hooks";
import {extractPrefix, extractSuffix, sprintfToD3Converter} from "../../utils/formatConversion";
import {TaipyBaseProps, TaipyHoverProps} from "./utils";
import {darkThemeTemplate} from "../../themes/darkThemeTemplate";

const Plot = lazy(() => import("react-plotly.js"));

interface MetricProps extends TaipyBaseProps, TaipyHoverProps {
    title?: string
    type?: string
    min?: number
    max?: number
    value?: number
    defaultValue?: number
    delta?: number
    defaultDelta?: number
    deltaColor?: string
    negativeDeltaColor?: string
    threshold?: number
    defaultThreshold?: number
    testId?: string
    defaultLayout?: string;
    layout?: string;
    defaultStyle?: string;
    style?: string;
    width?: string | number;
    height?: string | number;
    showValue?: boolean;
    format?: string;
    deltaFormat?: string;
    colorMap?: string;
    template?: string;
    template_Dark_?: string;
    template_Light_?: string;
}

const emptyLayout = {} as Partial<Layout>;
const defaultStyle = {position: "relative", display: "inline-block"};

const Metric = (props: MetricProps) => {
    const {
        width = "100%",
        height,
        showValue = true,
        deltaColor,
        negativeDeltaColor
    } = props;
    const value = useDynamicProperty(props.value, props.defaultValue, 0)
    const threshold = useDynamicProperty(props.threshold, props.defaultThreshold, undefined)
    const delta = useDynamicProperty(props.delta, props.defaultDelta, undefined)
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const baseLayout = useDynamicJsonProperty(props.layout, props.defaultLayout || "", emptyLayout);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const theme = useTheme();

    const colorMap = useMemo(() => {
        try {
            const obj = props.colorMap ? JSON.parse(props.colorMap) : null;
            if (obj && typeof obj === 'object') {
                const keys = Object.keys(obj);
                return keys.sort((a, b) => Number(a) - Number(b)).map((key, index) => {
                    const nextKey = keys[index + 1] !== undefined ? Number(keys[index + 1]) : props.max || 100;
                    return {range: [Number(key), nextKey], color: obj[key]};
                }).filter(item => item.color !== null)
            }
        } catch (e) {
            console.info(`Error parsing color_map value (metric).\n${(e as Error).message || e}`);
        }
        return undefined;
    }, [props.colorMap, props.max])

    const data = useMemo(() => {
        const mode = (props.type === "none") ? [] : ["gauge"];
        showValue && mode.push("number");
        (delta !== undefined) && mode.push("delta");
        const deltaIncreasing = deltaColor ? {
            color: deltaColor == "invert" ? "#FF4136" : deltaColor } : undefined
        const deltaDecreasing = negativeDeltaColor ? {
                color: deltaColor == "invert" ? "#3D9970" : negativeDeltaColor
            } : undefined
        return [
            {
                domain: {x: [0, 1], y: [0, 1]},
                value: value,
                type: "indicator",
                mode: mode.join("+"),
                number: {
                    prefix: extractPrefix(props.format),
                    suffix: extractSuffix(props.format),
                    valueformat: sprintfToD3Converter(props.format),
                },
                delta: {
                    reference: typeof value === 'number' && typeof delta === 'number' ? value - delta : undefined,
                    prefix: extractPrefix(props.deltaFormat),
                    suffix: extractSuffix(props.deltaFormat),
                    valueformat: sprintfToD3Converter(props.deltaFormat),
                    increasing: deltaIncreasing,
                    decreasing: deltaDecreasing

                } as Partial<Delta>,
                gauge: {
                    axis: {
                        range: [
                            props.min || 0,
                            props.max || 100
                        ]
                    },
                    steps: colorMap,
                    shape: props.type === "linear" ? "bullet" : "angular",
                    threshold: {
                        line: {color: "red", width: 4},
                        thickness: 0.75,
                        value: threshold
                    }
                },
            }
        ] as Data[];
    }, [
        props.format,
        props.deltaFormat,
        props.min,
        props.max,
        props.type,
        value,
        showValue,
        deltaColor,
        negativeDeltaColor,
        delta,
        threshold,
        colorMap
    ]);

    const style = useMemo(
        () =>
            height === undefined
                ? ({...defaultStyle, width: width} as CSSProperties)
                : ({...defaultStyle, width: width, height: height} as CSSProperties),
        [height, width]
    );

    const skelStyle = useMemo(() => ({...style, minHeight: "7em"}), [style]);

    const layout = useMemo(() => {
        const layout = {...baseLayout};
        let template = undefined;
        try {
            const tpl = props.template && JSON.parse(props.template);
            const tplTheme =
                theme.palette.mode === "dark"
                    ? props.template_Dark_
                        ? JSON.parse(props.template_Dark_)
                        : darkTemplate
                    : props.template_Light_ && JSON.parse(props.template_Light_);
            template = tpl ? (tplTheme ? {...tpl, ...tplTheme} : tpl) : tplTheme ? tplTheme : undefined;
        } catch (e) {
            console.info(`Error while parsing Metric.template\n${(e as Error).message || e}`);
        }
        if (template) {
            layout.template = template;
        }

        if (props.title) {
            layout.title = props.title;
        }

        return layout as Partial<Layout>;
    }, [
        props.title,
        props.template,
        props.template_Dark_,
        props.template_Light_,
        theme.palette.mode,
        baseLayout,
    ])

    return (
        <Tooltip title={hover || ""}>
            <Box data-testid={props.testId} className={className}>
                <Suspense fallback={<Skeleton key="skeleton" sx={skelStyle}/>}>
                    <Plot
                        data={data}
                        layout={layout}
                        style={style}
                        useResizeHandler
                    />
                </Suspense>
            </Box>
        </Tooltip>
    );
}

export default Metric;

const {colorscale, colorway, font} = darkThemeTemplate.layout;
const darkTemplate = {
    layout: {
        colorscale,
        colorway,
        font,
        paper_bgcolor: "rgb(31,47,68)",
    },
}
