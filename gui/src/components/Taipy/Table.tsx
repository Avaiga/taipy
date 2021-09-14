import React, { useState, useEffect, useContext, useCallback } from "react";

import { setValueForVarName, TaipyBaseProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createRequestTableUpdateAction } from "../../context/taipyReducers";
import { useWhyDidYouUpdate } from "../../utils/hooks";

interface TableProps extends TaipyBaseProps {
    pageSize?: number;
}

const Table = (props: TableProps) => {
    const { className, id, tp_varname, pageSize = 100 } = props;
    const [value, setValue] = useState<Record<string, any>>({});
    const [startIndex, setStartIndex] = useState(0);
    const { dispatch } = useContext(TaipyContext);

    useWhyDidYouUpdate('TaipyTable', props);

    useEffect(() => {
        setValueForVarName(tp_varname, props, setValue);
    }, [tp_varname, props]);

    useEffect(() => {
        dispatch(createRequestTableUpdateAction(tp_varname, id, startIndex, startIndex + pageSize));
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
        return false;
    }, [value, pageSize]);

    return <>
        <table className={className} id={id}>
            {
                Object.keys(value).map((rowKey: string) => <tr><td>{rowKey}</td>{
                    typeof value[rowKey] === 'object' ?
                        Object.keys(value[rowKey]).map((colKey: string) => <td>{value[rowKey][colKey]}</td>)
                        :
                        <td>{value[rowKey]}</td>
                }</tr>)
            }
        </table>
        <div>
            <a href="/" id={id + '-top'} onClick={otherPage}>Top Page</a>
            <a href="/" id={id + '-prev'} onClick={otherPage}>Prev Page</a>
            <a href="/" id={id + '-next'} onClick={otherPage}>Next Page</a>
            <a href="/" id={id + '-bot'} onClick={otherPage}>Bottom Page</a>
        </div>
    </>
};

export default Table;
