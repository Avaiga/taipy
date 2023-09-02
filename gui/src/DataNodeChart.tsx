/*
 * Copyright 2023 Avaiga Private Limited
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

import React, { useEffect, useState, useCallback, useMemo } from "react";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import InputLabel from "@mui/material/InputLabel";
import OutlinedInput from "@mui/material/OutlinedInput";
import ListItemText from "@mui/material/ListItemText";
import MenuItem from "@mui/material/MenuItem";
import Select, { SelectChangeEvent } from "@mui/material/Select";

import { Chart, ColumnDesc, TraceValueType } from "taipy-gui";

interface DataNodeChartProps {
    configId?: string;
    tabularData?: Record<string, TraceValueType>;
    columns?: Record<string, ColumnDesc>;
    defaultConfig?: string;
    updateVarName?: string;
    uniqid: string;
}

const chartTypes = {
    Cartesian: "scatter",
    Pie: "pie",
};

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
            width: 250,
        },
    },
};
const selectSx = { m: 1, width: 300 };

interface ChartConfig {
    traces?: Array<[string, string]>;
    types?: string[];
    columns?: Record<string, ColumnDesc>;
}

interface ColSelectProps {
    labelId: string;
    label: string;
    trace: number;
    axis: number;
    traceConf: Array<[string, string]>;
    setColConf: (trace: number, axis: number, col: string) => void;
    columns: string[];
}

const ColSelect = (props: ColSelectProps) => {
    const { labelId, trace, axis, columns, label, setColConf, traceConf } = props;

    const [col, setCol] = useState("");

    const onColChange = useCallback(
        (e: SelectChangeEvent<string>) => {
            setCol(e.target.value);
            setColConf(trace, axis, e.target.value);
        },
        [trace, axis, setColConf]
    );

    useEffect(() => setCol(getTraceCol(traceConf, trace, axis)), [traceConf, trace, axis]);

    return (
        <Select
            labelId={labelId}
            value={col}
            onChange={onColChange}
            input={<OutlinedInput label={label} />}
            MenuProps={MenuProps}
        >
            {columns.map((c) => (
                <MenuItem key={c} value={c}>
                    <ListItemText primary={c} />
                </MenuItem>
            ))}
        </Select>
    );
};

const getTraceCol = (traceConf: Array<[string, string]>, trace: number, axis: number) => {
    return trace < traceConf.length ? traceConf[trace][axis] : "";
};

const DataNodeChart = (props: DataNodeChartProps) => {
    const { defaultConfig = "", uniqid } = props;

    const baseConfig = useMemo(() => {
        try {
            return JSON.parse(defaultConfig) as ChartConfig;
        } catch {
            // Do nothing
        }
        return undefined;
    }, [defaultConfig]);

    const [config, setConfig] = useState<ChartConfig | undefined>(undefined);
    useEffect(() => baseConfig && setConfig(baseConfig), [baseConfig]);

    const columns = useMemo(() => Object.values(props.columns || {}).map((c) => c.dfid), [props.columns]);

    // tabular selected columns
    const [chartType, setChartType] = useState("scatter");
    const onTypeChange = useCallback((e: SelectChangeEvent<typeof chartType>) => {
        setChartType(e.target.value);
        e.target.value && setConfig((cfg) => (cfg ? { ...cfg, types: [e.target.value] } : cfg));
    }, []);

    const [traceConf, setTraceConf] = useState<Array<[string, string]>>([]);

    const setColConf = useCallback((trace: number, axis: number, col: string) => {
        setTraceConf((tc) => {
            const ntc = tc.map((axises, idx) =>
                idx == trace ? (axises.map((a, j) => (j == axis ? col : a)) as [string, string]) : axises
            );
            setConfig((cfg) => (cfg ? { ...cfg, traces: ntc } : cfg));
            return ntc;
        });
    }, []);

    useEffect(() => {
        if (baseConfig && baseConfig.traces && baseConfig.traces.length) {
            setTraceConf(baseConfig.traces);
        } else {
            setTraceConf(columns && columns.length > 0 ? [[columns[0], columns[columns.length > 1 ? 1 : 0]]] : []);
        }
    }, [columns, baseConfig]);

    return (
        <>
            <FormControl sx={selectSx}>
                <InputLabel id={uniqid + "-chart-config"}>Category</InputLabel>
                <Select
                    labelId={uniqid + "-chart-config"}
                    value={chartType}
                    onChange={onTypeChange}
                    input={<OutlinedInput label="Category" />}
                    MenuProps={MenuProps}
                >
                    {Object.entries(chartTypes).map(([k, v]) => (
                        <MenuItem key={v} value={v}>
                            <ListItemText primary={k} />
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
            <Grid container>
                <Grid item xs={3}>
                    Trace 1
                </Grid>
                <Grid item xs={4}>
                    <FormControl sx={selectSx}>
                        <InputLabel id={uniqid + "-trace1-x"}>X-axis</InputLabel>
                        <ColSelect
                            trace={0}
                            axis={0}
                            traceConf={traceConf}
                            label="X-axis"
                            labelId={uniqid + "-trace1-x"}
                            columns={columns}
                            setColConf={setColConf}
                        />
                    </FormControl>
                </Grid>
                <Grid item xs={4}>
                    <FormControl sx={selectSx}>
                        <InputLabel id={uniqid + "-trace1-y"}>Y-axis</InputLabel>
                        <ColSelect
                            trace={0}
                            axis={1}
                            traceConf={traceConf}
                            label="Y-axis"
                            labelId={uniqid + "-trace1-y"}
                            columns={columns}
                            setColConf={setColConf}
                        />
                    </FormControl>
                </Grid>
            </Grid>
            <Chart
                defaultConfig={config ? JSON.stringify(config) : defaultConfig}
                updateVarName={props.updateVarName}
                data={props.tabularData}
            />
        </>
    );
};

export default DataNodeChart;
