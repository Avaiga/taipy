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

import React, { useCallback, useEffect, useMemo, useReducer, useState } from "react";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import CssBaseline from "@mui/material/CssBaseline";
import Typography from "@mui/material/Typography";
import { ThemeProvider } from "@mui/system";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import axios from "axios";
import { MathJaxContext } from "better-react-mathjax";
import { SnackbarProvider } from "notistack";
import { HelmetProvider } from "react-helmet-async";
import { BrowserRouter, Route, Routes } from "react-router";
import { ErrorBoundary } from "react-error-boundary";

import { PageContext, TaipyContext, TaipyStore } from "../context/taipyContext";
import {
    createBlockAction,
    createSetLocationsAction,
    initializeWebSocket,
    INITIAL_STATE,
    retrieveBlockUi,
    taipyInitialize,
    taipyReducer,
    createSendUpdateAction,
    OnAction,
    createCleanAckListAction,
    shutdownWebSocket,
} from "../context/taipyReducers";
import { TaipyConfig } from "../utils";
import ErrorFallback from "../utils/ErrorBoundary";
import UIBlocker from "./Taipy/UIBlocker";
import Navigate from "./Taipy/Navigate";
import Menu from "./Taipy/Menu";
import TaipyNotification from "./Taipy/Notification";
import GuiDownload from "./Taipy/GuiDownload";
import MainPage from "./pages/MainPage";
import TaipyRendered from "./pages/TaipyRendered";
import NotFound404 from "./pages/NotFound404";
import { useLocalStorageWithEvent } from "../hooks";

interface AxiosRouter {
    router: string;
    locations: Record<string, string>;
    blockUI: boolean;
}

const mainSx = { flexGrow: 1, bgcolor: "background.default" };
const containerSx = { display: "flex" };
const progressSx = { position: "fixed", bottom: "1em", right: "1em" };
const pageStore = {};
const mathJaxConfig = {
    tex: {
        inlineMath: [
            ["$", "$"],
            ["\\(", "\\)"],
        ],
        displayMath: [
            ["$$", "$$"],
            ["\\[", "\\]"],
        ],
    },
    asyncLoad: true,
};

interface RouterProps {
    serverUrl?: string;
    config?: TaipyConfig;
    state?: Record<string, unknown>;
    onAction?: OnAction;
}

const Router = ({ serverUrl, config = window.taipyConfig!, state: stateChanges, onAction }: RouterProps) => {
    const [taipyConfig, setTaipyConfig] = useState<TaipyConfig>(config);
    const [state, dispatch] = useReducer(taipyReducer, INITIAL_STATE, (state) =>
        taipyInitialize(state, taipyConfig, serverUrl, onAction),
    );
    const [routes, setRoutes] = useState<Record<string, string>>({});
    const ackTimerRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);
    const refresh = !!Object.keys(routes).length;
    const themeClass = "taipy-" + state.theme.palette.mode;
    const baseURL = taipyConfig?.baseURL || "/";

    useLocalStorageWithEvent(dispatch, state.id);

    useEffect(() => {
        if (refresh) {
            // no need to access the backend again, the routes are static
            return;
        }
        if (!state.isSocketConnected) {
            // initialize only when there is an existing ws connection
            // --> assuring that there is a session data scope on the backend
            return;
        }
        // Fetch Flask Rendered JSX React Router
        axios
            .get<AxiosRouter>(serverUrl ? `${serverUrl}${baseURL}taipy-init` : "taipy-init", {
                params: { client_id: state.id || "", v: taipyConfig?.version },
            })
            .then((result) => {
                dispatch(createSetLocationsAction(result.data.locations));
                setRoutes(result.data.locations);
                result.data.blockUI && dispatch(createBlockAction(retrieveBlockUi()));
            })
            .catch((error) => {
                // Fallback router if there is any error
                setRoutes({ "/": "/TaiPy_root_page" });
                console.error(error);
            });
    }, [refresh, state.isSocketConnected, state.id, serverUrl, baseURL, taipyConfig?.version]);

    useEffect(() => {
        const socket = state.socket;
        initializeWebSocket(socket, dispatch);
        return () => shutdownWebSocket(socket);
    }, [state.socket]);

    useEffect(() => {
        const classes = [themeClass];
        document.body.classList.forEach((cls) => {
            if (!cls.startsWith("taipy-")) {
                classes.push(cls);
            }
        });
        document.body.className = classes.join(" ");
    }, [themeClass]);

    useEffect(() => {
        if (stateChanges) {
            Object.entries(stateChanges).forEach(([key, value]) => {
                dispatch(createSendUpdateAction(key, value, undefined));
            });
        }
    }, [stateChanges]);

    const onScriptLoad = useCallback(
        (name: string) => {
            const extension = taipyConfig.extensions?.[name];
            if (extension && !extension.loaded) {
                extension.loaded = true;
                console.debug("Extension script '", name, "' is loaded.");
                setTaipyConfig({ ...taipyConfig });
            }
        },
        [taipyConfig],
    );

    const contextStore = useMemo<TaipyStore>(
        () => ({ state, dispatch, serverUrl, config: taipyConfig }),
        [state, dispatch, serverUrl, taipyConfig],
    );

    const style = useMemo(() => {
        const styles = [];
        if (taipyConfig?.rootMargin) {
            styles.push(`#root{margin:${taipyConfig.rootMargin};}`);
        }
        styles.push(".__tgb_inline{display:inline-block;}");
        if (taipyConfig?.waterMark) {
            styles.push(
                ".__tp_watermark{position:fixed;bottom:1em;opacity:0.4;color:gray;left:50%;transform:translateX(-50%);font-size:0.7em;}",
            );
        }
        if (taipyConfig?.cssVars) {
            styles.push(`:root{${taipyConfig.cssVars}}`);
        }
        return styles.join("");
    }, [taipyConfig?.rootMargin, taipyConfig?.waterMark, taipyConfig?.cssVars]);

    useEffect(() => {
        setTaipyConfig((config) => {
            if (config) {
                let found = false;
                config.extensions &&
                    Object.entries(config.extensions)
                        .filter(([name, extension]) => !extension.loaded && (serverUrl || !name))
                        .forEach(([, extension]) => {
                            found = true;
                            extension.loaded = true;
                        });
                return found ? { ...config, extensions: { ...config.extensions } } : config;
            }
            return config;
        });
        Object.entries(taipyConfig?.extensions || {})
            .filter(([name, extension]) => !extension.loaded && (!serverUrl || !name))
            .forEach(([name, extension]) => {
                extension.scripts?.forEach((src) => {
                    const id = `taipy-${name}-${src}`;
                    if (document.getElementById(id)) {
                        return;
                    }
                    const extensionScript = document.createElement("script");
                    extensionScript.type = "text/javascript";
                    extensionScript.id = id;
                    extensionScript.src = src;
                    extensionScript.defer = true;
                    name && (extensionScript.onload = () => onScriptLoad(name));
                    extensionScript.onerror = console.error;
                    document.head.appendChild(extensionScript);
                });
            });
    }, [serverUrl, baseURL, taipyConfig?.extensions, onScriptLoad]);

    useEffect(() => {
        if (ackTimerRef.current) {
            clearTimeout(ackTimerRef.current);
            ackTimerRef.current = null;
        }
        if (state.ackList.length) {
            // set a timeout on the last acknowledgement received to clear the ack list
            ackTimerRef.current = setTimeout(() => {
                dispatch(createCleanAckListAction());
            }, 20000);
        }
        return () => {
            if (ackTimerRef.current) {
                clearTimeout(ackTimerRef.current);
                ackTimerRef.current = null;
            }
        };
    }, [state.ackList.length]);

    return taipyConfig ? (
        <TaipyContext.Provider value={contextStore}>
            <style href="taipy-style" precedence="medium">
                {style}
            </style>

            <>
                {Object.values(taipyConfig?.extensions || {})
                    .flatMap((ext) => ext.styles)
                    .filter((src) => !!src)
                    .map((src, idx) => (
                        <link
                            key={idx}
                            rel="stylesheet"
                            href={serverUrl && !src?.startsWith("http") ? `${serverUrl}${baseURL}${src}` : src}
                        />
                    ))}
                <HelmetProvider>
                    <ThemeProvider theme={state.theme}>
                        <SnackbarProvider maxSnack={5}>
                            <LocalizationProvider dateAdapter={AdapterDateFns}>
                                <PageContext.Provider value={pageStore}>
                                    <MathJaxContext config={mathJaxConfig}>
                                        <BrowserRouter>
                                            <Box style={containerSx}>
                                                <CssBaseline />
                                                <ErrorBoundary FallbackComponent={ErrorFallback}>
                                                    <Menu {...state.menu} />
                                                </ErrorBoundary>
                                                <Box component="main" sx={mainSx}>
                                                    <ErrorBoundary FallbackComponent={ErrorFallback}>
                                                        {Object.keys(routes).length ? (
                                                            <Routes>
                                                                <Route
                                                                    path={baseURL}
                                                                    element={
                                                                        <MainPage
                                                                            path={routes["/"]}
                                                                            route={Object.keys(routes).find(
                                                                                (path) => path !== "/",
                                                                            )}
                                                                        />
                                                                    }
                                                                >
                                                                    {Object.entries(routes)
                                                                        .filter(([path]) => path !== "/")
                                                                        .map(([path, name]) => (
                                                                            <Route
                                                                                key={name}
                                                                                path={path.substring(1)}
                                                                                element={<TaipyRendered />}
                                                                            />
                                                                        ))}
                                                                    <Route
                                                                        path="*"
                                                                        key="NotFound"
                                                                        element={<NotFound404 />}
                                                                    />
                                                                </Route>
                                                            </Routes>
                                                        ) : null}
                                                    </ErrorBoundary>
                                                </Box>
                                                {state.ackList.length ? (
                                                    <Box sx={progressSx} className="taipy-busy">
                                                        <CircularProgress size="1em" disableShrink />
                                                    </Box>
                                                ) : null}
                                            </Box>
                                            <ErrorBoundary FallbackComponent={ErrorFallback}>
                                                <TaipyNotification notifications={state.notifications} />
                                                <UIBlocker block={state.block} />
                                                <Navigate
                                                    to={state.navigateTo}
                                                    params={state.navigateParams}
                                                    tab={state.navigateTab}
                                                    force={state.navigateForce}
                                                />
                                                <GuiDownload download={state.download} />
                                            </ErrorBoundary>
                                        </BrowserRouter>
                                    </MathJaxContext>
                                </PageContext.Provider>
                            </LocalizationProvider>
                        </SnackbarProvider>
                    </ThemeProvider>
                </HelmetProvider>
                {config?.waterMark ? <span className="taipy-watermark __tp_watermark">{config.waterMark}</span> : null}
            </>
        </TaipyContext.Provider>
    ) : (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
            <Typography color="error">Taipy is not configured properly (check Taipy configuration)</Typography>
        </Box>
    );
};

export default Router;
