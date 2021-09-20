import React, { useState, useEffect, useContext, useCallback, useRef, useMemo } from "react";
import Box from '@mui/material/Box';
import MuiTable from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell, { TableCellProps } from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import TableSortLabel from '@mui/material/TableSortLabel';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Checkbox from '@mui/material/Checkbox';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import DeleteIcon from '@mui/icons-material/Delete';
import FilterListIcon from '@mui/icons-material/FilterList';
import { visuallyHidden } from '@mui/utils';
import { format } from 'date-fns';

import { TaipyBaseProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createRequestTableUpdateAction } from "../../context/taipyReducers";

//import { useWhyDidYouUpdate } from "../../utils/hooks";

interface TableProps extends TaipyBaseProps {
    pageSize?: number;
    /* eslint "@typescript-eslint/no-explicit-any": "off", curly: "error" */
    value: Record<string, Record<string, any>>
}

type Order = 'asc' | 'desc';

const descendingComparator = (a: any, b: any, orderBy: string) => {
    if (b[orderBy] < a[orderBy]) {
      return -1;
    }
    if (b[orderBy] > a[orderBy]) {
      return 1;
    }
    return 0;
  }
  
const  getComparator = (
    order: Order,
    orderBy: string,
  ) => (a: any, b: any) => order === 'desc'
      ? descendingComparator(a, b, orderBy)
      : -descendingComparator(a, b, orderBy);

const defaultDateFormat = "yyyy/MM/dd";

const formatValue = (val: any, col: any) => {
    switch (col.type) {
        case "datetime64[ns]":
            return format(new Date(val), col.format || defaultDateFormat);
        default:
            return val;
    }
}

const alignCell = (col: any): Partial<TableCellProps> => {
    switch (col.type) {
        case "int64":
        case "float64":
            return {align: "right"};
        default:
            return {};
    }
}

const Table = (props: TableProps) => {
    const { className, id, tp_varname, pageSize = 100 } = props;
    const [value, setValue] = useState<Record<string, Record<string, unknown>>>({});
    const [startIndex, setStartIndex] = useState(0);
    const { dispatch } = useContext(TaipyContext);
    const pageKey = useRef('no-page');
    const [orderBy, setOrderBy] = useState('');
    const [order, setOrder] = useState<Order>('asc');

//    useWhyDidYouUpdate('TaipyTable', props);

    useEffect(() => {
        if (props.value && typeof props.value[pageKey.current] !== 'undefined') {
            setValue(props.value[pageKey.current])
        }
    }, [props.value]);

    /* eslint react-hooks/exhaustive-deps: "off", curly: "error" */
    useEffect(() => {
        pageKey.current = `${startIndex}-${startIndex + pageSize}`;
        if (!props.value || typeof props.value[pageKey.current] === 'undefined') {
            dispatch(createRequestTableUpdateAction(tp_varname, id, pageKey.current, startIndex, startIndex + pageSize));
        } else {
            // {columns: [], data: [][], index: []}
            setValue(props.value[pageKey.current])
        }
    }, [startIndex, tp_varname, id, dispatch, pageSize]);

    const otherPage = useCallback(e => {
        setStartIndex(si => {
            if (si === -1) {
                si = Number(Object.keys(value)[0]);
            }
            const [id] = e.target.id.split('-').slice(-1);
            switch (id) {
                case 'top':
                    return 0;
                case 'bot':
                    return -1;
                case 'prev':
                    return si - pageSize > 0 ? si - pageSize : 0;
                case 'next':
                    return si + pageSize;
                default:
                    return si;
            }
        })
        e.preventDefault();
        e.stopPropagation();
    }, [value, pageSize]);

    const handleRequestSort = useCallback((
        event: React.MouseEvent<unknown>,
        col: string,
      ) => {
        const isAsc = orderBy === col && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(col);
      }, [orderBy, order]);

    const createSortHandler = useCallback((col: string) => (event: React.MouseEvent<unknown>) => {
        handleRequestSort(event, col);
    }, [handleRequestSort]);

    const handleChangePage = useCallback((event: unknown, newPage: number) => {
        setStartIndex(newPage * pageSize);
    }, [pageSize]);

    const {rows, cols, rowCount} = useMemo(() => {
        const ret = {rows: [], cols: {}, rowCount: 0} as {rows: any[], cols: any, rowCount: number};
        if (value) {
            if (value.coltypes) {
                ret.cols = value.coltypes;
            }
            if (value.data) {
                ret.rows = Object.keys(value.data).map(key => value.data[key]);
            }
            if (value.rowcount) {
                ret.rowCount = value.rowcount as unknown as number;
            }
        }
        return ret;
    }, [value]);

    return <>
        <Box sx={{ width: '100%' }}>
            <Paper sx={{ width: '100%', mb: 2 }}>
        <TableContainer>
          <MuiTable
            sx={{ minWidth: 750 }}
            aria-labelledby="tableTitle"
            size={'medium'}
          >
        <TableHead>
            <TableRow>
                {
                    Object.keys(cols).map((key, idx) => <TableCell 
                        key={'col'+idx} 
                        sortDirection={orderBy === key && order}>
                            <TableSortLabel
                                active={orderBy === key}
                                direction={orderBy === key ? order : 'asc'}
                                onClick={createSortHandler(key)}
                                >
                            {cols[key].label || key}
                            {orderBy === key ? (
                                <Box component="span" sx={visuallyHidden}>
                                {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                                </Box>
                            ) : null}
                            </TableSortLabel>
                        </TableCell>)
                }
            </TableRow>
        </TableHead>
        <TableBody>
            {
            rows.slice().sort(getComparator(order, orderBy))
                .map((row, index) => {
                  const isItemSelected = false;
                  return (
                    <TableRow
                      hover
                      tabIndex={-1}
                      key={'row' + index}
                      selected={isItemSelected}
                    >
                      {Object.keys(row).map((key, cidx) => <TableCell key={'val'+index + '-'+ cidx} {...alignCell(cols[key])}>{formatValue(row[key], cols[key])}</TableCell>)}
                    </TableRow>
                  );
                })
            }
        </TableBody>
        </MuiTable>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[pageSize]}
          component="div"
          count={rowCount}
          rowsPerPage={pageSize}
          page={startIndex / pageSize}
          onPageChange={handleChangePage}
        />
      </Paper>
      </Box>
    </>
};

export default Table;
