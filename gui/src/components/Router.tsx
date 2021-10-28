import React, { useEffect, useReducer, useState, ComponentType } from "react";
import JsxParser from "react-jsx-parser";
import axios from "axios";
import type {} from "@mui/lab/themeAugmentation";
import { ThemeProvider } from "@mui/material/styles";
import { HelmetProvider } from 'react-helmet-async';

import { setDarkMode, ENDPOINT, setTimeZone } from "../utils";
import { TaipyContext } from "../context/taipyContext";
import {
    createSetLocationsAction,
    initializeWebSocket,
    INITIAL_STATE,
    taipyInitialize,
    taipyReducer,
} from "../context/taipyReducers";
import { JSXReactRouterComponents } from "./Taipy";

interface AxiosRouter {
    router: string;
    darkMode: boolean;
    timeZone: string;
    locations: Record<string, string>;
}

const Router = () => {
    const [state, dispatch] = useReducer(taipyReducer, INITIAL_STATE, taipyInitialize);
    const [JSX, setJSX] = useState("");
    const refresh = !!JSX;

    useEffect(() => {
        if (refresh) {
            // no need to access the backend again, the routes are static
            return;
        }
        // Fetch Flask Rendered JSX React Router
        axios
            .get<AxiosRouter>(`${ENDPOINT}/initialize/`)
            .then((result) => {
                setJSX(result.data.router);
                setDarkMode(result.data.darkMode);
                setTimeZone(result.data.timeZone);
                dispatch(createSetLocationsAction(result.data.locations));
            })
            .catch((error) => {
                // Fallback router if there is any error
                setJSX(
                    '<Router><Switch><Route path="/404" exact component={NotFound404} /><Redirect to="/404" /></Switch></Router>'
                );
                console.log(error);
            });
    }, [refresh]);

    useEffect(() => {
        initializeWebSocket(state.socket, dispatch);
    }, [state.socket]);

    return (
        <TaipyContext.Provider value={{ state, dispatch }}>
            <HelmetProvider>
                <ThemeProvider theme={state.theme}>
                    <JsxParser
                        disableKeyGeneration={true}
                        components={JSXReactRouterComponents as Record<string, ComponentType>}
                        jsx={JSX}
                    />
                </ThemeProvider>
            </HelmetProvider>
        </TaipyContext.Provider>
    );
};

export default Router;
