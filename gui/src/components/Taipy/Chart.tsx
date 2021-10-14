import React, { CSSProperties, useContext, useEffect, useMemo } from "react";
import Plot from "react-plotly.js";
import { Data, Layout, PlotMarker } from "plotly.js";

import { TaipyContext } from "../../context/taipyContext";
import { createRequestChartUpdateAction } from "../../context/taipyReducers";
import { TaipyBaseProps } from "./utils";
import { getsortByIndex, ColumnDesc } from "./tableUtils";

interface ChartProp extends TaipyBaseProps {
    title: string;
    width: string | number;
    height: string | number;
    type: string;
    mode: string;
    marker: Partial<PlotMarker>;
    value: TraceValueType;
    refresh: boolean;
    columns: string;
    label: string;
}

type TraceValueType = Record<string, (string | number)[]>;

const defaultStyle = { position: "relative", display: "inline-block" };

const Chart = (props: ChartProp) => {
    const {
        title = "Chart",
        className,
        width = "100%",
        height = "100%",
        type = "scatter",
        mode = "lines+markers",
        marker = {},
        refresh = false,
        tp_varname,
        id,
        value,
    } = props;
    const { dispatch } = useContext(TaipyContext);

    const [colsOrder, columns, label] = useMemo(() => {
        if (props.columns) {
            const cols = (typeof props.columns === "string" ? JSON.parse(props.columns) : props.columns) as Record<
                string,
                ColumnDesc
            >;
            const lib = props.label && cols[props.label] && cols[props.label].dfid;
            return [Object.keys(cols).sort(getsortByIndex(cols)), cols, lib || ""];
        }
        return [[], {} as Record<string, ColumnDesc>, ""];
    }, [props.columns, props.label]);

    /* eslint react-hooks/exhaustive-deps: "off", curly: "error" */
    useEffect(() => {
        if (!props.value || !!refresh) {
            const cols = colsOrder.map((col) => columns[col].dfid);
            dispatch(createRequestChartUpdateAction(tp_varname, id, cols));
        }
    }, [refresh, colsOrder, columns, tp_varname, id, dispatch]);

    const layout = useMemo(
        () =>
            ({
                title: title,
                xaxis: { title: columns[colsOrder[0]].dfid },
                yaxis: { title: columns[colsOrder[1]].dfid },
            } as Layout),
        [title, columns]
    );

    const style = useMemo(
        () => ({ ...defaultStyle, width: width, height: height } as CSSProperties),
        [defaultStyle, width, height]
    );

    const data = useMemo(
        () => [
            {
                type: type,
                mode: mode,
                marker: marker,
                x: value ? value[colsOrder[0]] : [],
                y: value ? value[colsOrder[1]] : [],
                hovertext: value && label ? value[label] : [],
            } as Data,
        ],
        [value, type, mode, marker, colsOrder]
    );

    return <Plot data={data} layout={layout} className={className} style={style} />;
};

export default Chart;
