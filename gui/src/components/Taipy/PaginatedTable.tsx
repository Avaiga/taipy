import React, { useState, useEffect, useContext, useCallback, useRef, useMemo, CSSProperties } from "react";
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

import { TaipyContext } from "../../context/taipyContext";
import { createRequestTableUpdateAction } from "../../context/taipyReducers";
import {
    alignCell,
    boxSx,
    formatValue,
    getsortByIndex,
    Order,
    paperSx,
    tableSx,
    TaipyPaginatedTableProps,
    tcSx,
} from "./tableUtils";
//import { useWhyDidYouUpdate } from "../../utils/hooks";

const loadingStyle: CSSProperties = { height: "52px", textAlign: "right", verticalAlign: "center" };

const rowsPerPageOptions = [10, 50, 100, 500];

const PaginatedTable = (props: TaipyPaginatedTableProps) => {
    const {
        className,
        id,
        tp_varname,
        pageSize = 100,
        pageSizeOptions = rowsPerPageOptions,
        allowAllRows = false,
        showAll = false,
    } = props;
    const [value, setValue] = useState<Record<string, unknown>>({});
    const [startIndex, setStartIndex] = useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(pageSize);
    const { dispatch } = useContext(TaipyContext);
    const pageKey = useRef("no-page");
    const [orderBy, setOrderBy] = useState("");
    const [order, setOrder] = useState<Order>("asc");
    const [loading, setLoading] = useState(true);

    //    useWhyDidYouUpdate('TaipyTable', props);

    useEffect(() => {
        if (props.value && props.value[pageKey.current] !== undefined) {
            setValue(props.value[pageKey.current]);
            setLoading(false);
        }
    }, [props.value]);

    /* eslint react-hooks/exhaustive-deps: "off", curly: "error" */
    useEffect(() => {
        const endIndex = showAll ? -1 : startIndex + rowsPerPage;
        pageKey.current = `${startIndex}-${endIndex}-${orderBy}-${order}`;
        if (!props.value || props.value[pageKey.current] === undefined) {
            setLoading(true);
            dispatch(
                createRequestTableUpdateAction(tp_varname, id, pageKey.current, startIndex, endIndex, orderBy, order)
            );
        } else {
            setValue(props.value[pageKey.current]);
            setLoading(false);
        }
    }, [startIndex, showAll, rowsPerPage, order, orderBy, tp_varname, id, dispatch]);

    const handleRequestSort = useCallback(
        (event: React.MouseEvent<unknown>, col: string) => {
            const isAsc = orderBy === col && order === "asc";
            setOrder(isAsc ? "desc" : "asc");
            setOrderBy(col);
        },
        [orderBy, order]
    );

    const createSortHandler = useCallback(
        (col: string) => (event: React.MouseEvent<unknown>) => {
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

    const handleChangeRowsPerPage = useCallback((event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setLoading(true);
        setRowsPerPage(parseInt(event.target.value, 10));
        setStartIndex(0);
    }, []);

    const [colsOrder, columns] = useMemo(() => {
        if (props.columns) {
            const columns = typeof props.columns === "string" ? JSON.parse(props.columns) : props.columns;
            return [Object.keys(columns).sort(getsortByIndex(columns)), columns];
        }
        return [[], {}];
    }, [props.columns]);

    const pso = useMemo(() => {
        if (allowAllRows) {
            return pageSizeOptions.concat([{ value: -1, label: "All" }]);
        }
        return pageSizeOptions;
    }, [pageSizeOptions, allowAllRows]);

    const { rows, rowCount } = useMemo(() => {
        const ret = { rows: [], rowCount: 0 } as { rows: any[]; rowCount: number };
        if (value) {
            if (value.data) {
                ret.rows = value.data as any[];
            }
            if (value.rowcount) {
                ret.rowCount = value.rowcount as unknown as number;
            }
        }
        return ret;
    }, [value]);

    return (
        <>
            <Box sx={boxSx}>
                <Paper sx={paperSx}>
                    <TableContainer sx={tcSx}>
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
                                        <TableCell
                                            key={col + idx}
                                            sortDirection={orderBy === columns[col].dfid && order}
                                        >
                                            <TableSortLabel
                                                active={orderBy === columns[col].dfid}
                                                direction={orderBy === columns[col].dfid ? order : "asc"}
                                                onClick={createSortHandler(columns[col].dfid)}
                                            >
                                                {columns[col].title || columns[col].dfid}
                                                {orderBy === columns[col].dfid ? (
                                                    <Box component="span" sx={visuallyHidden}>
                                                        {order === "desc" ? "sorted descending" : "sorted ascending"}
                                                    </Box>
                                                ) : null}
                                            </TableSortLabel>
                                        </TableCell>
                                    ))}
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {rows.map((row, index) => {
                                    const isItemSelected = false;
                                    return (
                                        <TableRow hover tabIndex={-1} key={"row" + index} selected={isItemSelected}>
                                            {colsOrder.map((col, cidx) => (
                                                <TableCell
                                                    key={"val" + index + "-" + cidx}
                                                    {...alignCell(columns[col])}
                                                >
                                                    {formatValue(row[col], columns[col])}
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
                                                    <Skeleton width="100%" height="3rem" />
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                    ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    {!showAll &&
                        (loading ? (
                            <Skeleton width="100%" style={loadingStyle}>
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
        </>
    );
};

export default PaginatedTable;
