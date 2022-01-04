import React, {
    useState,
    useEffect,
    useContext,
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
import { visuallyHidden } from "@mui/utils";
import IconButton from "@mui/material/IconButton";
import AddIcon from "@mui/icons-material/Add";
import DataSaverOn from "@mui/icons-material/DataSaverOn";
import DataSaverOff from "@mui/icons-material/DataSaverOff";

import { TaipyContext } from "../../context/taipyContext";
import { createRequestTableUpdateAction, createSendActionNameAction } from "../../context/taipyReducers";
import {
    addDeleteColumn,
    alignCell,
    boxSx,
    EditableCell,
    EDIT_COL,
    getClassName,
    getsortByIndex,
    headBoxSx,
    iconInRowSx,
    OnCellValidation,
    OnRowDeletion,
    Order,
    PageSizeOptionsType,
    paperSx,
    RowType,
    RowValue,
    tableSx,
    TaipyPaginatedTableProps,
} from "./tableUtils";
import { useDispatchRequestUpdateOnFirstRender, useDynamicProperty, useFormatConfig } from "../../utils/hooks";

const loadingStyle: CSSProperties = { width: "100%", height: "3em", textAlign: "right", verticalAlign: "center" };
const skelSx = { width: "100%", height: "3em" };

const rowsPerPageOptions: PageSizeOptionsType = [10, 50, 100, 500];

const PaginatedTable = (props: TaipyPaginatedTableProps) => {
    const {
        className,
        id,
        tp_varname,
        pageSize = 100,
        pageSizeOptions,
        allowAllRows = false,
        showAll = false,
        refresh = false,
        height,
        selected = [],
        tp_updatevars,
        editAction = "",
        deleteAction = "",
        addAction = "",
    } = props;
    const [value, setValue] = useState<Record<string, unknown>>({});
    const [startIndex, setStartIndex] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(pageSize);
    const [order, setOrder] = useState<Order>("asc");
    const [orderBy, setOrderBy] = useState("");
    const [loading, setLoading] = useState(true);
    const [aggregates, setAggregates] = useState<string[]>([]);
    const { dispatch } = useContext(TaipyContext);
    const pageKey = useRef("no-page");
    const selectedRowRef = useRef<HTMLTableRowElement | null>(null);
    const formatConfig = useFormatConfig();

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const editable = useDynamicProperty(props.editable, props.defaultEditable, true);

    const [colsOrder, columns, styles] = useMemo(() => {
        if (props.columns) {
            const columns = typeof props.columns === "string" ? JSON.parse(props.columns) : props.columns;
            addDeleteColumn(!!(active && editable && deleteAction), columns);
            const colsOrder = Object.keys(columns).sort(getsortByIndex(columns));
            const styles = colsOrder.reduce<Record<string, unknown>>((pv, col) => {
                if (columns[col].style) {
                    pv[columns[col].dfid] = columns[col].style;
                }
                return pv;
            }, {});
            return [colsOrder, columns, styles];
        }
        return [[], {}, {}];
    }, [active, editable, deleteAction, props.columns]);

    useDispatchRequestUpdateOnFirstRender(dispatch, id, tp_updatevars);

    useEffect(() => {
        if (selected.length) {
            if (selected[0] < startIndex || selected[0] > startIndex + rowsPerPage) {
                setLoading(true);
                setStartIndex(rowsPerPage * Math.floor(selected[0] / rowsPerPage));
            }
        }
    }, [selected, startIndex, rowsPerPage]);

    useEffect(() => {
        if (props.value && props.value[pageKey.current] !== undefined) {
            setValue(props.value[pageKey.current]);
            setLoading(false);
        }
    }, [props.value]);

    useEffect(() => {
        const endIndex = showAll ? -1 : startIndex + rowsPerPage;
        const agg = aggregates.length
            ? colsOrder.reduce((pv, col, idx) => {
                  if (aggregates.includes(columns[col].dfid)) {
                      return pv + "-" + idx;
                  }
                  return pv;
              }, "-agg")
            : "";
        pageKey.current = `${startIndex}-${endIndex}-${orderBy}-${order}${agg}`;
        if (!props.value || props.value[pageKey.current] === undefined || !!refresh) {
            setLoading(true);
            const cols = colsOrder.map((col) => columns[col].dfid);
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
                    tp_varname,
                    id,
                    cols,
                    pageKey.current,
                    startIndex,
                    endIndex,
                    orderBy,
                    order,
                    aggregates,
                    applies,
                    styles
                )
            );
        } else {
            setValue(props.value[pageKey.current]);
            setLoading(false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [
        startIndex,
        refresh,
        aggregates,
        colsOrder,
        columns,
        showAll,
        rowsPerPage,
        order,
        orderBy,
        tp_varname,
        id,
        dispatch,
    ]);

    const handleRequestSort = useCallback(
        (event: MouseEvent<unknown>, col: string) => {
            const isAsc = orderBy === col && order === "asc";
            setOrder(isAsc ? "desc" : "asc");
            setOrderBy(col);
        },
        [orderBy, order]
    );

    const createSortHandler = useCallback(
        (col: string) => (event: MouseEvent<unknown>) => {
            handleRequestSort(event, col);
        },
        [handleRequestSort]
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
                createSendActionNameAction(tp_varname, {
                    action: addAction,
                    index: startIndex,
                })
            ),
        [startIndex, dispatch, tp_varname, addAction]
    );

    const onCellValidation: OnCellValidation = useCallback(
        (value: RowValue, rowIndex: number, colName: string) =>
            dispatch(
                createSendActionNameAction(tp_varname, {
                    action: editAction,
                    value: value,
                    index: rowIndex,
                    col: colName,
                })
            ),
        [dispatch, tp_varname, editAction]
    );

    const onRowDeletion: OnRowDeletion = useCallback(
        (rowIndex: number) =>
            dispatch(
                createSendActionNameAction(tp_varname, {
                    action: deleteAction,
                    index: rowIndex,
                })
            ),
        [dispatch, tp_varname, deleteAction]
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
        if (allowAllRows) {
            return psOptions.concat([{ value: -1, label: "All" }]);
        }
        return psOptions;
    }, [pageSizeOptions, allowAllRows]);

    const { rows, rowCount } = useMemo(() => {
        const ret = { rows: [], rowCount: 0 } as { rows: RowType[]; rowCount: number };
        if (value) {
            if (value.data) {
                ret.rows = value.data as RowType[];
            }
            if (value.rowcount) {
                ret.rowCount = value.rowcount as unknown as number;
            }
        }
        return ret;
    }, [value]);

    return (
        <Box id={id} sx={boxSx}>
            <Paper sx={paperSx}>
                <TableContainer sx={tableContainerSx}>
                    <Table
                        sx={tableSx}
                        aria-labelledby="tableTitle"
                        size={"medium"}
                        className={className}
                        stickyHeader={true}
                    >
                        <TableHead>
                            <TableRow>
                                {colsOrder.map((col, idx) => (
                                    <TableCell key={col + idx} sortDirection={orderBy === columns[col].dfid && order}>
                                        {columns[col].dfid === EDIT_COL ? (
                                            active && editable && addAction ? (
                                                <IconButton onClick={onAddRowClick} size="small" sx={iconInRowSx}>
                                                    <AddIcon />
                                                </IconButton>
                                            ) : null
                                        ) : (
                                            <TableSortLabel
                                                active={orderBy === columns[col].dfid}
                                                direction={orderBy === columns[col].dfid ? order : "asc"}
                                                onClick={createSortHandler(columns[col].dfid)}
                                                disabled={!active}
                                            >
                                                <Box sx={headBoxSx}>
                                                    {columns[col].groupBy ? (
                                                        <IconButton
                                                            onClick={onAggregate}
                                                            size="small"
                                                            title="aggregate"
                                                            sx={iconInRowSx}
                                                            data-dfid={columns[col].dfid}
                                                            disabled={!active}
                                                        >
                                                            {aggregates.includes(columns[col].dfid) ? (
                                                                <DataSaverOff />
                                                            ) : (
                                                                <DataSaverOn />
                                                            )}
                                                        </IconButton>
                                                    ) : null}
                                                    {columns[col].title === undefined
                                                        ? columns[col].dfid
                                                        : columns[col].title}
                                                </Box>
                                                {orderBy === columns[col].dfid ? (
                                                    <Box component="span" sx={visuallyHidden}>
                                                        {order === "desc" ? "sorted descending" : "sorted ascending"}
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
                                    setTimeout(() => selectedRowRef.current?.scrollIntoView({ block: "center" }), 1);
                                }
                                return (
                                    <TableRow
                                        hover
                                        tabIndex={-1}
                                        key={"row" + index}
                                        selected={sel > -1}
                                        ref={sel == 0 ? selectedRowRef : undefined}
                                    >
                                        {colsOrder.map((col, cidx) => (
                                            <TableCell
                                                key={"val" + index + "-" + cidx}
                                                {...alignCell(columns[col])}
                                                className={getClassName(rows[index], columns[col].style)}
                                            >
                                                <EditableCell
                                                    colDesc={columns[col]}
                                                    value={rows[index][col]}
                                                    formatConfig={formatConfig}
                                                    rowIndex={index}
                                                    onValidation={
                                                        active && editable && editAction ? onCellValidation : undefined
                                                    }
                                                    onDeletion={
                                                        active && editable && deleteAction ? onRowDeletion : undefined
                                                    }
                                                />
                                            </TableCell>
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
