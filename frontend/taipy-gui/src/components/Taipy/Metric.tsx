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
import {Data} from "plotly.js";
import Box from "@mui/material/Box";
import Skeleton from "@mui/material/Skeleton";
import Tooltip from "@mui/material/Tooltip";
import {useClassNames, useDynamicJsonProperty, useDynamicProperty} from "../../utils/hooks";
import {extractPrefix, extractSuffix, sprintfToD3Converter} from "../../utils/formatConversion";
import {TaipyBaseProps, TaipyHoverProps} from "./utils";
import {useTheme} from "@mui/material";

const Plot = lazy(() => import("react-plotly.js"));

interface MetricProps extends TaipyBaseProps, TaipyHoverProps {
    type?: string
    min?: number
    max?: number
    value?: number
    defaultValue?: number
    delta?: number
    defaultDelta?: number
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
    template?: string;
    template_Dark_?: string;
    template_Light_?: string;
}

const emptyLayout = {} as Record<string, Record<string, unknown>>;
const defaultStyle = {position: "relative", display: "inline-block"};

const Metric = (props: MetricProps) => {
    const {
        width = "100%",
        height,
        showValue = true
    } = props;
    const value = useDynamicProperty(props.value, props.defaultValue, 0)
    const threshold = useDynamicProperty(props.threshold, props.defaultThreshold, undefined)
    const delta = useDynamicProperty(props.delta, props.defaultDelta, undefined)
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const baseLayout = useDynamicJsonProperty(props.layout, props.defaultLayout || "", emptyLayout);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const theme = useTheme();

    const data = useMemo(() => {
        return [
            {
                domain: {x: [0, 1], y: [0, 1]},
                value: value,
                type: "indicator",
                mode: "gauge" + (showValue ? "+number" : "") + (delta !== undefined ? "+delta" : ""),
                number: {
                    prefix: extractPrefix(props.format),
                    suffix: extractSuffix(props.format),
                    valueformat: sprintfToD3Converter(props.format),
                },
                delta: {
                    reference: typeof value === 'number' && typeof delta === 'number' ? value - delta : undefined,
                    prefix: extractPrefix(props.deltaFormat),
                    suffix: extractSuffix(props.deltaFormat),
                    valueformat: sprintfToD3Converter(props.deltaFormat)
                },
                gauge: {
                    axis: {
                        range: [
                            props.min || 0,
                            props.max || 100
                        ]
                    },
                    shape: props.type === "linear" ? "bullet" : "angular",
                    threshold: {
                        line: {color: "red", width: 4},
                        thickness: 0.75,
                        value: threshold
                    }
                },
            }
        ];
    }, [
        props.format,
        props.deltaFormat,
        props.min,
        props.max,
        props.type,
        value,
        showValue,
        delta,
        threshold
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

        return layout
    }, [
        props.template,
        props.template_Dark_,
        props.template_Light_,
        theme.palette.mode,
        baseLayout
    ])

    return (
        <Box data-testid={props.testId} className={className}>
            <Tooltip title={hover || ""}>
                <Suspense fallback={<Skeleton key="skeleton" sx={skelStyle}/>}>
                    <Plot
                        data={data as Data[]}
                        layout={layout}
                        style={style}
                        useResizeHandler
                    />
                </Suspense>
            </Tooltip>
        </Box>
    );
}

export default Metric;

const darkTemplate = {
    layout: {
        colorscale: {
            diverging: [
                [0, "#8e0152"],
                [0.1, "#c51b7d"],
                [0.2, "#de77ae"],
                [0.3, "#f1b6da"],
                [0.4, "#fde0ef"],
                [0.5, "#f7f7f7"],
                [0.6, "#e6f5d0"],
                [0.7, "#b8e186"],
                [0.8, "#7fbc41"],
                [0.9, "#4d9221"],
                [1, "#276419"],
            ],
            sequential: [
                [0.0, "#0d0887"],
                [0.1111111111111111, "#46039f"],
                [0.2222222222222222, "#7201a8"],
                [0.3333333333333333, "#9c179e"],
                [0.4444444444444444, "#bd3786"],
                [0.5555555555555556, "#d8576b"],
                [0.6666666666666666, "#ed7953"],
                [0.7777777777777778, "#fb9f3a"],
                [0.8888888888888888, "#fdca26"],
                [1.0, "#f0f921"],
            ],
            sequentialminus: [
                [0.0, "#0d0887"],
                [0.1111111111111111, "#46039f"],
                [0.2222222222222222, "#7201a8"],
                [0.3333333333333333, "#9c179e"],
                [0.4444444444444444, "#bd3786"],
                [0.5555555555555556, "#d8576b"],
                [0.6666666666666666, "#ed7953"],
                [0.7777777777777778, "#fb9f3a"],
                [0.8888888888888888, "#fdca26"],
                [1.0, "#f0f921"],
            ],
        },
        colorway: [
            "#636efa",
            "#EF553B",
            "#00cc96",
            "#ab63fa",
            "#FFA15A",
            "#19d3f3",
            "#FF6692",
            "#B6E880",
            "#FF97FF",
            "#FECB52",
        ],
        font: {
            color: "#f2f5fa",
        },
        paper_bgcolor: "rgb(31,47,68)",
    },
};
