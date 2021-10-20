import React, { CSSProperties, useCallback, useContext, useEffect, useMemo, useState } from "react";
import Plot from "react-plotly.js";
import { Data, Layout, PlotMarker, PlotRelayoutEvent } from "plotly.js";
import Skeleton from "@mui/material/Skeleton";

import { TaipyContext } from "../../context/taipyContext";
import { createRequestChartUpdateAction } from "../../context/taipyReducers";
import { TaipyBaseProps } from "./utils";
import { ColumnDesc } from "./tableUtils";

interface ChartProp extends TaipyBaseProps {
    title: string;
    width: string | number;
    height: string | number;
    types: string;
    modes: string;
    value: TraceValueType;
    refresh: boolean;
    columns: string;
    labels: string;
    colors: string;
    traces: string;
    axis: string;
    layout: string;
}

type TraceValueType = Record<string, (string | number)[]>;

const defaultStyle = { position: "relative", display: "inline-block" };

const Chart = (props: ChartProp) => {
    const {
        title = "Chart",
        className,
        width = "100%",
        height = "100%",
        refresh = false,
        tp_varname,
        id,
        value,
    } = props;
    const { dispatch } = useContext(TaipyContext);
    const [loading, setLoading] = useState(false);

    const { columns, labels, modes, types, markers, traces, axis } = useMemo(() => {
        const ret = {
            columns: {} as Record<string, ColumnDesc>,
            labels: [],
            modes: [],
            types: [],
            markers: [],
            traces: [],
            axis: [],
        } as {
            columns: Record<string, ColumnDesc>;
            labels: string[];
            modes: string[];
            types: string[];
            markers: Partial<PlotMarker>[];
            traces: string[][];
            axis: string[][];
        };
        if (props.columns) {
            ret.columns = JSON.parse(props.columns) as Record<string, ColumnDesc>;
        }
        if (props.labels) {
            ret.labels = JSON.parse(props.labels);
        }
        if (props.modes) {
            ret.modes = JSON.parse(props.modes);
        }
        if (props.types) {
            ret.types = JSON.parse(props.types);
        }
        if (props.colors) {
            ret.markers = JSON.parse(props.colors).map((color: string) =>
                color ? { color: color } : ({} as Partial<PlotMarker>)
            );
        }
        if (props.axis) {
            ret.axis = JSON.parse(props.axis) as string[][];
        }
        if (props.traces) {
            ret.traces = JSON.parse(props.traces);
        }
        return ret;
    }, [props.columns, props.labels, props.types, props.modes, props.colors, props.traces, props.axis]);

    /* eslint react-hooks/exhaustive-deps: "off", curly: "error" */
    useEffect(() => {
        if (!props.value || !!refresh) {
            setLoading(true);
            const back_cols = Object.keys(columns).map((col) => columns[col].dfid);
            dispatch(createRequestChartUpdateAction(tp_varname, id, back_cols));
        }
    }, [refresh, columns, tp_varname, id, dispatch]);

    const layout = useMemo(() => {
        const playout = props.layout ? JSON.parse(props.layout) : {};
        return {
            ...playout,
            title: title,
            xaxis: {
                title: traces.length && traces[0].length && traces[0][0] ? columns[traces[0][0]].dfid : undefined,
            },
            yaxis: {
                title:
                    traces.length == 1 && traces[0].length > 1 && columns[traces[0][1]]
                        ? columns[traces[0][1]].dfid
                        : undefined,
            },
        } as Layout;
    }, [title, columns, traces, props.layout]);

    const style = useMemo(
        () => ({ ...defaultStyle, width: width, height: height } as CSSProperties),
        [defaultStyle, width, height]
    );

    const divStyle = useMemo(() => (loading ? { display: "none" } : {}), [loading]);

    const data = useMemo(
        () =>
            traces.map(
                (trace, idx) =>
                    ({
                        type: types[idx],
                        mode: modes[idx],
                        name: columns[trace[1]] ? columns[trace[1]].dfid : undefined,
                        marker: idx < markers.length ? markers[idx] : {},
                        x: value && trace.length ? value[trace[0]] : [],
                        y: value && trace.length > 1 ? value[trace[1]] : [],
                        z: value && trace.length > 2 ? value[trace[2]] : [],
                        xaxis: axis[idx][0],
                        yaxis: axis[idx][1],
                        hovertext: value && idx < labels.length ? value[labels[idx]] : [],
                    } as Data)
            ),
        [value, traces, types, modes, markers, labels, columns]
    );

    const onRelayout = useCallback(
        (eventData: PlotRelayoutEvent) => console.log("plotly_relayout Event data:", eventData),
        []
    );

    const onAfterPlot = useCallback(() => setLoading(false), []);

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
                />
            </div>
        </>
    );
};

export default Chart;
