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

import React, { useEffect, useState, useCallback, useMemo, MouseEvent, ChangeEvent, MutableRefObject } from "react";

import BarChartOutlined from "@mui/icons-material/BarChartOutlined";
import RefreshOutlined from "@mui/icons-material/RefreshOutlined";
import TableChartOutlined from "@mui/icons-material/TableChartOutlined";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import Grid from "@mui/material/Grid2";
import InputLabel from "@mui/material/InputLabel";
import OutlinedInput from "@mui/material/OutlinedInput";
import ListItemText from "@mui/material/ListItemText";
import MenuItem from "@mui/material/MenuItem";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";

import {
    ColumnDesc,
    Table,
    TraceValueType,
    createSendActionNameAction,
    getUpdateVar,
    useDispatch,
    useModule,
} from "taipy-gui";

import { ChartViewType, MenuProps, TableViewType, selectSx, tabularHeaderSx } from "./utils";

interface DataNodeTableProps {
    active: boolean;
    nodeId?: string;
    configId?: string;
    data?: Record<string, TraceValueType>;
    columns?: Record<string, ColumnDesc>;
    updateVarName?: string;
    uniqId: string;
    onEdit?: string;
    onViewTypeChange: (e: MouseEvent, value?: string) => void;
    onLock?: string;
    editInProgress?: boolean;
    editLock: MutableRefObject<boolean>;
    notEditableReason: string;
    updateDnVars?: string;
}

const pushRightSx = { ml: "auto" };

const DataNodeTable = (props: DataNodeTableProps) => {
    const { uniqId, configId, nodeId, columns = "", onViewTypeChange, notEditableReason, updateDnVars = "" } = props;

    const dispatch = useDispatch();
    const module = useModule();

    // tabular selected columns
    const [selectedCols, setSelectedCols] = useState<string[]>([]);
    const onColsChange = useCallback(
        (e: SelectChangeEvent<typeof selectedCols>) => {
            const sc = typeof e.target.value == "string" ? e.target.value.split(",") : e.target.value;
            localStorage && localStorage.setItem(`${configId}-selected-cols`, JSON.stringify(sc));
            setSelectedCols(sc);
        },
        [configId]
    );
    const resetCols = useCallback(() => {
        localStorage && localStorage.removeItem(`${configId}-selected-cols`);
        columns && setSelectedCols(Object.entries(columns).map((e) => e[1].dfid));
    }, [configId, columns]);

    useEffect(() => {
        if (columns) {
            let tc = Object.entries(columns).map((e) => e[1].dfid);
            const storedSel = localStorage && localStorage.getItem(`${configId}-selected-cols`);
            if (storedSel) {
                try {
                    const storedCols = JSON.parse(storedSel);
                    if (Array.isArray(storedCols)) {
                        tc = tc.filter((c) => storedCols.includes(c));
                    }
                } catch {
                    // do nothing
                }
            }
            setSelectedCols(tc);
        }
    }, [columns, configId]);

    // tabular columns
    const [tabCols, setTabCols] = useState<Record<string, ColumnDesc>>({});
    useEffect(() => {
        if (columns) {
            const res = {} as Record<string, ColumnDesc>;
            const dfIds = {} as Record<string, string>;
            Object.entries(columns).forEach(([k, v]) => (dfIds[v.dfid] = k));
            selectedCols.forEach((c) => dfIds[c] && (res[dfIds[c]] = columns[dfIds[c]]));
            setTabCols(res);
        }
    }, [columns, selectedCols]);

    const [tableEdit, setTableEdit] = useState(false);
    const toggleTableEdit = useCallback(
        () =>
            setTableEdit((e) => {
                props.editLock.current = !e;
                dispatch(
                    createSendActionNameAction("", module, props.onLock, {
                        id: nodeId,
                        lock: !e,
                        error_id: getUpdateVar(updateDnVars, "error_id"),
                    })
                );
                return !e;
            }),
        [nodeId, dispatch, module, props.onLock, props.editLock, updateDnVars]
    );

    const userData = useMemo(() => {
        const ret: Record<string, unknown> = { dn_id: nodeId, comment: "" };
        const idVar = getUpdateVar(updateDnVars, "data_id");
        idVar && (ret.context = { [idVar]: nodeId, data_id: idVar, error_id: getUpdateVar(updateDnVars, "error_id") });
        return ret;
    }, [nodeId, updateDnVars]);
    const [comment, setComment] = useState("");
    const changeComment = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            setComment(e.currentTarget.value);
            userData.comment = e.currentTarget.value;
        },
        [userData]
    );

    return (
        <>
            <Grid container sx={tabularHeaderSx}>
                <Grid>
                    <Box className="taipy-toggle">
                        <ToggleButtonGroup onChange={onViewTypeChange} exclusive value={TableViewType} color="primary">
                            <ToggleButton value={TableViewType}>
                                <TableChartOutlined />
                            </ToggleButton>
                            <ToggleButton value={ChartViewType}>
                                <BarChartOutlined />
                            </ToggleButton>
                        </ToggleButtonGroup>
                    </Box>
                </Grid>
                <Grid>
                    <FormControl sx={selectSx} fullWidth className="taipy-selector">
                        <InputLabel id={uniqId + "-cols-label"}>Columns</InputLabel>
                        <Select
                            labelId={uniqId + "-cols-label"}
                            multiple
                            value={selectedCols}
                            onChange={onColsChange}
                            input={<OutlinedInput label="Columns" fullWidth />}
                            renderValue={(selected) => selected.join(", ")}
                            MenuProps={MenuProps}
                            fullWidth
                        >
                            {Object.values(columns || {}).map((colDesc) => (
                                <MenuItem key={colDesc.dfid} value={colDesc.dfid}>
                                    <Checkbox checked={selectedCols.includes(colDesc.dfid)} />
                                    <ListItemText primary={colDesc.dfid} />
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid>
                    <Button
                        onClick={resetCols}
                        variant="text"
                        color="primary"
                        className="taipy-button"
                        startIcon={<RefreshOutlined />}
                    >
                        Reset View
                    </Button>
                </Grid>
                {tableEdit ? (
                    <Grid sx={pushRightSx}>
                        <TextField value={comment} onChange={changeComment} label="Comment"></TextField>
                    </Grid>
                ) : null}
                <Grid sx={tableEdit ? undefined : pushRightSx}>
                    <FormControlLabel
                        disabled={!props.active || !!notEditableReason || !!props.editInProgress}
                        control={<Switch color="primary" checked={tableEdit} onChange={toggleTableEdit} />}
                        label="Edit data"
                        labelPlacement="start"
                    />
                </Grid>
            </Grid>
            <Table
                active={props.active}
                defaultColumns={JSON.stringify(tabCols)}
                updateVarName={props.updateVarName}
                data={props.data}
                userData={userData}
                onEdit={props.onEdit}
                editable={tableEdit}
                filter={true}
                libClassName="taipy-table"
                pageSize={25}
            />
        </>
    );
};

export default DataNodeTable;
