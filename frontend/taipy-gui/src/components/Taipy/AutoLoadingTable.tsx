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

import React, { useState, useEffect, useCallback, useRef, useMemo, CSSProperties, MouseEvent } from "react";
import Box from "@mui/material/Box";
import MuiTable from "@mui/material/Table";
import TableCell, { TableCellProps } from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import Paper from "@mui/material/Paper";
import { visuallyHidden } from "@mui/utils";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList, ListOnItemsRenderedProps } from "react-window";
import InfiniteLoader from "react-window-infinite-loader";
import Skeleton from "@mui/material/Skeleton";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import AddIcon from "@mui/icons-material/Add";
import DataSaverOn from "@mui/icons-material/DataSaverOn";
import DataSaverOff from "@mui/icons-material/DataSaverOff";

import {
    createRequestInfiniteTableUpdateAction,
    createSendActionNameAction,
    FormatConfig,
} from "../../context/taipyReducers";
import {
    ColumnDesc,
    getsortByIndex,
    Order,
    TaipyTableProps,
    baseBoxSx,
    paperSx,
    tableSx,
    RowType,
    EditableCell,
    OnCellValidation,
    RowValue,
    EDIT_COL,
    OnRowDeletion,
    addDeleteColumn,
    headBoxSx,
    getClassName,
    LINE_STYLE,
    iconInRowSx,
    DEFAULT_SIZE,
    OnRowSelection,
    getRowIndex,
    getTooltip,
    defaultColumns,
    OnRowClick,
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
import { getSuffixedClassNames } from "./utils";

interface RowData {
    colsOrder: string[];
    columns: Record<string, ColumnDesc>;
    rows: RowType[];
    classes: Record<string, string>;
    cellProps: Partial<TableCellProps>[];
    isItemLoaded: (index: number) => boolean;
    selection: number[];
    formatConfig: FormatConfig;
    onValidation?: OnCellValidation;
    onDeletion?: OnRowDeletion;
    onRowSelection?: OnRowSelection;
    onRowClick?: OnRowClick;
    lineStyle?: string;
    nanValue?: string;
}

const Row = ({
    index,
    style,
    data: {
        colsOrder,
        columns,
        rows,
        classes,
        cellProps,
        isItemLoaded,
        selection,
        formatConfig,
        onValidation,
        onDeletion,
        onRowSelection,
        onRowClick,
        lineStyle,
        nanValue,
    },
}: {
    index: number;
    style: CSSProperties;
    data: RowData;
}) =>
    isItemLoaded(index) ? (
        <TableRow
            hover
            tabIndex={-1}
            key={"row" + index}
            component="div"
            sx={style}
            className={(classes && classes.row) + " " + getClassName(rows[index], lineStyle)}
            data-index={index}
            selected={selection.indexOf(index) > -1}
            onClick={onRowClick}
        >
            {colsOrder.map((col, cidx) => (
                <EditableCell
                    key={"val" + index + "-" + cidx}
                    className={getClassName(rows[index], columns[col].style, col)}
                    colDesc={columns[col]}
                    value={rows[index][col]}
                    formatConfig={formatConfig}
                    rowIndex={index}
                    onValidation={!columns[col].notEditable ? onValidation : undefined}
                    onDeletion={onDeletion}
                    onSelection={onRowSelection}
                    nanValue={columns[col].nanValue || nanValue}
                    tableCellProps={cellProps[cidx]}
                    tooltip={getTooltip(rows[index], columns[col].tooltip, col)}
                />
            ))}
        </TableRow>
    ) : (
        <Skeleton sx={style} key={"Skeleton" + index} />
    );

interface PromiseProps {
    resolve: () => void;
    reject: () => void;
}

interface key2Rows {
    key: string;
    promises: Record<number, PromiseProps>;
}

const getRowHeight = (size = DEFAULT_SIZE) => (size == DEFAULT_SIZE ? 37 : 54);
const getCellSx = (width: string | number | undefined, size = DEFAULT_SIZE) => ({
    width: width,
    height: 22,
    padding: size == DEFAULT_SIZE ? "7px" : undefined,
});

const AutoLoadingTable = (props: TaipyTableProps) => {
    const {
        id,
        updateVarName,
        height = "80vh",
        width = "100%",
        updateVars,
        selected = [],
        pageSize = 100,
        defaultKey = "",
        onEdit = "",
        onDelete = "",
        onAdd = "",
        onAction = "",
        size = DEFAULT_SIZE,
        userData,
    } = props;
    const [rows, setRows] = useState<RowType[]>([]);
    const [rowCount, setRowCount] = useState(1000); // need something > 0 to bootstrap the infinite loader
    const dispatch = useDispatch();
    const page = useRef<key2Rows>({ key: defaultKey, promises: {} });
    const [orderBy, setOrderBy] = useState("");
    const [order, setOrder] = useState<Order>("asc");
    const [appliedFilters, setAppliedFilters] = useState<FilterDesc[]>([]);
    const [visibleStartIndex, setVisibleStartIndex] = useState(0);
    const [aggregates, setAggregates] = useState<string[]>([]);
    const infiniteLoaderRef = useRef<InfiniteLoader>(null);
    const headerRow = useRef<HTMLTableRowElement>(null);
    const formatConfig = useFormatConfig();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const editable = useDynamicProperty(props.editable, props.defaultEditable, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const baseColumns = useDynamicJsonProperty(props.columns, props.defaultColumns, defaultColumns);

    const refresh = typeof props.data === "number";

    useEffect(() => {
        if (!refresh && props.data && page.current.key && props.data[page.current.key] !== undefined) {
            const newValue = props.data[page.current.key];
            const promise = page.current.promises[newValue.start];
            setRowCount(newValue.rowcount);
            const nr = newValue.data as RowType[];
            if (Array.isArray(nr) && nr.length > newValue.start) {
                setRows(nr);
                promise && promise.resolve();
            } else {
                promise && promise.reject();
            }
            delete page.current.promises[newValue.start];
        }
    }, [refresh, props.data]);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, updateVars);

    const onSort = useCallback(
        (e: React.MouseEvent<HTMLElement>) => {
            const col = e.currentTarget.getAttribute("data-dfid");
            if (col) {
                const isAsc = orderBy === col && order === "asc";
                setOrder(isAsc ? "desc" : "asc");
                setOrderBy(col);
                setRows([]);
                setTimeout(() => infiniteLoaderRef.current?.resetloadMoreItemsCache(true), 1); // So that the state can be changed
            }
        },
        [orderBy, order]
    );

    useEffect(() => {
        if (refresh) {
            setRows([]);
            setTimeout(() => infiniteLoaderRef.current?.resetloadMoreItemsCache(true), 1); // So that the state can be changed
        }
    }, [refresh]);

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

    const [colsOrder, columns, styles, tooltips, handleNan, filter] = useMemo(() => {
        let hNan = !!props.nanValue;
        if (baseColumns) {
            try {
                let filter = false;
                Object.values(baseColumns).forEach((col) => {
                    if (typeof col.filter != "boolean") {
                        col.filter = !!props.filter;
                    }
                    filter = filter || col.filter;
                    if (typeof col.notEditable != "boolean") {
                        col.notEditable = !editable;
                    }
                    if (col.tooltip === undefined) {
                        col.tooltip = props.tooltip;
                    }
                });
                addDeleteColumn((active && (onAdd || onDelete) ? 1 : 0) + (active && filter ? 1 : 0), baseColumns);
                const colsOrder = Object.keys(baseColumns).sort(getsortByIndex(baseColumns));
                const styTt = colsOrder.reduce<Record<string, Record<string, string>>>((pv, col) => {
                    if (baseColumns[col].style) {
                        pv.styles = pv.styles || {};
                        pv.styles[baseColumns[col].dfid] = baseColumns[col].style as string;
                    }
                    hNan = hNan || !!baseColumns[col].nanValue;
                    if (baseColumns[col].tooltip) {
                        pv.tooltips = pv.tooltips || {};
                        pv.tooltips[baseColumns[col].dfid] = baseColumns[col].tooltip as string;
                    }
                    return pv;
                }, {});
                if (props.lineStyle) {
                    styTt.styles = styTt.styles || {};
                    styTt.styles[LINE_STYLE] = props.lineStyle;
                }
                return [colsOrder, baseColumns, styTt.styles, styTt.tooltips, hNan, filter];
            } catch (e) {
                console.info("ATable.columns: " + ((e as Error).message || e));
            }
        }
        return [
            [],
            {} as Record<string, ColumnDesc>,
            {} as Record<string, string>,
            {} as Record<string, string>,
            hNan,
            false,
        ];
    }, [active, editable, onAdd, onDelete, baseColumns, props.lineStyle, props.tooltip, props.nanValue, props.filter]);

    const boxBodySx = useMemo(() => ({ height: height }), [height]);

    useEffect(() => {
        selected.length &&
            infiniteLoaderRef.current &&
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            (infiniteLoaderRef.current as any)._listRef.scrollToItem(selected[0]);
    }, [selected]);

    useEffect(() => {
        if (headerRow.current) {
            Array.from(headerRow.current.cells).forEach((cell, idx) => {
                columns[colsOrder[idx]].widthHint = cell.offsetWidth;
            });
        }
    }, [columns, colsOrder]);

    const loadMoreItems = useCallback(
        (startIndex: number, stopIndex: number) => {
            if (page.current.promises[startIndex]) {
                page.current.promises[startIndex].reject();
            }
            return new Promise<void>((resolve, reject) => {
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
                const key = `Infinite-${cols.join()}-${orderBy}-${order}${agg}${afs.map(
                    (af) => `${af.col}${af.action}${af.value}`
                )}`;
                page.current = {
                    key: key,
                    promises: { ...page.current.promises, [startIndex]: { resolve: resolve, reject: reject } },
                };
                const applies = aggregates.length
                    ? colsOrder.reduce<Record<string, unknown>>((pv, col) => {
                          if (columns[col].apply) {
                              pv[columns[col].dfid] = columns[col].apply;
                          }
                          return pv;
                      }, {})
                    : undefined;
                dispatch(
                    createRequestInfiniteTableUpdateAction(
                        updateVarName,
                        id,
                        module,
                        cols,
                        key,
                        startIndex,
                        stopIndex,
                        orderBy,
                        order,
                        aggregates,
                        applies,
                        styles,
                        tooltips,
                        handleNan,
                        afs
                    )
                );
            });
        },
        [
            aggregates,
            styles,
            tooltips,
            updateVarName,
            orderBy,
            order,
            id,
            colsOrder,
            columns,
            handleNan,
            appliedFilters,
            dispatch,
            module,
        ]
    );

    const onAddRowClick = useCallback(
        () =>
            dispatch(
                createSendActionNameAction(updateVarName, module, {
                    action: onAdd,
                    index: visibleStartIndex,
                    user_data: userData,
                })
            ),
        [visibleStartIndex, dispatch, updateVarName, onAdd, module, userData]
    );

    const isItemLoaded = useCallback((index: number) => index < rows.length && !!rows[index], [rows]);

    const onCellValidation: OnCellValidation = useCallback(
        (value: RowValue, rowIndex: number, colName: string, userValue: string, tz?: string) =>
            dispatch(
                createSendActionNameAction(updateVarName, module, {
                    action: onEdit,
                    value: value,
                    index: getRowIndex(rows[rowIndex], rowIndex),
                    col: colName,
                    user_value: userValue,
                    tz: tz,
                    user_data: userData,
                })
            ),
        [dispatch, updateVarName, onEdit, rows, module, userData]
    );

    const onRowDeletion: OnRowDeletion = useCallback(
        (rowIndex: number) =>
            dispatch(
                createSendActionNameAction(updateVarName, module, {
                    action: onDelete,
                    index: getRowIndex(rows[rowIndex], rowIndex),
                    user_data: userData,
                })
            ),
        [dispatch, updateVarName, onDelete, rows, module, userData]
    );

    const onRowSelection: OnRowSelection = useCallback(
        (rowIndex: number, colName?: string) =>
            dispatch(
                createSendActionNameAction(updateVarName, module, {
                    action: onAction,
                    index: getRowIndex(rows[rowIndex], rowIndex),
                    col: colName === undefined ? null : colName,
                    user_data: userData,
                })
            ),
        [dispatch, updateVarName, onAction, rows, module, userData]
    );

    const onRowClick = useCallback(
        (e: MouseEvent<HTMLTableRowElement>) => {
            const { index } = e.currentTarget.dataset || {};
            const rowIndex = index === undefined ? NaN : Number(index);
            if (!isNaN(rowIndex)) {
                onRowSelection(rowIndex);
            }
        },
        [onRowSelection]
    );

    const onTaipyItemsRendered = useCallback(
        (onItemsR: (props: ListOnItemsRenderedProps) => undefined) =>
            ({ visibleStartIndex, visibleStopIndex }: { visibleStartIndex: number; visibleStopIndex: number }) => {
                setVisibleStartIndex(visibleStartIndex);
                onItemsR({ visibleStartIndex, visibleStopIndex } as ListOnItemsRenderedProps);
            },
        []
    );

    const rowData: RowData = useMemo(
        () => ({
            colsOrder: colsOrder,
            columns: columns,
            rows: rows,
            classes: {},
            cellProps: colsOrder.map((col) => ({
                sx: getCellSx(columns[col].width || columns[col].widthHint, size),
                component: "div",
                variant: "body",
            })),

            isItemLoaded: isItemLoaded,
            selection: selected,
            formatConfig: formatConfig,
            onValidation: active && onEdit ? onCellValidation : undefined,
            onDeletion: active && onDelete ? onRowDeletion : undefined,
            onRowSelection: active && onAction ? onRowSelection : undefined,
            onRowClick: active && onAction ? onRowClick : undefined,
            lineStyle: props.lineStyle,
            nanValue: props.nanValue,
        }),
        [
            rows,
            isItemLoaded,
            active,
            colsOrder,
            columns,
            selected,
            formatConfig,
            onEdit,
            onCellValidation,
            onDelete,
            onRowDeletion,
            onAction,
            onRowSelection,
            onRowClick,
            props.lineStyle,
            props.nanValue,
            size,
        ]
    );

    const boxSx = useMemo(() => ({ ...baseBoxSx, width: width }), [width]);

    return (
        <Box id={id} sx={boxSx} className={`${className} ${getSuffixedClassNames(className, "-autoloading")}`}>
            <Paper sx={paperSx}>
                <Tooltip title={hover || ""}>
                    <TableContainer>
                        <MuiTable sx={tableSx} aria-labelledby="tableTitle" size={size} stickyHeader={true}>
                            <TableHead>
                                <TableRow ref={headerRow}>
                                    {colsOrder.map((col, idx) => (
                                        <TableCell
                                            key={col + idx}
                                            sortDirection={orderBy === columns[col].dfid && order}
                                            sx={columns[col].width ? { width: columns[col].width } : {}}
                                        >
                                            {columns[col].dfid === EDIT_COL ? (
                                                [
                                                    active && onAdd ? (
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
                                                        />
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
                        </MuiTable>
                        <Box sx={boxBodySx}>
                            <AutoSizer>
                                {({ height, width }) => (
                                    <InfiniteLoader
                                        ref={infiniteLoaderRef}
                                        isItemLoaded={isItemLoaded}
                                        itemCount={rowCount}
                                        loadMoreItems={loadMoreItems}
                                        minimumBatchSize={pageSize}
                                    >
                                        {({ onItemsRendered, ref }) => (
                                            <FixedSizeList
                                                height={height || 100}
                                                width={width || 100}
                                                itemCount={rowCount}
                                                itemSize={getRowHeight(size)}
                                                onItemsRendered={onTaipyItemsRendered(onItemsRendered)}
                                                ref={ref}
                                                itemData={rowData}
                                            >
                                                {Row}
                                            </FixedSizeList>
                                        )}
                                    </InfiniteLoader>
                                )}
                            </AutoSizer>
                        </Box>
                    </TableContainer>
                </Tooltip>
            </Paper>
        </Box>
    );
};

export default AutoLoadingTable;
