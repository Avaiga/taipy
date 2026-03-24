/*
 * Copyright 2021-2025 Avaiga Private Limited
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

import React, { useContext, useEffect, useMemo, useState } from "react";
import axios from "axios";
import { ErrorBoundary } from "react-error-boundary";
import { Helmet } from "react-helmet-async";
import { useLocation } from "react-router";

import { PageContext, TaipyContext } from "../../context/taipyContext";
import { createPartialAction } from "../../context/taipyReducers";
import ErrorFallback from "../../utils/ErrorBoundary";
import { getRegisteredComponents } from "../Taipy/components";
import { parseJSX } from "../../jsx/parser";

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
    scriptPaths: string[];
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

// set script tag for the page
const setScript = (id: string, scriptPaths: string[]): void => {
    document.querySelectorAll(`script[id^="${id}_"]`).forEach((script) => script.remove());
    scriptPaths.forEach((path, index) => {
        const script = document.createElement("script");
        script.id = `${id}_${index}`;
        script.src = path;
        script.defer = true;
        document.head.append(script);
    });
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
    const { state, dispatch, serverUrl, config } = useContext(TaipyContext);

    const baseURL = config?.baseURL || "/";
    const pathname = baseURL == "/" ? location.pathname : location.pathname.replace(baseURL, "/");
    const path =
        props.path || (state.locations && pathname in state.locations && state.locations[pathname]) || pathname;

    useEffect(() => {
        // Fetch JSX Flask Backend Render
        if (partial) {
            dispatch(createPartialAction(path.slice(1), false));
        } else {
            const searchParams = new URLSearchParams(location.search);
            const params = Object.fromEntries(searchParams.entries());
            axios
                .get<AxiosRenderer>(serverUrl ? `${serverUrl}${baseURL}taipy-jsx${path}` : `taipy-jsx${path}`, {
                    params: { ...params, client_id: state.id || "", v: config?.version },
                })
                .then((result) => {
                    // set rendered JSX and CSS style from fetch result
                    if (typeof result.data.jsx === "string") {
                        setPageState({ module: result.data.context, jsx: result.data.jsx });
                    }
                    if (!fromBlock) {
                        setStyle(
                            path == "/TaiPy_root_page" ? "Taipy_root_style" : "Taipy_style",
                            result.data.style || ""
                        );
                        Array.isArray(result.data.head) && setHead(result.data.head);
                        Array.isArray(result.data.scriptPaths) && setScript("Taipy_script", result.data.scriptPaths);
                    }
                })
                .catch((error) => {
                    const res =
                        error.response?.data && /<p\sclass=\"errormsg\">([\s\S]*?)<\/p>/gm.exec(error.response?.data);
                    setPageState({
                        jsx: `<h1>${res ? res[0].replace("<br>", "<br/>") : "Unknown Error"}</h1><h2>No data fetched from backend from ${
                            path === "/TaiPy_root_page" ? baseURL : baseURL + path
                        }</h2><br/>${res && res[0] ? "" : error}`,
                    });
                });
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [path, state.id, dispatch, partial, fromBlock, baseURL, config?.version, serverUrl]);

    const tree = useMemo(() => parseJSX(pageState.jsx || "", state.data, getRegisteredComponents(config?.extensions)), [pageState.jsx, state.data, config?.extensions]);

    return (
        <ErrorBoundary FallbackComponent={ErrorFallback}>
            {head.length ? (
                <Helmet>
                    {head.map((v, i) => React.createElement(v.tag, { key: `head${i}`, ...v.props }, v.content))}
                </Helmet>
            ) : null}
            <PageContext.Provider value={pageState}>
                {/* <JsxParser
                    disableKeyGeneration={true}
                    bindings={state.data}
                    components={components}
                    jsx={pageState.jsx}
                    renderUnrecognized={unregisteredRender}
                    allowUnknownElements={false}
                    renderError={renderError}
                    blacklistedAttrs={emptyArray}
                /> */}
                {tree}
            </PageContext.Provider>
        </ErrorBoundary>
    );
};

export default TaipyRendered;
