import React, { CSSProperties, useCallback, useContext, useEffect, useMemo, useState } from "react";
import Plot from "react-plotly.js";
import { Data, Layout, PlotMarker, PlotRelayoutEvent, PlotMouseEvent, PlotSelectionEvent } from "plotly.js";
import Skeleton from "@mui/material/Skeleton";

import { TaipyContext } from "../../context/taipyContext";
import { getArrayValue, getUpdateVar, getUpdateVars, TaipyBaseProps } from "./utils";
import {
    createRequestChartUpdateAction,
    createRequestUpdateAction,
    createSendActionNameAction,
    createSendUpdateAction,
} from "../../context/taipyReducers";
import { ColumnDesc } from "./tableUtils";

interface ChartProp extends TaipyBaseProps {
    title: string;
    width: string | number;
    height: string | number;
    config: string;
    value: TraceValueType;
    refresh: boolean;
    layout: string;
    rangeChange: string;
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
}

type TraceValueType = Record<string, (string | number)[]>;

const defaultStyle = { position: "relative", display: "inline-block" };

const getValue = <T extends unknown>(values: TraceValueType, arr: T[], idx: number): (string | number)[] => {
    if (values) {
        const confValue = getArrayValue(arr, idx) as string;
        if (confValue) {
            return values[confValue] || [];
        }
    }
    return [];
};

const selectedPropRe = /selected(\d+)/;

const Chart = (props: ChartProp) => {
    const {
        title = "Chart",
        className,
        width = "100%",
        height = "100%",
        refresh = false,
        tp_varname,
        tp_updatevars,
        id,
        value,
        rangeChange,
        propagate,
    } = props;
    const { dispatch } = useContext(TaipyContext);
    const [loading, setLoading] = useState(false);
    const [selected, setSelected] = useState<number[][]>([]);

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
            return JSON.parse(props.config) as ChartConfig;
        } else {
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
            } as ChartConfig;
        }
    }, [props.config]);

    /* eslint react-hooks/exhaustive-deps: "off", curly: "error" */
    useEffect(() => {
        if (!props.value || !!refresh) {
            setLoading(true);
            const back_cols = Object.keys(config.columns).map((col) => config.columns[col].dfid);
            dispatch(createRequestChartUpdateAction(tp_varname, id, back_cols));
        }
    }, [refresh, dispatch, config.columns, tp_varname, id]);

    useEffect(() => {
        const updateVars = getUpdateVars(tp_updatevars);
        updateVars.length && dispatch(createRequestUpdateAction(id, updateVars));
    }, [dispatch, tp_updatevars, id]);

    const layout = useMemo(() => {
        const playout = props.layout ? JSON.parse(props.layout) : {};
        return {
            ...playout,
            title: title,
            xaxis: {
                title:
                    config.traces.length && config.traces[0].length && config.traces[0][0]
                        ? config.columns[config.traces[0][0]].dfid
                        : undefined,
            },
            yaxis: {
                title:
                    config.traces.length == 1 && config.traces[0].length > 1 && config.columns[config.traces[0][1]]
                        ? config.columns[config.traces[0][1]].dfid
                        : undefined,
            },
            clickmode: "event+select",
        } as Layout;
    }, [title, config.columns, config.traces, props.layout]);

    const style = useMemo(
        () => ({ ...defaultStyle, width: width, height: height } as CSSProperties),
        [defaultStyle, width, height]
    );

    const divStyle = useMemo(() => (loading ? { display: "none" } : {}), [loading]);

    const data = useMemo(
        () =>
            config.traces.map((trace, idx) => {
                const ret = {
                    type: config.types[idx],
                    mode: config.modes[idx],
                    name: config.columns[trace[1]] ? config.columns[trace[1]].dfid : undefined,
                    marker: getArrayValue(config.markers, idx, {}),
                    x: getValue(value, trace, 0),
                    y: getValue(value, trace, 1),
                    z: getValue(value, trace, 2),
                    xaxis: config.xaxis[idx],
                    yaxis: config.yaxis[idx],
                    hovertext: getValue(value, config.labels, idx),
                    selectedpoints: getArrayValue(selected, idx, []),
                } as Record<string, unknown>;
                const selectedMarker = getArrayValue(config.selectedMarkers, idx);
                if (selectedMarker) {
                    ret.selected = { marker: selectedMarker };
                }
                return ret as Data;
            }),
        [value, config, selected]
    );

    const onRelayout = useCallback(
        (eventData: PlotRelayoutEvent) =>
            rangeChange && dispatch(createSendActionNameAction(id, { action: rangeChange, ...eventData })),
        [rangeChange]
    );

    const onAfterPlot = useCallback(() => setLoading(false), []);

    const onSelect = useCallback(
        (evt?: PlotMouseEvent | PlotSelectionEvent) => {
            const points = evt?.points || [];
            if (points.length && tp_updatevars) {
                const traces = points.reduce((tr, pt) => {
                    tr[pt.curveNumber] = tr[pt.curveNumber] || [];
                    tr[pt.curveNumber].push(pt.pointIndex);
                    return tr;
                }, [] as number[][]);
                traces.forEach((tr, idx) => {
                    const upvar = getUpdateVar(tp_updatevars, `selected${idx}`);
                    if (upvar && tr && tr.length) {
                        dispatch(createSendUpdateAction(upvar, tr, propagate));
                    }
                });
            }
        },
        [tp_updatevars, propagate]
    );

    return (
        <>
            {loading ? <Skeleton key="skeleton" sx={style} /> : null}
            <div style={divStyle} key="div">
                <Plot
                    data={data}
                    layout={layout}
                    className={className}
                    style={style}
                    onRelayout={onRelayout}
                    onAfterPlot={onAfterPlot}
                    onSelected={onSelect}
                    onDeselect={onSelect}
                    onClick={onSelect}
                />
            </div>
        </>
    );
};

export default Chart;
