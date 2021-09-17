import React, { useState, useEffect, useContext, useCallback, useRef } from "react";

import { TaipyBaseProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";
import { createRequestTableUpdateAction } from "../../context/taipyReducers";
//import { useWhyDidYouUpdate } from "../../utils/hooks";

interface TableProps extends TaipyBaseProps {
    pageSize?: number;
    /* eslint "@typescript-eslint/no-explicit-any": "off", curly: "error" */
    value: Record<string, Record<string, any>>
}

const Table = (props: TableProps) => {
    const { className, id, tp_varname, pageSize = 100 } = props;
    const [value, setValue] = useState<Record<string, Record<string, unknown>>>({});
    const [startIndex, setStartIndex] = useState(0);
    const { dispatch } = useContext(TaipyContext);
    const pageKey = useRef('no-page');

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

    return <>
        <table className={className} id={id}>
            <tbody>
            {
                Object.keys(value).map((rowKey: string) => <tr key={rowKey}><td>{rowKey}</td>{
                    typeof value[rowKey] === 'object' ?
                        Object.keys(value[rowKey]).map((colKey: string) => <td key={colKey}>{value[rowKey][colKey] as string}</td>)
                        :
                        <td>{value[rowKey]}</td>
                }</tr>)
            }
            </tbody>
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
