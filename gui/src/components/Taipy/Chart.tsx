import React, {
    CSSProperties,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useRef,
    useState,
    lazy,
    Suspense,
} from "react";
import {
    Data,
    Layout,
    PlotMarker,
    PlotRelayoutEvent,
    PlotMouseEvent,
    PlotSelectionEvent,
    ScatterLine,
} from "plotly.js";
import Skeleton from "@mui/material/Skeleton";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";

import { TaipyContext } from "../../context/taipyContext";
import { getArrayValue, getUpdateVar, TaipyActiveProps, TaipyChangeProps } from "./utils";
import {
    createRequestChartUpdateAction,
    createSendActionNameAction,
    createSendUpdateAction,
} from "../../context/taipyReducers";
import { ColumnDesc } from "./tableUtils";
import { useDispatchRequestUpdateOnFirstRender, useDynamicProperty } from "../../utils/hooks";
import { useTheme } from "@mui/system";

const Plot = lazy(() => import("react-plotly.js"));

interface ChartProp extends TaipyActiveProps, TaipyChangeProps {
    title?: string;
    width?: string | number;
    height?: string | number;
    config: string;
    data?: Record<string, TraceValueType>;
    layout?: string;
    plotConfig?: string;
    tp_onRangeChange?: string;
    limitRows?: boolean;
    testId?: string;
    render?: boolean;
    defaultRender?: boolean;
    //[key: `selected_${number}`]: number[];
}

interface ChartConfig {
    columns: Record<string, ColumnDesc>;
    labels: string[];
    modes: string[];
    types: string[];
    traces: string[][];
    xaxis: string[];
    yaxis: string[];
    markers: Partial<PlotMarker>[];
    selectedMarkers: Partial<PlotMarker>[];
    orientations: string[];
    names: string[];
    lines: Partial<ScatterLine>[];
    texts: string[];
    textAnchors: string[];
    options: Record<string, unknown>[];
}

export type TraceValueType = Record<string, (string | number)[]>;

const defaultStyle = { position: "relative", display: "inline-block" };

const indexedData = /^(\d+)\/(.*)/;

const getColNameFromIndexed = (colName: string): string => {
    const reRes = indexedData.exec(colName);
    if (reRes && reRes.length > 2) {
        return reRes[2] || colName;
    }
    return colName;
};

const getValue = <T,>(values: TraceValueType | undefined, arr: T[], idx: number): (string | number)[] => {
    if (values) {
        const confValue = getArrayValue(arr, idx) as unknown as string;
        if (confValue) {
            if (Array.isArray(values)) {
                const reRes = indexedData.exec(confValue);
                if (reRes && reRes.length > 2) {
                    return values[parseInt(reRes[1], 10) || 0][reRes[2] || confValue] || [];
                }
            } else {
                return values[confValue] || [];
            }
        }
    }
    return [];
};

const selectedPropRe = /selected(\d+)/;

const ONE_COLUMN_CHART = ["pie"];
const LAT_LON_CHART = ["scattermapbox", "scattergeo", "densitymapbox"]; // choropleth doesn't rely on latlon

const Chart = (props: ChartProp) => {
    const {
        title = "",
        className,
        width = "100%",
        height,
        updateVarName,
        updateVars,
        id,
        data = {},
        tp_onRangeChange,
        propagate = true,
        limitRows = false,
    } = props;
    const { dispatch } = useContext(TaipyContext);
    const [selected, setSelected] = useState<number[][]>([]);
    const plotRef = useRef<HTMLDivElement>(null);
    const dataKey = useRef("default");
    const theme = useTheme();

    const refresh = data === null;
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const render = useDynamicProperty(props.render, props.defaultRender, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    // get props.selected[i] values
    useEffect(() => {
        setSelected((sel) => {
            Object.keys(props).forEach((key) => {
                const res = selectedPropRe.exec(key);
                if (res && res.length == 2) {
                    const idx = parseInt(res[1], 10);
                    let val = (props as unknown as Record<string, number[]>)[key];
                    if (val !== undefined) {
                        if (typeof val === "string") {
                            try {
                                val = JSON.parse(val) as number[];
                            } catch (e) {
                                // too bad
                                val = [];
                            }
                        }
                        if (!Array.isArray(val)) {
                            val = [];
                        }
                        if (
                            idx >= sel.length ||
                            val.length !== sel[idx].length ||
                            val.some((v, i) => sel[idx][i] != v)
                        ) {
                            sel = sel.concat();
                            sel[idx] = val;
                        }
                    }
                }
            });
            return sel;
        });
    }, [props]);

    const config = useMemo(() => {
        if (props.config) {
            try {
                return JSON.parse(props.config) as ChartConfig;
            } catch (e) {
                console.info(`Error while parsing Chart.config\n${(e as Error).message || e}`);
            }
        }
        return {
            columns: {} as Record<string, ColumnDesc>,
            labels: [],
            modes: [],
            types: [],
            traces: [],
            xaxis: [],
            yaxis: [],
            markers: [],
            selectedMarkers: [],
            orientations: [],
            names: [],
            lines: [],
            texts: [],
            textAnchors: [],
            options: [],
        } as ChartConfig;
    }, [props.config]);

    useEffect(() => {
        if (refresh || !data[dataKey.current]) {
            const backCols = Object.keys(config.columns).map((col) => config.columns[col].dfid);
            dataKey.current = backCols.join("-");
            dispatch(
                createRequestChartUpdateAction(
                    updateVarName,
                    id,
                    dataKey.current,
                    backCols,
                    limitRows ? plotRef.current?.clientWidth : undefined
                )
            );
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [refresh, dispatch, config.columns, updateVarName, id, limitRows]);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, updateVars);

    const layout = useMemo(() => {
        let playout = {} as Layout;
        if (props.layout) {
            try {
                playout = JSON.parse(props.layout);
            } catch (e) {
                console.info(`Error while parsing Chart.layout\n${(e as Error).message || e}`);
            }
        }
        if (playout.mapbox && !playout.mapbox.style) {
            playout.mapbox.style = theme.palette.mode;
        }
        return {
            ...playout,
            title: title || playout.title,
            xaxis: {
                title:
                    config.traces.length && config.traces[0].length && config.traces[0][0]
                        ? getColNameFromIndexed(config.columns[config.traces[0][0]].dfid)
                        : undefined,
                ...playout.xaxis,
            },
            yaxis: {
                title:
                    config.traces.length == 1 && config.traces[0].length > 1 && config.columns[config.traces[0][1]]
                        ? getColNameFromIndexed(config.columns[config.traces[0][1]].dfid)
                        : undefined,
                ...playout.yaxis,
            },
            clickmode: "event+select",
        } as Layout;
    }, [theme.palette.mode, title, config.columns, config.traces, props.layout]);

    const style = useMemo(
        () =>
            height === undefined
                ? ({ ...defaultStyle, width: width } as CSSProperties)
                : ({ ...defaultStyle, width: width, height: height } as CSSProperties),
        [width, height]
    );
    const skelStyle = useMemo(() => ({ ...style, minHeight: "7em" }), [style]);

    const dataPl = useMemo(() => {
        const datum = data && data[dataKey.current];
        return config.traces.map((trace, idx) => {
            const ret = {
                ...getArrayValue(config.options, idx, {}),
                type: config.types[idx],
                mode: config.modes[idx],
                name:
                    getArrayValue(config.names, idx) ||
                    (config.columns[trace[1]] ? getColNameFromIndexed(config.columns[trace[1]].dfid) : undefined),
            } as Record<string, unknown>;
            if (ONE_COLUMN_CHART.includes(config.types[idx])) {
                ret.values = getValue(datum, trace, 0);
                const lbl = getValue(datum, config.labels, idx);
                if (lbl.length) {
                    ret.labels = lbl;
                }
            } else {
                ret.marker = getArrayValue(config.markers, idx, {});
                if ((ret.marker as PlotMarker).opacity !== undefined && ret.type === "bar") {
                    ret.opacity = (ret.marker as PlotMarker).opacity;
                }
                const xs = getValue(datum, trace, 0);
                const ys = getValue(datum, trace, 1);
                if (LAT_LON_CHART.includes(ret.type as string)) {
                    ret.lon = xs;
                    ret.lat = ys;
                } else {
                    if (ys.length) {
                        ret.x = xs;
                        ret.y = ys;
                    } else {
                        ret.x = Array.from(Array(xs.length).keys());
                        ret.y = xs;
                    }
                }
                ret.z = getValue(datum, trace, 2);
                ret.text = getValue(datum, config.texts, idx);
                ret.xaxis = config.xaxis[idx];
                ret.yaxis = config.yaxis[idx];
                ret.hovertext = getValue(datum, config.labels, idx);
                ret.selectedpoints = getArrayValue(selected, idx, []);
                ret.orientation = getArrayValue(config.orientations, idx);
                ret.line = getArrayValue(config.lines, idx);
                ret.textposition = getArrayValue(config.textAnchors, idx);
            }
            const selectedMarker = getArrayValue(config.selectedMarkers, idx);
            if (selectedMarker) {
                ret.selected = { marker: selectedMarker };
            }
            return ret as Data;
        });
    }, [data, config, selected]);

    const plotConfig = useMemo(() => {
        let plconf = {};
        if (props.plotConfig) {
            try {
                plconf = JSON.parse(props.plotConfig);
            } catch (e) {
                console.info(`Error while parsing Chart.plot_config\n${(e as Error).message || e}`);
            }
            if (typeof plconf !== 'object' || plconf === null || Array.isArray(plconf)) {
                console.info("Error Chart.plot_config is not a dictionnary");
                plconf = {}
            }
        }
        if (active) {
            return plconf;
        } else {
            return { ...plconf, staticPlot: true };
        }
    }, [active, props.plotConfig]);

    const onRelayout = useCallback(
        (eventData: PlotRelayoutEvent) =>
            tp_onRangeChange && dispatch(createSendActionNameAction(id, { action: tp_onRangeChange, ...eventData })),
        [dispatch, tp_onRangeChange, id]
    );

    const onAfterPlot = useCallback(() => {
        // Manage loading Animation ... One day
    }, []);

    const getRealIndex = useCallback(
        (index: number) => (data[dataKey.current].tp_index ? (data[dataKey.current].tp_index[index] as number) : index),
        [data]
    );

    const onSelect = useCallback(
        (evt?: PlotMouseEvent | PlotSelectionEvent) => {
            if ((evt as unknown as Record<string, unknown>).event === undefined) {
                return;
            }
            const points = evt?.points || [];
            if (points.length && updateVars) {
                const traces = points.reduce((tr, pt) => {
                    tr[pt.curveNumber] = tr[pt.curveNumber] || [];
                    tr[pt.curveNumber].push(getRealIndex(pt.pointIndex));
                    return tr;
                }, [] as number[][]);
                traces.forEach((tr, idx) => {
                    const upvar = getUpdateVar(updateVars, `selected${idx}`);
                    if (upvar && tr && tr.length) {
                        dispatch(createSendUpdateAction(upvar, tr, props.tp_onChange, propagate));
                    }
                });
            }
        },
        [getRealIndex, dispatch, updateVars, propagate, props.tp_onChange]
    );

    return render ? (
        <Box id={id} key="div" data-testid={props.testId} className={className} ref={plotRef}>
            <Tooltip title={hover || ""}>
                <Suspense fallback={<Skeleton key="skeleton" sx={skelStyle} />}>
                    <Plot
                        data={dataPl}
                        layout={layout}
                        style={style}
                        onRelayout={onRelayout}
                        onAfterPlot={onAfterPlot}
                        onSelected={onSelect}
                        onDeselect={onSelect}
                        onClick={onSelect}
                        config={plotConfig}
                    />
                </Suspense>
            </Tooltip>
        </Box>
    ) : null;
};

export default Chart;
