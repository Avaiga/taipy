import React, { CSSProperties, useContext, useEffect, useMemo } from "react";
import Plot from "react-plotly.js";
import { Data, Layout, PlotMarker } from "plotly.js";

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

    const { columns, labels, modes, types, markers, traces } = useMemo(() => {
        const ret = {
            columns: {} as Record<string, ColumnDesc>,
            labels: [],
            modes: [],
            types: [],
            markers: [],
            traces: [],
        } as {
            columns: Record<string, ColumnDesc>;
            labels: string[];
            modes: string[];
            types: string[];
            markers: Partial<PlotMarker>[];
            traces: string[][];
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
        if (props.traces) {
            ret.traces = JSON.parse(props.traces);
        }
        return ret;
    }, [props.columns, props.labels, props.types, props.modes, props.colors, props.traces]);

    /* eslint react-hooks/exhaustive-deps: "off", curly: "error" */
    useEffect(() => {
        if (!props.value || !!refresh) {
            const back_cols = Object.keys(columns).map((col) => columns[col].dfid);
            dispatch(createRequestChartUpdateAction(tp_varname, id, back_cols));
        }
    }, [refresh, columns, tp_varname, id, dispatch]);

    const layout = useMemo(
        () =>
            ({
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
            } as Layout),
        [title, columns, traces]
    );

    const style = useMemo(
        () => ({ ...defaultStyle, width: width, height: height } as CSSProperties),
        [defaultStyle, width, height]
    );

    const data = useMemo(
        () =>
            traces.map(
                (trace, idx) =>
                    ({
                        type: types[idx],
                        mode: modes[idx],
                        name: columns[traces[0][1]] ? columns[trace[1]].dfid : undefined,
                        marker: idx < markers.length ? markers[idx] : {},
                        x: value && trace.length ? value[trace[0]] : [],
                        y: value && trace.length > 1 ? value[trace[1]] : [],
                        hovertext: value && idx < labels.length ? value[labels[idx]] : [],
                    } as Data)
            ),
        [value, traces, types, modes, markers, labels, columns]
    );

    return <Plot data={data} layout={layout} className={className} style={style} />;
};

export default Chart;
