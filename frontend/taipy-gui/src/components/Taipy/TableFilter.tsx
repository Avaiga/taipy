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

import React, { ChangeEvent, SyntheticEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import Autocomplete from "@mui/material/Autocomplete";
import CheckIcon from "@mui/icons-material/Check";
import DeleteIcon from "@mui/icons-material/Delete";
import FilterListIcon from "@mui/icons-material/FilterList";
import Badge from "@mui/material/Badge";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid2";
import IconButton from "@mui/material/IconButton";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import OutlinedInput from "@mui/material/OutlinedInput";
import Popover, { PopoverOrigin } from "@mui/material/Popover";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import { DateField, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFnsV3";

import { ColumnDesc, defaultDateFormat, getSortByIndex, iconInRowSx } from "./tableUtils";
import { getDateTime, getTypeFromDf } from "../../utils";
import { getSuffixedClassNames } from "./utils";

export interface FilterDesc {
    col: string;
    action: string;
    value: string | number | boolean | Date;
    type: string;
}

interface TableFilterProps {
    columns: Record<string, ColumnDesc>;
    colsOrder?: Array<string>;
    onValidate: (data: Array<FilterDesc>) => void;
    appliedFilters?: Array<FilterDesc>;
    className?: string;
    filteredCount: number;
}

interface FilterRowProps {
    idx: number;
    filter?: FilterDesc;
    columns: Record<string, ColumnDesc>;
    colsOrder: Array<string>;
    setFilter: (idx: number, fd: FilterDesc, remove?: boolean) => void;
}

const anchorOrigin = {
    vertical: "bottom",
    horizontal: "right",
} as PopoverOrigin;

const actionsByType = {
    string: { "==": "equals", contains: "contains", "!=": "not equals" },
    number: {
        "<": "less",
        "<=": "less equals",
        "==": "equals",
        "!=": "not equals",
        ">=": "greater equals",
        ">": "greater",
    },
    boolean: { "==": "equals", "!=": "not equals" },
    date: {
        "<": "before",
        "<=": "before equal",
        "==": "equals",
        "!=": "not equals",
        ">=": "after equal",
        ">": "after",
    },
} as Record<string, Record<string, string>>;

const gridSx = { p: "0.5em", minWidth: "36rem" };
const autocompleteSx = { "& .MuiInputBase-root": { padding: "0" } };
const badgeSx = {
    "& .MuiBadge-badge": {
        height: "10px",
        minWidth: "10px",
        width: "10px",
        borderRadius: "5px",
    },
};

const getActionsByType = (colType?: string) =>
    (colType && colType in actionsByType && actionsByType[colType]) ||
    (colType === "any" ? { ...actionsByType.string, ...actionsByType.number } : actionsByType.string);

const getFilterDesc = (columns: Record<string, ColumnDesc>, colId?: string, act?: string, val?: string) => {
    if (colId && act && val !== undefined) {
        const colType = getTypeFromDf(columns[colId].type);
        if (val === "" && (colType === "date" || colType === "number" || colType === "boolean")) {
            return;
        }
        try {
            return {
                col: columns[colId].dfid,
                action: act,
                value:
                    typeof val === "string"
                        ? colType === "number"
                            ? parseFloat(val)
                            : colType === "boolean"
                            ? val === "1"
                            : colType === "date"
                            ? getDateTime(val)
                            : val
                        : val,
                type: colType,
            } as FilterDesc;
        } catch (e) {
            console.info("could not parse value ", val, e);
        }
    }
};

const FilterRow = (props: FilterRowProps) => {
    const { idx, setFilter, columns, colsOrder, filter } = props;

    const [colId, setColId] = useState<string>("");
    const [action, setAction] = useState<string>("");
    const [val, setVal] = useState<string>("");
    const [enableCheck, setEnableCheck] = useState(false);
    const [enableDel, setEnableDel] = useState(false);

    const onColSelect = useCallback(
        (e: SelectChangeEvent<string>) => {
            setColId(e.target.value);
            setEnableCheck(!!getFilterDesc(columns, e.target.value, action, val));
        },
        [columns, action, val]
    );
    const onActSelect = useCallback(
        (e: SelectChangeEvent<string>) => {
            setAction(e.target.value);
            setEnableCheck(!!getFilterDesc(columns, colId, e.target.value, val));
        },
        [columns, colId, val]
    );
    const onValueChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            setVal(e.target.value);
            setEnableCheck(!!getFilterDesc(columns, colId, action, e.target.value));
        },
        [columns, colId, action]
    );
    const onValueAutoComp = useCallback(
        (e: SyntheticEvent, value: string | null) => {
            setVal(value || "");
            setEnableCheck(!!getFilterDesc(columns, colId, action, value || ""));
        },
        [columns, colId, action]
    );
    const onValueSelect = useCallback(
        (e: SelectChangeEvent<string>) => {
            setVal(e.target.value);
            setEnableCheck(!!getFilterDesc(columns, colId, action, e.target.value));
        },
        [columns, colId, action]
    );
    const onDateChange = useCallback(
        (v: Date | null) => {
            const dv = (!(v instanceof Date) || isNaN(v.valueOf())) ?  "": v.toISOString();
            setVal(dv);
            setEnableCheck(!!getFilterDesc(columns, colId, action, dv));
        },
        [columns, colId, action]
    );

    const onDeleteClick = useCallback(() => setFilter(idx, undefined as unknown as FilterDesc, true), [idx, setFilter]);
    const onCheckClick = useCallback(() => {
        const fd = getFilterDesc(columns, colId, action, val);
        fd && setFilter(idx, fd);
    }, [idx, setFilter, columns, colId, action, val]);

    useEffect(() => {
        if (filter && idx > -1) {
            const col = Object.keys(columns).find((col) => columns[col].dfid === filter.col) || "";
            setColId(col);
            setAction(filter.action);
            setVal(filter.value as string);
            setEnableCheck(false);
            setEnableDel(!!getFilterDesc(columns, col, filter.action, filter.value as string));
        } else {
            setColId("");
            setAction("");
            setVal("");
            setEnableCheck(false);
            setEnableDel(false);
        }
    }, [columns, filter, idx]);

    const colType = getTypeFromDf(colId in columns ? columns[colId].type : "");
    const colFormat = colId in columns && columns[colId].format ? columns[colId].format : defaultDateFormat;
    const colLov = colId in columns && columns[colId].lov ? columns[colId].lov : undefined;

    return (
        <Grid container size={12} alignItems="center">
            <Grid size={3.5}>
                <FormControl margin="dense">
                    <InputLabel>Column</InputLabel>
                    <Select value={colId || ""} onChange={onColSelect} input={<OutlinedInput label="Column" />}>
                        {colsOrder.map((col) =>
                            columns[col].filter ? (
                                <MenuItem key={col} value={col}>
                                    {columns[col].title || columns[col].dfid}
                                </MenuItem>
                            ) : null
                        )}
                    </Select>
                </FormControl>
            </Grid>
            <Grid size={3}>
                <FormControl margin="dense">
                    <InputLabel>Action</InputLabel>
                    <Select value={action || ""} onChange={onActSelect} input={<OutlinedInput label="Action" />}>
                        {Object.keys(getActionsByType(colType)).map((a) => (
                            <MenuItem key={a} value={a}>
                                {getActionsByType(colType)[a]}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Grid>
            <Grid size={3.5}>
                {colType == "number" ? (
                    <TextField
                        type="number"
                        value={typeof val === "number" ? val : val || ""}
                        onChange={onValueChange}
                        label="Number"
                        margin="dense"
                    />
                ) : colType == "boolean" ? (
                    <FormControl margin="dense">
                        <InputLabel>Boolean</InputLabel>
                        <Select
                            value={typeof val === "boolean" ? (val ? "1" : "0") : val || ""}
                            onChange={onValueSelect}
                            input={<OutlinedInput label="Boolean" />}
                        >
                            <MenuItem value={"1"}>True</MenuItem>
                            <MenuItem value={"0"}>False</MenuItem>
                        </Select>
                    </FormControl>
                ) : colType == "date" ? (
                    <DateField
                        value={(val && new Date(val)) || null}
                        onChange={onDateChange}
                        format={colFormat}
                        margin="dense"
                    />
                ) : colLov ? (
                    <Autocomplete
                        freeSolo
                        autoSelect
                        disableClearable
                        options={colLov}
                        value={val || ""}
                        onChange={onValueAutoComp}
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                className="MuiAutocomplete-inputRootDense"
                                label={`${val ? "" : "Empty "}String`}
                                margin="dense"
                            />
                        )}
                        sx={autocompleteSx}
                    />
                ) : (
                    <TextField
                        value={val || ""}
                        onChange={onValueChange}
                        label={`${val ? "" : "Empty "}String`}
                        margin="dense"
                    />
                )}
            </Grid>
            <Grid size={1}>
                <Tooltip title="Validate">
                    <span>
                        <IconButton onClick={onCheckClick} disabled={!enableCheck} sx={iconInRowSx}>
                            <CheckIcon />
                        </IconButton>
                    </span>
                </Tooltip>
            </Grid>
            <Grid size={1}>
                <Tooltip title="Delete">
                    <span>
                        <IconButton onClick={onDeleteClick} disabled={!enableDel} sx={iconInRowSx}>
                            <DeleteIcon />
                        </IconButton>
                    </span>
                </Tooltip>
            </Grid>
        </Grid>
    );
};

const TableFilter = (props: TableFilterProps) => {
    const { onValidate, appliedFilters, columns, className = "", filteredCount } = props;

    const [showFilter, setShowFilter] = useState(false);
    const filterRef = useRef<HTMLButtonElement | null>(null);
    const [filters, setFilters] = useState<Array<FilterDesc>>([]);

    const colsOrder = useMemo(() => {
        if (props.colsOrder) {
            return props.colsOrder;
        }
        return Object.keys(columns).sort(getSortByIndex(columns));
    }, [props.colsOrder, columns]);

    const onShowFilterClick = useCallback(() => setShowFilter((f) => !f), []);

    const updateFilter = useCallback(
        (idx: number, nfd: FilterDesc, remove?: boolean) => {
            setFilters((fds) => {
                let newFds;
                if (idx > -1) {
                    if (remove) {
                        fds.splice(idx, 1);
                        newFds = [...fds];
                    } else {
                        newFds = fds.map((fd, index) => (index == idx ? nfd : fd));
                    }
                } else if (remove) {
                    newFds = fds;
                } else {
                    newFds = [...fds, nfd];
                }
                onValidate([...newFds]);
                return newFds;
            });
        },
        [onValidate]
    );

    useEffect(() => {
        columns &&
            appliedFilters &&
            setFilters(appliedFilters.filter((fd) => Object.values(columns).some((cd) => cd.dfid === fd.col)));
    }, [columns, appliedFilters]);

    return (
        <>
            <Tooltip
                title={
                    `${filters.length} filter${filters.length > 1 ? "s" : ""} applied` +
                    (filteredCount ? ` (${filteredCount} non visible rows)` : "")
                }
            >
                <IconButton
                    onClick={onShowFilterClick}
                    size="small"
                    ref={filterRef}
                    sx={iconInRowSx}
                    className={getSuffixedClassNames(className, "-filter-icon")}
                >
                    <Badge badgeContent={filters.length} color="primary" sx={badgeSx}>
                        <FilterListIcon fontSize="inherit" />
                    </Badge>
                </IconButton>
            </Tooltip>
            <Popover
                anchorEl={filterRef.current}
                anchorOrigin={anchorOrigin}
                open={showFilter}
                onClose={onShowFilterClick}
                className={getSuffixedClassNames(className, "-filter")}
            >
                <Grid container sx={gridSx} gap={0.5}>
                    <LocalizationProvider dateAdapter={AdapterDateFns}>
                        {filters.map((fd, idx) => (
                            <FilterRow
                                key={"fd" + idx}
                                idx={idx}
                                filter={fd}
                                columns={columns}
                                colsOrder={colsOrder}
                                setFilter={updateFilter}
                            />
                        ))}
                        <FilterRow
                            idx={-(filters.length + 1)}
                            columns={columns}
                            colsOrder={colsOrder}
                            setFilter={updateFilter}
                        />
                    </LocalizationProvider>
                </Grid>
            </Popover>
        </>
    );
};

export default TableFilter;
