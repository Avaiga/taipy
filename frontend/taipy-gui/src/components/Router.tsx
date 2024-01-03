/*
 * Copyright 2021-2024 Avaiga Private Limited
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

import React, { useEffect, useReducer, useState } from "react";
import axios from "axios";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/system";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { SnackbarProvider } from "notistack";
import { HelmetProvider } from "react-helmet-async";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ErrorBoundary } from "react-error-boundary";

import { PageContext, TaipyContext } from "../context/taipyContext";
import {
    createBlockAction,
    createSetLocationsAction,
    initializeWebSocket,
    INITIAL_STATE,
    retreiveBlockUi,
    taipyInitialize,
    taipyReducer,
} from "../context/taipyReducers";
import Alert from "./Taipy/Alert";
import UIBlocker from "./Taipy/UIBlocker";
import Navigate from "./Taipy/Navigate";
import Menu from "./Taipy/Menu";
import GuiDownload from "./Taipy/GuiDownload";
import ErrorFallback from "../utils/ErrorBoundary";
import MainPage from "./pages/MainPage";
import TaipyRendered from "./pages/TaipyRendered";
import NotFound404 from "./pages/NotFound404";
import { getBaseURL } from "../utils";

interface AxiosRouter {
    router: string;
    locations: Record<string, string>;
    blockUI: boolean;
}

const mainSx = { flexGrow: 1, bgcolor: "background.default" };
const containerSx = { display: "flex" };
const progressSx = { position: "fixed", bottom: "1em", right: "1em" };
const pageStore = {};

const Router = () => {
    const [state, dispatch] = useReducer(taipyReducer, INITIAL_STATE, taipyInitialize);
    const [routes, setRoutes] = useState<Record<string, string>>({});
    const refresh = !!Object.keys(routes).length;
    const themeClass = "taipy-" + state.theme.palette.mode;
    const baseURL = getBaseURL();

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
            .get<AxiosRouter>("taipy-init", { params: { client_id: state.id || "", v: window.taipyVersion } })
            .then((result) => {
                dispatch(createSetLocationsAction(result.data.locations));
                setRoutes(result.data.locations);
                result.data.blockUI && dispatch(createBlockAction(retreiveBlockUi()));
            })
            .catch((error) => {
                // Fallback router if there is any error
                setRoutes({ "/": "/TaiPy_root_page" });
                console.log(error);
            });
    }, [refresh, state.isSocketConnected, state.id]);

    useEffect(() => {
        initializeWebSocket(state.socket, dispatch);
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

    return (
        <TaipyContext.Provider value={{ state, dispatch }}>
            <HelmetProvider>
                <ThemeProvider theme={state.theme}>
                    <SnackbarProvider maxSnack={5}>
                        <LocalizationProvider dateAdapter={AdapterDateFns}>
                            <PageContext.Provider value={pageStore}>
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
                                                                        (path) => path !== "/"
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
                                                            <Route path="*" key="NotFound" element={<NotFound404 />} />
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
                                        <Alert alerts={state.alerts} />
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
                            </PageContext.Provider>
                        </LocalizationProvider>
                    </SnackbarProvider>
                </ThemeProvider>
            </HelmetProvider>
        </TaipyContext.Provider>
    );
};

export default Router;
