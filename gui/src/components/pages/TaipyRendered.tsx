import React, { useEffect, useState, useContext, ComponentType } from "react";
import axios from "axios";
import JsxParser from "react-jsx-parser";
import { useLocation } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { ErrorBoundary } from "react-error-boundary";

import { TaipyContext } from "../../context/taipyContext";
import { getRegisteredComponents } from "../Taipy";
import { unregisteredRender, renderError } from "../Taipy/Unregistered";
import { createModuleContextAction, createPartialAction } from "../../context/taipyReducers";
import ErrorFallback from "../../utils/ErrorBoundary";

interface TaipyRenderedProps {
    path?: string;
    partial?: boolean;
    fromBlock?: boolean;
}

interface HeadProps {
    tag: string;
    props: Record<string, string>;
    content: string;
}

interface AxiosRenderer {
    jsx: string;
    style: string;
    head: HeadProps[];
    context: string;
}

// set global style the traditional way
const setStyle = (id: string, styleString: string): void => {
    let style = document.getElementById(id);
    if (style && style.tagName !== "STYLE") {
        style = null;
        id = "TaiPy_" + id;
    }
    if (!style && styleString) {
        style = document.createElement("style");
        style.id = id;
        document.head.append(style);
    }
    if (style) {
        style.textContent = styleString;
    }
};


const TaipyRendered = (props: TaipyRenderedProps) => {
    const {partial, fromBlock} = props;
    const location = useLocation();
    const [JSX, setJSX] = useState("");
    const [head, setHead] = useState<HeadProps[]>([]);
    const { state, dispatch } = useContext(TaipyContext);

    const path = props.path || (state.locations && state.locations[location.pathname]) || location.pathname;

    useEffect(() => {
        // Fetch JSX Flask Backend Render
        if (partial) {
            dispatch(createPartialAction(path.slice(1), false));
        } else {
            axios
            .get<AxiosRenderer>(`/taipy-jsx${path}`, {params: {client_id: state.id || "", v: window.taipyVersion}})
            .then((result) => {
                // set rendered JSX and CSS style from fetch result
                typeof result.data.jsx === "string" && setJSX(result.data.jsx);
                if (!fromBlock) {
                    setStyle("Taipy_style", result.data.style || "");
                    result.data.head && setHead(result.data.head);
                }
                dispatch(createModuleContextAction(result.data.context));
            })
            .catch((error) => setJSX(`<h1>No data fetched from backend from ${path}</h1><br></br>${error}`));
        }
    }, [path, state.id, dispatch, partial, fromBlock]);

    return (
        <ErrorBoundary FallbackComponent={ErrorFallback}>
            {head.length ? <Helmet>{head.map((v) => React.createElement(v.tag, v.props, v.content))}</Helmet> : null}
            <JsxParser
                disableKeyGeneration={true}
                bindings={state.data}
                components={getRegisteredComponents() as Record<string, ComponentType>}
                jsx={JSX}
                renderUnrecognized={unregisteredRender}
                allowUnknownElements={false}
                renderError={renderError}
            />
        </ErrorBoundary>
    );
};

export default TaipyRendered;
