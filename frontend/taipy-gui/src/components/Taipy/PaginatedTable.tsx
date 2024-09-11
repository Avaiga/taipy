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

import React, {
    useState,
    useEffect,
    useCallback,
    useRef,
    useMemo,
    CSSProperties,
    ChangeEvent,
    MouseEvent,
} from "react";
import Box from "@mui/material/Box";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TablePagination from "@mui/material/TablePagination";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import Paper from "@mui/material/Paper";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import Tooltip from "@mui/material/Tooltip";
import { visuallyHidden } from "@mui/utils";
import IconButton from "@mui/material/IconButton";
import AddIcon from "@mui/icons-material/Add";
import DataSaverOn from "@mui/icons-material/DataSaverOn";
import DataSaverOff from "@mui/icons-material/DataSaverOff";
import Download from "@mui/icons-material/Download";

import { createRequestTableUpdateAction, createSendActionNameAction } from "../../context/taipyReducers";
import {
    addDeleteColumn,
    baseBoxSx,
    defaultColumns,
    EditableCell,
    EDIT_COL,
    getClassName,
    getsortByIndex,
    headBoxSx,
    LINE_STYLE,
    OnCellValidation,
    OnRowDeletion,
    Order,
    PageSizeOptionsType,
    paperSx,
    RowType,
    RowValue,
    tableSx,
    TaipyPaginatedTableProps,
    ColumnDesc,
    iconInRowSx,
    DEFAULT_SIZE,
    OnRowSelection,
    getRowIndex,
    getTooltip,
    OnRowClick,
    DownloadAction,
} from "./tableUtils";
import {
    useClassNames,
    useDispatch,
    useDispatchRequestUpdateOnFirstRender,
    useDynamicJsonProperty,
    useDynamicProperty,
    useFormatConfig,
    useModule,
} from "../../utils/hooks";
import TableFilter, { FilterDesc } from "./TableFilter";
import { getSuffixedClassNames, getUpdateVar } from "./utils";
import { emptyArray } from "../../utils";

const loadingStyle: CSSProperties = { width: "100%", height: "3em", textAlign: "right", verticalAlign: "center" };
const skelSx = { width: "100%", height: "3em" };

const rowsPerPageOptions: PageSizeOptionsType = [10, 50, 100, 500];

const PaginatedTable = (props: TaipyPaginatedTableProps) => {
    const {
        id,
        updateVarName,
        pageSizeOptions,
        allowAllRows = false,
        showAll = false,
        height,
        selected = emptyArray,
        updateVars,
        onEdit = "",
        onDelete = "",
        onAdd = "",
        onAction = "",
        width = "100%",
        size = DEFAULT_SIZE,
        userData,
        downloadable = false,
        compare = false,
        onCompare = "",
    } = props;
    const pageSize = props.pageSize === undefined || props.pageSize < 1 ? 100 : Math.round(props.pageSize);
    const [value, setValue] = useState<Record<string, unknown>>({});
    const [startIndex, setStartIndex] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(pageSize);
    const [order, setOrder] = useState<Order>("asc");
    const [orderBy, setOrderBy] = useState("");
    const [loading, setLoading] = useState(true);
    const [aggregates, setAggregates] = useState<string[]>([]);
    const [appliedFilters, setAppliedFilters] = useState<FilterDesc[]>([]);
    const dispatch = useDispatch();
    const pageKey = useRef("no-page");
    const selectedRowRef = useRef<HTMLTableRowElement | null>(null);
    const formatConfig = useFormatConfig();
    const module = useModule();

    const refresh = props.data && typeof props.data.__taipy_refresh === "boolean";
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const editable = useDynamicProperty(props.editable, props.defaultEditable, false);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const baseColumns = useDynamicJsonProperty(props.columns, props.defaultColumns, defaultColumns);

    const [colsOrder, columns, styles, tooltips, handleNan, filter] = useMemo(() => {
        let hNan = !!props.nanValue;
        if (baseColumns) {
            try {
                let filter = false;
                const newCols: Record<string, ColumnDesc> = {};
                Object.entries(baseColumns).forEach(([cId, cDesc]) => {
                    const nDesc = (newCols[cId] = { ...cDesc });
                    if (typeof nDesc.filter != "boolean") {
                        nDesc.filter = !!props.filter;
                    }
                    filter = filter || nDesc.filter;
                    if (typeof nDesc.notEditable != "boolean") {
                        nDesc.notEditable = !editable;
                    }
                    if (nDesc.tooltip === undefined) {
                        nDesc.tooltip = props.tooltip;
                    }
                });
                addDeleteColumn(
                    (active && editable && (onAdd || onDelete) ? 1 : 0) +
                        (active && filter ? 1 : 0) +
                        (active && downloadable ? 1 : 0),
                    newCols
                );
                const colsOrder = Object.keys(newCols).sort(getsortByIndex(newCols));
                const styTt = colsOrder.reduce<Record<string, Record<string, string>>>((pv, col) => {
                    if (newCols[col].style) {
                        pv.styles = pv.styles || {};
                        pv.styles[newCols[col].dfid] = newCols[col].style as string;
                    }
                    hNan = hNan || !!newCols[col].nanValue;
                    if (newCols[col].tooltip) {
                        pv.tooltips = pv.tooltips || {};
                        pv.tooltips[newCols[col].dfid] = newCols[col].tooltip as string;
                    }
                    return pv;
                }, {});
                if (props.lineStyle) {
                    styTt.styles = styTt.styles || {};
                    styTt.styles[LINE_STYLE] = props.lineStyle;
                }
                return [colsOrder, newCols, styTt.styles, styTt.tooltips, hNan, filter];
            } catch (e) {
                console.info("PaginatedTable.columns: ", (e as Error).message || e);
            }
        }
        return [
            [] as string[],
            {} as Record<string, ColumnDesc>,
            {} as Record<string, string>,
            {} as Record<string, string>,
            hNan,
            false,
        ];
    }, [
        active,
        editable,
        onAdd,
        onDelete,
        baseColumns,
        props.lineStyle,
        props.tooltip,
        props.nanValue,
        props.filter,
        downloadable,
    ]);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, updateVars);

    /*
    TODO: If the 'selected' value is a negative number, it will lead to unexpected pagination behavior.
    For instance, if 'selected' is -1, the pagination will display from -99 to 0 and no data will be selected.
    Need to fix this issue.
    */
    useEffect(() => {
        if (selected.length) {
            if (selected[0] < startIndex || selected[0] > startIndex + rowsPerPage) {
                setLoading(true);
                setStartIndex(rowsPerPage * Math.floor(selected[0] / rowsPerPage));
            }
        }
    }, [selected, startIndex, rowsPerPage]);

    useEffect(() => {
        if (!refresh && props.data && props.data[pageKey.current] !== undefined) {
            setValue(props.data[pageKey.current]);
            setLoading(false);
        }
    }, [refresh, props.data]);

    useEffect(() => {
        const endIndex = showAll ? -1 : startIndex + rowsPerPage - 1;
        const agg = aggregates.length
            ? colsOrder.reduce((pv, col, idx) => {
                  if (aggregates.includes(columns[col].dfid)) {
                      return pv + "-" + idx;
                  }
                  return pv;
              }, "-agg")
            : "";
        const cols = colsOrder.map((col) => columns[col].dfid).filter((c) => c != EDIT_COL);
        const afs = appliedFilters.filter((fd) => Object.values(columns).some((cd) => cd.dfid === fd.col));
        pageKey.current = `${startIndex}-${endIndex}-${cols.join()}-${orderBy}-${order}${agg}${afs.map(
            (af) => `${af.col}${af.action}${af.value}`
        )}`;
        if (refresh || !props.data || props.data[pageKey.current] === undefined) {
            setLoading(true);
            const applies = aggregates.length
                ? colsOrder.reduce<Record<string, unknown>>((pv, col) => {
                      if (columns[col].apply) {
                          pv[columns[col].dfid] = columns[col].apply;
                      }
                      return pv;
                  }, {})
                : undefined;
            dispatch(
                createRequestTableUpdateAction(
                    updateVarName,
                    id,
                    module,
                    cols,
                    pageKey.current,
                    startIndex,
                    endIndex,
                    orderBy,
                    order,
                    aggregates,
                    applies,
                    styles,
                    tooltips,
                    handleNan,
                    afs,
                    compare ? onCompare : undefined,
                    updateVars && getUpdateVar(updateVars, "comparedatas"),
                    typeof userData == "object"
                        ? (userData as Record<string, Record<string, unknown>>).context
                        : undefined
                )
            );
        } else {
            setValue(props.data[pageKey.current]);
            setLoading(false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [
        refresh,
        startIndex,
        aggregates,
        colsOrder,
        columns,
        showAll,
        rowsPerPage,
        order,
        orderBy,
        updateVarName,
        updateVars,
        id,
        handleNan,
        appliedFilters,
        dispatch,
        module,
        compare,
        onCompare,
        userData,
    ]);

    const onSort = useCallback(
        (e: MouseEvent<HTMLElement>) => {
            const col = e.currentTarget.getAttribute("data-dfid");
            if (col) {
                const isAsc = orderBy === col && order === "asc";
                setOrder(isAsc ? "desc" : "asc");
                setOrderBy(col);
            }
        },
        [orderBy, order]
    );

    const handleChangePage = useCallback(
        (event: unknown, newPage: number) => {
            setStartIndex(newPage * rowsPerPage);
        },
        [rowsPerPage]
    );

    const handleChangeRowsPerPage = useCallback((event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setLoading(true);
        setRowsPerPage(parseInt(event.target.value, 10));
        setStartIndex(0);
    }, []);

    const onAggregate = useCallback((e: MouseEvent<HTMLElement>) => {
        const groupBy = e.currentTarget.getAttribute("data-dfid");
        if (groupBy) {
            setAggregates((ags) => {
                const nags = ags.filter((ag) => ag !== groupBy);
                if (ags.length == nags.length) {
                    nags.push(groupBy);
                }
                return nags;
            });
        }
        e.stopPropagation();
    }, []);

    const onAddRowClick = useCallback(
        () =>
            dispatch(
                createSendActionNameAction(updateVarName, module, {
                    action: onAdd,
                    index: startIndex,
                    user_data: userData,
                })
            ),
        [startIndex, dispatch, updateVarName, onAdd, module, userData]
    );

    const onDownload = useCallback(
        () =>
            dispatch(
                createSendActionNameAction(updateVarName, module, {
                    action: DownloadAction,
                    user_data: userData,
                })
            ),
        [dispatch, updateVarName, module, userData]
    );

    const tableContainerSx = useMemo(() => ({ maxHeight: height }), [height]);

    const pso = useMemo(() => {
        let psOptions = rowsPerPageOptions;
        if (pageSizeOptions) {
            try {
                psOptions = JSON.parse(pageSizeOptions);
            } catch (e) {
                console.log("PaginatedTable pageSizeOptions is wrong ", pageSizeOptions, e);
            }
        }
        if (
            pageSize > 0 &&
            !psOptions.some((ps) =>
                typeof ps === "number" ? ps === pageSize : typeof ps.value === "number" ? ps.value === pageSize : false
            )
        ) {
            psOptions.push({ value: pageSize, label: "" + pageSize });
        }
        if (allowAllRows) {
            psOptions.push({ value: -1, label: "All" });
        }
        psOptions.sort((a, b) => (typeof a === "number" ? a : a.value) - (typeof b === "number" ? b : b.value));
        return psOptions;
    }, [pageSizeOptions, allowAllRows, pageSize]);

    const { rows, rowCount, filteredCount, compRows } = useMemo(() => {
        const ret = { rows: [], rowCount: 0, filteredCount: 0, compRows: [] } as {
            rows: RowType[];
            rowCount: number;
            filteredCount: number;
            compRows: RowType[];
        };
        if (value) {
            if (value.data) {
                ret.rows = value.data as RowType[];
            }
            if (value.rowcount) {
                ret.rowCount = value.rowcount as unknown as number;
                if (value.fullrowcount && value.rowcount != value.fullrowcount) {
                    ret.filteredCount = (value.fullrowcount as unknown as number) - ret.rowCount;
                }
            }
            if (value.comp) {
                ret.compRows = value.comp as RowType[];
            }
        }
        return ret;
    }, [value]);

    const onCellValidation: OnCellValidation = useCallback(
        (value: RowValue, rowIndex: number, colName: string, userValue: string, tz?: string) =>
            dispatch(
                createSendActionNameAction(updateVarName, module, {
                    action: onEdit,
                    value: value,
                    index: getRowIndex(rows[rowIndex], rowIndex, startIndex),
                    col: colName,
                    user_value: userValue,
                    tz: tz,
                    user_data: userData,
                })
            ),
        [dispatch, updateVarName, onEdit, rows, startIndex, module, userData]
    );

    const onRowDeletion: OnRowDeletion = useCallback(
        (rowIndex: number) =>
            dispatch(
                createSendActionNameAction(updateVarName, module, {
                    action: onDelete,
                    index: getRowIndex(rows[rowIndex], rowIndex, startIndex),
                    user_data: userData,
                })
            ),
        [dispatch, updateVarName, onDelete, rows, startIndex, module, userData]
    );

    const onRowSelection: OnRowSelection = useCallback(
        (rowIndex: number, colName?: string, value?: string) =>
            dispatch(
                createSendActionNameAction(updateVarName, module, {
                    action: onAction,
                    index: getRowIndex(rows[rowIndex], rowIndex, startIndex),
                    col: colName === undefined ? null : colName,
                    value,
                    reason: value === undefined ? "click" : "button",
                    user_data: userData,
                })
            ),
        [dispatch, updateVarName, onAction, rows, startIndex, module, userData]
    );

    const onRowClick: OnRowClick = useCallback(
        (e: MouseEvent<HTMLTableRowElement>) => {
            const { index } = e.currentTarget.dataset || {};
            const rowIndex = index === undefined ? NaN : Number(index);
            if (!isNaN(rowIndex)) {
                onRowSelection(rowIndex);
            }
        },
        [onRowSelection]
    );

    const boxSx = useMemo(() => ({ ...baseBoxSx, width: width }), [width]);

    return (
        <Box id={id} sx={boxSx} className={`${className} ${getSuffixedClassNames(className, "-paginated")}`}>
            <Paper sx={paperSx}>
                <Tooltip title={hover || ""}>
                    <TableContainer sx={tableContainerSx}>
                        <Table sx={tableSx} aria-labelledby="tableTitle" size={size} stickyHeader={true}>
                            <TableHead>
                                <TableRow>
                                    {colsOrder.map((col, idx) => (
                                        <TableCell
                                            key={col + idx}
                                            sortDirection={orderBy === columns[col].dfid && order}
                                            sx={columns[col].width ? { width: columns[col].width } : {}}
                                        >
                                            {columns[col].dfid === EDIT_COL ? (
                                                [
                                                    active && editable && onAdd ? (
                                                        <Tooltip title="Add a row" key="addARow">
                                                            <IconButton
                                                                onClick={onAddRowClick}
                                                                size="small"
                                                                sx={iconInRowSx}
                                                            >
                                                                <AddIcon fontSize="inherit" />
                                                            </IconButton>
                                                        </Tooltip>
                                                    ) : null,
                                                    active && filter ? (
                                                        <TableFilter
                                                            key="filter"
                                                            columns={columns}
                                                            colsOrder={colsOrder}
                                                            onValidate={setAppliedFilters}
                                                            appliedFilters={appliedFilters}
                                                            className={className}
                                                            filteredCount={filteredCount}
                                                        />
                                                    ) : null,
                                                    active && downloadable ? (
                                                        <Tooltip title="Download as CSV" key="downloadCsv">
                                                            <IconButton
                                                                onClick={onDownload}
                                                                size="small"
                                                                sx={iconInRowSx}
                                                            >
                                                                <Download fontSize="inherit" />
                                                            </IconButton>
                                                        </Tooltip>
                                                    ) : null,
                                                ]
                                            ) : (
                                                <TableSortLabel
                                                    active={orderBy === columns[col].dfid}
                                                    direction={orderBy === columns[col].dfid ? order : "asc"}
                                                    data-dfid={columns[col].dfid}
                                                    onClick={onSort}
                                                    disabled={!active}
                                                    hideSortIcon={!active}
                                                >
                                                    <Box sx={headBoxSx}>
                                                        {columns[col].groupBy ? (
                                                            <IconButton
                                                                onClick={onAggregate}
                                                                size="small"
                                                                title="aggregate"
                                                                data-dfid={columns[col].dfid}
                                                                disabled={!active}
                                                                sx={iconInRowSx}
                                                            >
                                                                {aggregates.includes(columns[col].dfid) ? (
                                                                    <DataSaverOff fontSize="inherit" />
                                                                ) : (
                                                                    <DataSaverOn fontSize="inherit" />
                                                                )}
                                                            </IconButton>
                                                        ) : null}
                                                        {columns[col].title === undefined
                                                            ? columns[col].dfid
                                                            : columns[col].title}
                                                    </Box>
                                                    {orderBy === columns[col].dfid ? (
                                                        <Box component="span" sx={visuallyHidden}>
                                                            {order === "desc"
                                                                ? "sorted descending"
                                                                : "sorted ascending"}
                                                        </Box>
                                                    ) : null}
                                                </TableSortLabel>
                                            )}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {rows.map((row, index) => {
                                    const sel = selected.indexOf(index + startIndex);
                                    if (sel == 0) {
                                        Promise.resolve().then(
                                            () =>
                                                selectedRowRef.current?.scrollIntoView &&
                                                selectedRowRef.current.scrollIntoView({ block: "center" })
                                        );
                                    }
                                    return (
                                        <TableRow
                                            hover
                                            tabIndex={-1}
                                            key={"row" + index}
                                            selected={sel > -1}
                                            ref={sel == 0 ? selectedRowRef : undefined}
                                            className={getClassName(row, props.lineStyle)}
                                            data-index={index}
                                            onClick={active && onAction ? onRowClick : undefined}
                                        >
                                            {colsOrder.map((col, cidx) => (
                                                <EditableCell
                                                    key={"val" + index + "-" + cidx}
                                                    className={getClassName(row, columns[col].style, col)}
                                                    colDesc={columns[col]}
                                                    value={row[col]}
                                                    formatConfig={formatConfig}
                                                    rowIndex={index}
                                                    onValidation={
                                                        active && !columns[col].notEditable && onEdit
                                                            ? onCellValidation
                                                            : undefined
                                                    }
                                                    onDeletion={
                                                        active && editable && onDelete ? onRowDeletion : undefined
                                                    }
                                                    onSelection={active && onAction ? onRowSelection : undefined}
                                                    nanValue={columns[col].nanValue || props.nanValue}
                                                    tooltip={getTooltip(row, columns[col].tooltip, col)}
                                                    comp={compRows && compRows[index] && compRows[index][col]}
                                                />
                                            ))}
                                        </TableRow>
                                    );
                                })}
                                {rows.length == 0 &&
                                    loading &&
                                    Array.from(Array(30).keys(), (v, idx) => (
                                        <TableRow hover key={"rowskel" + idx}>
                                            {colsOrder.map((col, cidx) => (
                                                <TableCell key={"skel" + cidx}>
                                                    <Skeleton sx={skelSx} />
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                    ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Tooltip>
                {!showAll &&
                    (loading ? (
                        <Skeleton sx={loadingStyle}>
                            <Typography>Loading...</Typography>
                        </Skeleton>
                    ) : (
                        <TablePagination
                            component="div"
                            count={rowCount}
                            page={startIndex / rowsPerPage}
                            rowsPerPage={rowsPerPage}
                            showFirstButton={true}
                            showLastButton={true}
                            rowsPerPageOptions={pso}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                        />
                    ))}
            </Paper>
        </Box>
    );
};

export default PaginatedTable;
