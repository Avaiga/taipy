import React, { ComponentType, useContext, useEffect, useState } from "react";
import axios from "axios";
import { Helmet } from "react-helmet-async";
import JsxParser from "react-jsx-parser";
import { useLocation } from "react-router-dom";
import { ErrorBoundary } from "react-error-boundary";

import { PageContext, TaipyContext } from "../../context/taipyContext";
import { createPartialAction } from "../../context/taipyReducers";
import { getRegisteredComponents } from "../Taipy";
import { renderError, unregisteredRender } from "../Taipy/Unregistered";
import ErrorFallback from "../../utils/ErrorBoundary";
import { emptyArray, getBaseURL } from "../../utils";

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

// Set global style in the traditional way
const setStyle = (id: string, styleString: string): void => {
    let style = document.getElementById(id);
    if (!style || style.tagName !== "STYLE") {
        style = document.createElement("style");
        style.id = `TaiPy_${id}`;
        document.head.appendChild(style);
    }
    style.textContent = styleString || "";
};

interface PageState {
    jsx?: string;
    module?: string;
}

const TaipyRendered = (props: TaipyRenderedProps) => {
    const { partial, fromBlock } = props;
    const location = useLocation();
    const [pageState, setPageState] = useState<PageState>({});
    const [head, setHead] = useState<HeadProps[]>([]);
    const { state, dispatch } = useContext(TaipyContext);

    const baseURL = getBaseURL();
    const pathname = baseURL === "/" ? location.pathname : location.pathname.replace(baseURL, "/");

    const computePath = (): string => {
        if (props.path) return props.path;
        if (state.locations && pathname in state.locations) {
            return state.locations[pathname];
        }
        return pathname;
    };

    const path = computePath();

    useEffect(() => {
        if (partial) {
            dispatch(createPartialAction(path.slice(1), false));
            return;
        }

        const searchParams = new URLSearchParams(location.search);
        const params = Object.fromEntries(searchParams.entries());

        axios
            .get<AxiosRenderer>(`taipy-jsx${path}`, {
                params: { ...params, client_id: state.id || "", v: window.taipyVersion },
            })
            .then((result) => {
                if (typeof result.data.jsx === "string") {
                    setPageState({ module: result.data.context, jsx: result.data.jsx });
                }
                if (!fromBlock) {
                    setStyle("Taipy_style", result.data.style || "");
                    Array.isArray(result.data.head) && setHead(result.data.head);
                }
            })
            .catch((error) => {
                const res = error.response?.data && /<p\sclass=\"errormsg\">([\s\S]*?)<\/p>/gm.exec(error.response?.data);
                setPageState({
                    jsx: `<h1>${res ? res[0] : "Unknown Error"}</h1><h2>No data fetched from backend from ${
                        path === "/TaiPy_root_page" ? baseURL : baseURL + path
                    }</h2><br></br>${res ? "" : error}`,
                });
            });
    }, [path, state.id, dispatch, partial, fromBlock, baseURL, location.search]);

    const headElements = head.map((v, i) =>
        React.createElement(v.tag, { key: `head${i}`, ...v.props }, v.content)
    );

    return (
        <ErrorBoundary FallbackComponent={ErrorFallback}>
            {head.length ? <Helmet>{headElements}</Helmet> : null}
            <PageContext.Provider value={pageState}>
                <JsxParser
                    disableKeyGeneration={true}
                    bindings={state.data}
                    components={getRegisteredComponents() as Record<string, ComponentType>}
                    jsx={pageState.jsx}
                    renderUnrecognized={unregisteredRender}
                    allowUnknownElements={false}
                    renderError={renderError}
                    blacklistedAttrs={emptyArray}
                />
            </PageContext.Provider>
        </ErrorBoundary>
    );
};

export default TaipyRendered;
