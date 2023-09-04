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

import React, { useEffect, useState, useCallback, useMemo, MouseEvent } from "react";

import { DeleteOutline, Add } from "@mui/icons-material";
import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
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

const chartTypes: Record<string, { name: string; [prop: string]: unknown }> = {
    scatter: { name: "Cartesian", addIndex: true, axisNames: [] },
    pie: { name: "Pie", addIndex: false, axisNames: ["values", "labels"] },
};

const getChartTypeConfig = (...types: string[]) => {
    const ret: Record<string, Array<unknown>> = {};
    types.forEach((t, i) => {
        if (t && chartTypes[t]) {
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            const { name, ...cfg } = chartTypes[t];
            Object.entries(cfg).forEach(([k, v]) => {
                ret[k] = ret[k] || [];
                ret[k][i] = v;
            });
        }
    });
    return ret;
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

interface TypeSelectProps {
    labelId: string;
    label: string;
    trace: number;
    setTypeConf: (trace: number, cType: string) => void;
    value: string;
}

const TypeSelect = (props: TypeSelectProps) => {
    const { labelId, trace, label, setTypeConf, value } = props;

    const [cType, setType] = useState("");

    const onTypeChange = useCallback(
        (e: SelectChangeEvent<string>) => {
            setType(e.target.value);
            setTypeConf(trace, e.target.value);
        },
        [trace, setTypeConf]
    );

    useEffect(() => setType(value), [value]);

    return (
        <Select
            labelId={labelId}
            value={cType}
            onChange={onTypeChange}
            input={<OutlinedInput label={label} />}
            MenuProps={MenuProps}
        >
            {Object.entries(chartTypes).map(([k, v]) => (
                <MenuItem key={k} value={k}>
                    <ListItemText primary={v.name} />
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

    const [traceConf, setTraceConf] = useState<Array<[string, string]>>([]);

    const [chartTypes, setChartTypes] = useState(["scatter"]);
    const setTypeChange = useCallback((trace: number, cType: string) => {
        setChartTypes((cts) => {
            const nct = cts.map((ct, i) => (i == trace ? cType : ct));
            setConfig((cfg) => (cfg ? { ...cfg, types: nct, ...getChartTypeConfig(...nct) } : cfg));
            return nct;
        });
    }, []);

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
        if (baseConfig && baseConfig.types && baseConfig.types.length) {
            setChartTypes(baseConfig.types);
        } else {
            setChartTypes(["scatter"]);
        }
    }, [columns, baseConfig]);

    const onAddTrace = useCallback(
        () =>
            setTraceConf((tc) => {
                if (columns && columns.length > 0) {
                    const ntc: Array<[string, string]> = [...tc, [columns[0], columns[columns.length > 1 ? 1 : 0]]];
                    setChartTypes((cts) => {
                        const ncts = [...cts, cts[0]];
                        setConfig((cfg) => (cfg ? { ...cfg, types: ncts, traces: ntc } : cfg));
                        return ncts;
                    });
                    return ntc;
                }
                return tc;
            }),
        [columns]
    );
    const onRemoveTrace = useCallback((e: MouseEvent<HTMLElement>) => {
        const { idx } = e.currentTarget.dataset;
        const i = Number(idx);
        setTraceConf((tc) => {
            if (isNaN(i) || i >= tc.length) {
                return tc;
            }
            const ntc = tc.filter((c, j) => j != i);
            setChartTypes((cts) => {
                const ncts = cts.filter((ct, j) => j != i);
                setConfig((cfg) => (cfg ? { ...cfg, types: ncts, traces: ntc, ...getChartTypeConfig(...ncts) } : cfg));
                return ncts;
            });
            return ntc;
        });
    }, []);

    return (
        <>
            <Grid container>
                {traceConf
                    ? traceConf.map((tc, idx) => {
                          const baseLabelId = `${uniqid}-trace${idx}-"`;
                          return (
                              <>
                                  <Grid item xs={2}>
                                      Trace {idx + 1}
                                  </Grid>
                                  <Grid item xs={3}>
                                      <FormControl sx={selectSx}>
                                          <InputLabel id={baseLabelId + "config"}>Category</InputLabel>
                                          <TypeSelect
                                              trace={idx}
                                              label="Category"
                                              labelId={baseLabelId + "config"}
                                              setTypeConf={setTypeChange}
                                              value={chartTypes[idx]}
                                          />
                                      </FormControl>
                                  </Grid>
                                  <Grid item xs={3}>
                                      <FormControl sx={selectSx}>
                                          <InputLabel id={baseLabelId + "x"}>X-axis</InputLabel>
                                          <ColSelect
                                              trace={idx}
                                              axis={0}
                                              traceConf={traceConf}
                                              label="X-axis"
                                              labelId={baseLabelId + "x"}
                                              columns={columns}
                                              setColConf={setColConf}
                                          />
                                      </FormControl>
                                  </Grid>
                                  <Grid item xs={3}>
                                      <FormControl sx={selectSx}>
                                          <InputLabel id={baseLabelId + "y"}>Y-axis</InputLabel>
                                          <ColSelect
                                              trace={idx}
                                              axis={1}
                                              traceConf={traceConf}
                                              label="Y-axis"
                                              labelId={baseLabelId + "y"}
                                              columns={columns}
                                              setColConf={setColConf}
                                          />
                                      </FormControl>
                                  </Grid>
                                  <Grid item xs={1}>
                                      {traceConf.length > 1 ? (
                                          <IconButton onClick={onRemoveTrace} data-idx={idx}>
                                              <DeleteOutline color="primary" />
                                          </IconButton>
                                      ) : null}
                                  </Grid>
                              </>
                          );
                      })
                    : null}
                <Grid item xs={12}>
                    <Button onClick={onAddTrace}>
                        <Add color="primary" />
                        Add trace
                    </Button>
                </Grid>
            </Grid>
            <Chart
                defaultConfig={config ? JSON.stringify(config) : defaultConfig}
                updateVarName={props.updateVarName}
                data={props.tabularData}
                libClassName="taipy-chart"
            />
        </>
    );
};

export default DataNodeChart;
