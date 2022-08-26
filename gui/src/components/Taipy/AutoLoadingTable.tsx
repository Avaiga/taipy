import React, { useState, useEffect, useContext, useCallback, useRef, useMemo, CSSProperties, MouseEvent } from "react";
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
import { FixedSizeList as List, ListOnItemsRenderedProps } from "react-window";
import InfiniteLoader from "react-window-infinite-loader";
import Skeleton from "@mui/material/Skeleton";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import AddIcon from "@mui/icons-material/Add";
import DataSaverOn from "@mui/icons-material/DataSaverOn";
import DataSaverOff from "@mui/icons-material/DataSaverOff";

import { TaipyContext } from "../../context/taipyContext";
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
} from "./tableUtils";
import { useDispatchRequestUpdateOnFirstRender, useDynamicProperty, useFormatConfig } from "../../utils/hooks";
import TableFilter, { FilterDesc } from "./TableFilter";

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
        >
            {colsOrder.map((col, cidx) => (
                <EditableCell
                    key={"val" + index + "-" + cidx}
                    className={getClassName(rows[index], columns[col].style)}
                    colDesc={columns[col]}
                    value={rows[index][col]}
                    formatConfig={formatConfig}
                    rowIndex={index}
                    onValidation={onValidation}
                    onDeletion={onDeletion}
                    nanValue={columns[col].nanValue || nanValue}
                    tableCellProps={cellProps[cidx]}
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

const getRowHeight = (size = DEFAULT_SIZE) => size == DEFAULT_SIZE ? 37 : 54;
const getCellSx = (width: string | number | undefined, size = DEFAULT_SIZE) => ({ width: width, height: 22, padding: size == DEFAULT_SIZE ? "7px": undefined });

const AutoLoadingTable = (props: TaipyTableProps) => {
    const {
        className,
        id,
        updateVarName,
        height = "60vh",
        width = "100vw",
        updateVars,
        selected = [],
        pageSize = 100,
        defaultKey = "",
        tp_onEdit = "",
        tp_onDelete = "",
        tp_onAdd = "",
        size = DEFAULT_SIZE,
    } = props;
    const [rows, setRows] = useState<RowType[]>([]);
    const [rowCount, setRowCount] = useState(1000); // need someting > 0 to bootstrap the infinit loader
    const { dispatch } = useContext(TaipyContext);
    const page = useRef<key2Rows>({ key: defaultKey, promises: {} });
    const [orderBy, setOrderBy] = useState("");
    const [order, setOrder] = useState<Order>("asc");
    const [appliedFilters, setAppliedFilters] = useState<FilterDesc[]>([]);
    const [visibleStartIndex, setVisibleStartIndex] = useState(0);
    const [aggregates, setAggregates] = useState<string[]>([]);
    const infiniteLoaderRef = useRef<InfiniteLoader>(null);
    const headerRow = useRef<HTMLTableRowElement>(null);
    const formatConfig = useFormatConfig();

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const editable = useDynamicProperty(props.editable, props.defaultEditable, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    useEffect(() => {
        if (props.data && page.current.key && props.data[page.current.key] !== undefined) {
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
    }, [props.data]);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, updateVars);

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
        if (props.data === null) {
            setRows([]);
            setTimeout(() => infiniteLoaderRef.current?.resetloadMoreItemsCache(true), 1); // So that the state can be changed
        }
    }, [props.data]);

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

    const [colsOrder, columns, styles, handleNan, filter] = useMemo(() => {
        let hNan = !!props.nanValue;
        if (props.columns) {
            try {
                const columns = (
                    typeof props.columns === "string" ? JSON.parse(props.columns) : props.columns
                ) as Record<string, ColumnDesc>;
                let filter = false;
                Object.values(columns).forEach((col) => {
                    if (typeof col.filter != "boolean") {
                        col.filter = !!props.filter;
                    }
                    filter = filter || col.filter;
                    if (typeof col.notEditable != "boolean") {
                        col.notEditable = !editable;
                    } else {
                        col.notEditable = col.notEditable || !editable;
                    }
                });
                addDeleteColumn(
                    (!!(active && editable && (tp_onAdd || tp_onDelete)) ? 1 : 0) + (active && filter ? 1 : 0),
                    columns
                );
                const colsOrder = Object.keys(columns).sort(getsortByIndex(columns));
                const styles = colsOrder.reduce<Record<string, unknown>>((pv, col) => {
                    if (columns[col].style) {
                        pv[columns[col].dfid] = columns[col].style;
                    }
                    hNan = hNan || !!columns[col].nanValue;
                    return pv;
                }, {});
                if (props.lineStyle) {
                    styles[LINE_STYLE] = props.lineStyle;
                }
                return [colsOrder, columns, styles, hNan, filter];
            } catch (e) {
                console.info("ATable.columns: " + ((e as Error).message || e));
            }
        }
        return [[], {}, {}, hNan, false];
    }, [active, editable, tp_onAdd, tp_onDelete, props.columns, props.lineStyle, props.nanValue, props.filter]);

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
                const cols = colsOrder.map((col) => columns[col].dfid);
                const key = `Infinite-${cols.join()}-${orderBy}-${order}${agg}`;
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
                        cols,
                        key,
                        startIndex,
                        stopIndex,
                        orderBy,
                        order,
                        aggregates,
                        applies,
                        styles,
                        handleNan,
                        appliedFilters
                    )
                );
            });
        },
        [aggregates, styles, updateVarName, orderBy, order, id, colsOrder, columns, handleNan, appliedFilters, dispatch]
    );

    const onAddRowClick = useCallback(
        () =>
            dispatch(
                createSendActionNameAction(updateVarName, {
                    action: tp_onAdd,
                    index: visibleStartIndex,
                })
            ),
        [visibleStartIndex, dispatch, updateVarName, tp_onAdd]
    );

    const isItemLoaded = useCallback((index: number) => index < rows.length && !!rows[index], [rows]);

    const onCellValidation: OnCellValidation = useCallback(
        (value: RowValue, rowIndex: number, colName: string, userValue: string) =>
            dispatch(
                createSendActionNameAction(updateVarName, {
                    action: tp_onEdit,
                    value: value,
                    index: rowIndex,
                    col: colName,
                    user_value: userValue,
                })
            ),
        [dispatch, updateVarName, tp_onEdit]
    );

    const onRowDeletion: OnRowDeletion = useCallback(
        (rowIndex: number) =>
            dispatch(
                createSendActionNameAction(updateVarName, {
                    action: tp_onDelete,
                    index: rowIndex,
                })
            ),
        [dispatch, updateVarName, tp_onDelete]
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
            onValidation: active && editable && tp_onEdit ? onCellValidation : undefined,
            onDeletion: active && editable && tp_onDelete ? onRowDeletion : undefined,
            lineStyle: props.lineStyle,
            nanValue: props.nanValue,
        }),
        [
            rows,
            isItemLoaded,
            active,
            editable,
            colsOrder,
            columns,
            selected,
            formatConfig,
            tp_onEdit,
            onCellValidation,
            tp_onDelete,
            onRowDeletion,
            props.lineStyle,
            props.nanValue,
            size,
        ]
    );

    const boxSx = useMemo(() => ({ ...baseBoxSx, width: width }), [width]);

    return (
        <Box sx={boxSx} id={id}>
            <Paper sx={paperSx}>
                <Tooltip title={hover || ""}>
                    <TableContainer>
                        <MuiTable
                            sx={tableSx}
                            aria-labelledby="tableTitle"
                            size={size}
                            className={className}
                            stickyHeader={true}
                        >
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
                                                    active && editable && tp_onAdd ? (
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
                                            <List
                                                height={height}
                                                width={width}
                                                itemCount={rowCount}
                                                itemSize={getRowHeight(size)}
                                                onItemsRendered={onTaipyItemsRendered(onItemsRendered)}
                                                ref={ref}
                                                itemData={rowData}
                                            >
                                                {Row}
                                            </List>
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
