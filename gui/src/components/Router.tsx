import React, { useEffect, useReducer, useState, ComponentType } from "react";
import JsxParser from "react-jsx-parser";
import axios from "axios";
import type {} from "@mui/lab/themeAugmentation";
import { ThemeProvider } from "@mui/material/styles";
import { HelmetProvider } from "react-helmet-async";
import AdapterDateFns from "@mui/lab/AdapterDateFns";
import LocalizationProvider from "@mui/lab/LocalizationProvider";
import CssBaseline from "@mui/material/CssBaseline";
import Box from "@mui/material/Box";
import { SnackbarProvider } from "notistack";
import { BrowserRouter } from "react-router-dom";

import { ENDPOINT } from "../utils";
import { TaipyContext } from "../context/taipyContext";
import {
    createBlockAction,
    createSetLocationsAction,
    createThemeAction,
    createTimeZoneAction,
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

interface AxiosRouter {
    router: string;
    darkMode: boolean;
    timeZone: string;
    locations: Record<string, string>;
    blockUI: boolean;
}

const mainSx = { flexGrow: 1, bgcolor: "background.default"};
const containerSx = { display: "flex" };

const Router = () => {
    const [state, dispatch] = useReducer(taipyReducer, INITIAL_STATE, taipyInitialize);
    const [JSX, setJSX] = useState("");
    const refresh = !!JSX;

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
            .get<AxiosRouter>(`${ENDPOINT}/taipy-init/?client_id=${state.id || ""}`)
            .then((result) => {
                setJSX(result.data.router);
                dispatch(createThemeAction(result.data.darkMode, true));
                dispatch(createTimeZoneAction(result.data.timeZone, true));
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
                                <Box style={containerSx}>
                                    <CssBaseline />
                                    <Menu {...state.menu} />
                                    <Box component="main" sx={mainSx}>
                                        <JsxParser
                                            disableKeyGeneration={true}
                                            components={JSXReactRouterComponents as Record<string, ComponentType>}
                                            jsx={JSX}
                                        />
                                    </Box>
                                </Box>
                                <Alert alert={state.alert} />
                                <UIBlocker block={state.block} />
                                <Navigate to={state.to} />
                            </BrowserRouter>
                        </LocalizationProvider>
                    </SnackbarProvider>
                </ThemeProvider>
            </HelmetProvider>
        </TaipyContext.Provider>
    );
};

export default Router;
