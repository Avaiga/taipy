/*
 * Copyright 2023 Avaiga Private Limited
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

import React, { useEffect, useReducer, useState, ComponentType } from "react";
import axios from "axios";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/system";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { SnackbarProvider } from "notistack";
import { HelmetProvider } from "react-helmet-async";
import JsxParser from "react-jsx-parser";
import { BrowserRouter } from "react-router-dom";
import { ErrorBoundary } from "react-error-boundary";

import { TaipyContext } from "../context/taipyContext";
import {
    createBlockAction,
    createSetLocationsAction,
    initializeWebSocket,
    INITIAL_STATE,
    retreiveBlockUi,
    taipyInitialize,
    taipyReducer,
} from "../context/taipyReducers";
import { JSXReactRouterComponents } from "./Taipy";
import Alert from "./Taipy/Alert";
import UIBlocker from "./Taipy/UIBlocker";
import Navigate from "./Taipy/Navigate";
import Menu from "./Taipy/Menu";
import GuiDownload from "./Taipy/GuiDownload";
import ErrorFallback from "../utils/ErrorBoundary";

interface AxiosRouter {
    router: string;
    locations: Record<string, string>;
    blockUI: boolean;
}

const mainSx = { flexGrow: 1, bgcolor: "background.default" };
const containerSx = { display: "flex" };
const progressSx = { position: "fixed", bottom: "1em", right: "1em" };

const Router = () => {
    const [state, dispatch] = useReducer(taipyReducer, INITIAL_STATE, taipyInitialize);
    const [JSX, setJSX] = useState("");
    const refresh = !!JSX;
    const themeClass = "taipy-" + state.theme.palette.mode;

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
            .get<AxiosRouter>("/taipy-init", { params: { client_id: state.id || "", v: window.taipyVersion } })
            .then((result) => {
                setJSX(result.data.router);
                dispatch(createSetLocationsAction(result.data.locations));
                result.data.blockUI && dispatch(createBlockAction(retreiveBlockUi()));
            })
            .catch((error) => {
                // Fallback router if there is any error
                setJSX('<Router><Routes><Route path="/*" element={NotFound404} /></Routes></Router>');
                console.log(error);
            });
    }, [refresh, state.isSocketConnected, state.id]);

    useEffect(() => {
        initializeWebSocket(state.socket, dispatch);
    }, [state.socket]);

    return (
        <TaipyContext.Provider value={{ state, dispatch }}>
            <HelmetProvider>
                <ThemeProvider theme={state.theme}>
                    <SnackbarProvider maxSnack={5}>
                        <LocalizationProvider dateAdapter={AdapterDateFns}>
                            <BrowserRouter>
                                <Box style={containerSx} className={themeClass}>
                                    <CssBaseline />
                                    <ErrorBoundary FallbackComponent={ErrorFallback}>
                                        <Menu {...state.menu} />
                                    </ErrorBoundary>
                                    <Box component="main" sx={mainSx}>
                                        <ErrorBoundary FallbackComponent={ErrorFallback}>
                                            <JsxParser
                                                disableKeyGeneration={true}
                                                components={JSXReactRouterComponents as Record<string, ComponentType>}
                                                jsx={JSX}
                                            />
                                        </ErrorBoundary>
                                    </Box>
                                    {state.ackList.length ? (
                                        <Box sx={progressSx}>
                                            <CircularProgress size="1em" disableShrink/>
                                        </Box>
                                    ) : null}
                                </Box>
                                <ErrorBoundary FallbackComponent={ErrorFallback}>
                                    <Alert alert={state.alert} />
                                    <UIBlocker block={state.block} />
                                    <Navigate to={state.navigateTo} tab={state.navigateTab} />
                                    <GuiDownload download={state.download} />
                                </ErrorBoundary>
                            </BrowserRouter>
                        </LocalizationProvider>
                    </SnackbarProvider>
                </ThemeProvider>
            </HelmetProvider>
        </TaipyContext.Provider>
    );
};

export default Router;
