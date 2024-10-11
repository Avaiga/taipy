import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Data, Layout, Frame, PlotlyHTMLElement } from "plotly.js";
import Plot from "react-plotly.js";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import Skeleton from "@mui/material/Skeleton";
import { useTheme } from "@mui/system";

import { getArrayValue, getUpdateVar, TaipyActiveProps, TaipyChangeProps } from "./utils";
import {
    createRequestChartUpdateAction,
    createSendActionNameAction,
    createSendUpdateAction,
} from "../../context/taipyReducers";
import { ColumnDesc } from "./tableUtils";
import {
    useClassNames,
    useDispatch,
    useDispatchRequestUpdateOnFirstRender,
    useDynamicJsonProperty,
    useDynamicProperty,
    useModule,
} from "../../utils/hooks";

interface AnimatedChartProps extends TaipyActiveProps, TaipyChangeProps {
    title?: string;
    width?: string | number;
    height?: string | number;
    defaultConfig: string;
    config?: string;
    data?: Record<string, TraceValueType>;
    defaultLayout?: string;
    layout?: string;
    plotConfig?: string;
    onRangeChange?: string;
    testId?: string;
    render?: boolean;
    defaultRender?: boolean;
    template?: string;
    template_Dark_?: string;
    template_Light_?: string;
    frames?: Frame[];
    animationConfig?: Partial<Plotly.AnimationAttributes>;
}

interface ChartConfig {
    columns: Record<string, ColumnDesc>;
    labels: string[];
    modes: string[];
    types: string[];
    traces: string[][];
    decimators?: string[];
}

export type TraceValueType = Record<string, (string | number)[]>;

const defaultStyle = { position: "relative", display: "inline-block" };

const AnimatedChart = (props: AnimatedChartProps) => {
    const {
        title = "",
        width = "100%",
        height,
        updateVarName,
        updateVars,
        id,
        data = {},
        onRangeChange,
        propagate = true,
        frames,
        animationConfig,
        render = true,
        defaultRender = true
    } = props;

    const dispatch = useDispatch();
    const [selected, setSelected] = useState<number[][]>([]);
    const plotRef = useRef<PlotlyHTMLElement | null>(null);
    const [dataKey, setDataKey] = useState("__default__");
    
    const theme = useTheme();
    
    const [loading, setLoading] = useState(true);

    const refresh = typeof data === "number" ? data : 0;

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    
    const baseLayout = useDynamicJsonProperty(
        props.layout,
        props.defaultLayout || "",
        {} as Record<string, Record<string, unknown>>
    );

    const config = useDynamicJsonProperty(props.config, props.defaultConfig, {} as ChartConfig);

    const shouldRender = useDynamicProperty(render, defaultRender);

    useDispatchRequestUpdateOnFirstRender(dispatch, updateVarName, refresh);

    useEffect(() => {
        if (refresh || !data[dataKey]) {
            const backCols = Object.values(config.columns).map((col) => col.dfid);
            const dtKey = backCols.join("-") + (config.decimators ? `--${config.decimators.join("")}` : "");
            setDataKey(dtKey);
            if (refresh || !data[dtKey]) {
                dispatch(
                    createRequestChartUpdateAction(
                        updateVarName,
                        id,
                        backCols,
                        dtKey
                    )
                );
            }
        }
        
        if (data[dataKey]) {
            setLoading(false);
        }
        
    }, [refresh, dispatch, config.columns, config.decimators, updateVarName, id, data, dataKey]);

    const layout = useMemo(() => {
        const templateKey = `template_${theme.palette.mode}_`;
        const template = props[templateKey as keyof AnimatedChartProps] || props.template;
        return {
            ...baseLayout,
            title: title || baseLayout.title,
            clickmode: "event+select",
            template: template,
        } as Layout;
    }, [baseLayout, theme.palette.mode, title, props]);

    const style = useMemo(() => ({
        ...defaultStyle,
        width: width,
        height: height ? height : 'auto'
    }), [width, height]);

    const dataPl = useMemo(() => {
        if (!data[dataKey]) return [];

        return config.traces.map((traceGroup) => {
            return traceGroup.map((traceId, index) => {
                const traceData = data[dataKey][traceId];
                if (!traceData) return null;

                const type = config.types[index] || 'scatter';
                const mode = config.modes[index] || 'lines+markers';
                const label = config.labels[index] || getColNameFromIndexed(traceId);

                return {
                    x: traceData.map((value: any) => value.x),
                    y: traceData.map((value: any) => value.y),
                    type: type,
                    mode: mode,
                    name: label,
                    marker: {
                        size: 6,
                        color: theme.palette.primary.main,
                    },
                };
            }).filter(Boolean);
        }).flat();
    }, [data, config, dataKey, theme]);

    const onAfterPlot = useCallback(() => {
        setLoading(false);
    }, []);

    const handleClick = useCallback((event: Readonly<Plotly.PlotMouseEvent>) => {
        if (propagate && isOnClick(config.types)) {
            const pointNumber = event.points[0].pointNumber;
            const pointIndex = event.points[0].pointIndex;
            const newSelected = [[pointNumber, pointIndex]];
            setSelected(newSelected);
            
            if (updateVars) {
                const value = getArrayValue(newSelected, 1);
                dispatch(createSendUpdateAction(getUpdateVar(updateVars, 0), value, id));
            }
        }
    }, [config.types, propagate, updateVars, id, dispatch]);

    const handleRangeChange = useCallback((event: Readonly<Plotly.PlotRelayoutEvent>) => {
        if (onRangeChange) {
            dispatch(createSendActionNameAction(onRangeChange, event, id));
        }
    }, [onRangeChange, id, dispatch]);

    return shouldRender ? (
        <Box id={id} data-testid={props.testId} className={className}>
            {loading && <Skeleton variant="rectangular" sx={{ ...style }} />}
            <Tooltip title={title || ""}>
                <Plot
                    data={dataPl}
                    layout={layout}
                    frames={frames}
                    config={{
                        ...JSON.parse(props.plotConfig || "{}"),
                        displayModeBar: true,
                        scrollZoom: true,
                    }}
                    style={style}
                    useResizeHandler={true}
                    onClick={handleClick}
                    onRelayout={handleRangeChange}
                    onInitialized={(figure) => (plotRef.current = figure)}
                    onAfterPlot={onAfterPlot}
                    onAnimated={() => {
                        if (animationConfig && plotRef.current) {
                            plotRef.current.animate(frames || [], animationConfig);
                        }
                    }}
                />
            </Tooltip>
        </Box>
    ) : null;
};

const getColNameFromIndexed = (dfid: string): string => {
    return dfid.split('.').pop() || dfid;
};

const isOnClick = (types: string[]): boolean => {
    return types.some(type => ['scatter', 'bar', 'pie', 'heatmap'].includes(type));
};

export default AnimatedChart;