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

import React, { ChangeEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import CheckIcon from "@mui/icons-material/Check";
import DeleteIcon from "@mui/icons-material/Delete";
import SortByAlpha from "@mui/icons-material/SortByAlpha";
import Badge from "@mui/material/Badge";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid2";
import IconButton from "@mui/material/IconButton";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import OutlinedInput from "@mui/material/OutlinedInput";
import Popover, { PopoverOrigin } from "@mui/material/Popover";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Switch from "@mui/material/Switch";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

import { ColumnDesc, getsortByIndex, iconInRowSx } from "./tableUtils";
import { getSuffixedClassNames } from "./utils";

export interface SortDesc {
    col: string;
    order: boolean;
}

interface TableSortProps {
    columns: Record<string, ColumnDesc>;
    colsOrder?: Array<string>;
    onValidate: (data: Array<SortDesc>) => void;
    appliedSorts?: Array<SortDesc>;
    className?: string;
}

interface SortRowProps {
    idx: number;
    sort?: SortDesc;
    columns: Record<string, ColumnDesc>;
    colsOrder: Array<string>;
    setSort: (idx: number, fd: SortDesc, remove?: boolean) => void;
    appliedSorts?: Array<SortDesc>;
}

const anchorOrigin = {
    vertical: "bottom",
    horizontal: "right",
} as PopoverOrigin;

const gridSx = { p: "0.5em", minWidth: "36rem" };
const badgeSx = {
    "& .MuiBadge-badge": {
        height: "10px",
        minWidth: "10px",
        width: "10px",
        borderRadius: "5px",
    },
};
const orderCaptionSx = { ml: 1 };

const getSortDesc = (columns: Record<string, ColumnDesc>, colId?: string, asc?: boolean) =>
    colId && asc !== undefined
        ? ({
              col: columns[colId].dfid,
              order: !!asc,
          } as SortDesc)
        : undefined;

const SortRow = (props: SortRowProps) => {
    const { idx, setSort, columns, colsOrder, sort, appliedSorts } = props;

    const [colId, setColId] = useState("");
    const [order, setOrder] = useState(true); // true => asc
    const [enableCheck, setEnableCheck] = useState(false);
    const [enableDel, setEnableDel] = useState(false);

    const cols = useMemo(() => {
        if (!Array.isArray(appliedSorts) || appliedSorts.length == 0) {
            return colsOrder;
        }
        return colsOrder.filter((col) => col == sort?.col || !appliedSorts.some((fd) => col === fd.col));
    }, [colsOrder, appliedSorts, sort?.col]);

    const onColSelect = useCallback(
        (e: SelectChangeEvent<string>) => {
            setColId(e.target.value);
            setEnableCheck(!!getSortDesc(columns, e.target.value, order));
        },
        [columns, order]
    );
    const onOrderSwitch = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            setOrder(e.target.checked);
            setEnableCheck(!!getSortDesc(columns, colId, e.target.checked));
        },
        [columns, colId]
    );

    const onDeleteClick = useCallback(() => setSort(idx, undefined as unknown as SortDesc, true), [idx, setSort]);
    const onCheckClick = useCallback(() => {
        const fd = getSortDesc(columns, colId, order);
        fd && setSort(idx, fd);
    }, [idx, setSort, columns, colId, order]);

    useEffect(() => {
        if (sort && idx > -1) {
            const col = Object.keys(columns).find((col) => columns[col].dfid === sort.col) || "";
            setColId(col);
            setOrder(sort.order);
            setEnableCheck(false);
            setEnableDel(!!getSortDesc(columns, col, sort.order));
        } else {
            setColId("");
            setOrder(true);
            setEnableCheck(false);
            setEnableDel(false);
        }
    }, [columns, sort, idx]);

    return cols.length ? (
        <Grid container size={12} alignItems="center">
            <Grid size={6}>
                <FormControl margin="dense">
                    <InputLabel>Column</InputLabel>
                    <Select value={colId || ""} onChange={onColSelect} input={<OutlinedInput label="Column" />}>
                        {cols.map((col) => (
                            <MenuItem key={col} value={col}>
                                {columns[col].title || columns[col].dfid}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Grid>
            <Grid size={4}>
                <Switch checked={order} onChange={onOrderSwitch} />
                <Typography variant="caption" color="text.secondary" sx={orderCaptionSx}>
                    {order ? "asc" : "desc"}
                </Typography>
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
    ) : null;
};

const TableSort = (props: TableSortProps) => {
    const { onValidate, appliedSorts, columns, className = "" } = props;

    const [showSort, setShowSort] = useState(false);
    const sortRef = useRef<HTMLButtonElement | null>(null);
    const [sorts, setSorts] = useState<Array<SortDesc>>([]);

    const colsOrder = useMemo(() => {
        if (props.colsOrder) {
            return props.colsOrder;
        }
        return Object.keys(columns).sort(getsortByIndex(columns));
    }, [props.colsOrder, columns]);

    const onShowSortClick = useCallback(() => setShowSort((f) => !f), []);

    const updateSort = useCallback(
        (idx: number, nsd: SortDesc, remove?: boolean) => {
            setSorts((sds) => {
                let newSds;
                if (idx > -1) {
                    if (remove) {
                        sds.splice(idx, 1);
                        newSds = [...sds];
                    } else {
                        newSds = sds.map((fd, index) => (index == idx ? nsd : fd));
                    }
                } else if (remove) {
                    newSds = sds;
                } else {
                    newSds = [...sds, nsd];
                }
                onValidate([...newSds]);
                return newSds;
            });
        },
        [onValidate]
    );

    useEffect(() => {
        columns &&
            appliedSorts &&
            setSorts(appliedSorts.filter((fd) => Object.values(columns).some((cd) => cd.dfid === fd.col)));
    }, [columns, appliedSorts]);

    return (
        <>
            <Tooltip title={`${sorts.length} sort${sorts.length > 1 ? "s" : ""} applied`}>
                <IconButton
                    onClick={onShowSortClick}
                    size="small"
                    ref={sortRef}
                    sx={iconInRowSx}
                    className={getSuffixedClassNames(className, "-sort-icon")}
                >
                    <Badge badgeContent={sorts.length} color="primary" sx={badgeSx}>
                        <SortByAlpha fontSize="inherit" />
                    </Badge>
                </IconButton>
            </Tooltip>
            <Popover
                anchorEl={sortRef.current}
                anchorOrigin={anchorOrigin}
                open={showSort}
                onClose={onShowSortClick}
                className={getSuffixedClassNames(className, "-filter")}
            >
                <Grid container sx={gridSx} gap={0.5}>
                    {sorts.map((sd, idx) => (
                        <SortRow
                            key={"fd" + idx}
                            idx={idx}
                            sort={sd}
                            columns={columns}
                            colsOrder={colsOrder}
                            setSort={updateSort}
                            appliedSorts={sorts}
                        />
                    ))}
                    <SortRow
                        idx={-(sorts.length + 1)}
                        columns={columns}
                        colsOrder={colsOrder}
                        setSort={updateSort}
                        appliedSorts={sorts}
                    />
                </Grid>
            </Popover>
        </>
    );
};

export default TableSort;
