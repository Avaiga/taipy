import React, { useEffect, useReducer, useState, useRef, ComponentType } from "react";
import JsxParser from "react-jsx-parser";
import axios from "axios";
import type {} from '@mui/lab/themeAugmentation';
import { ThemeProvider } from "@mui/material/styles";

import { ENDPOINT } from "./utils";
import { TaipyContext } from "./context/taipyContext";
import { createSetRoutesAction, initializeWebSocket, INITIAL_STATE, taipyInitialize, taipyReducer } from "./context/taipyReducers";
import { JSXReactRouterComponents, JSXRouterBindings } from "./components/Taipy";


const App = () => {
    const [state, dispatch] = useReducer(taipyReducer, INITIAL_STATE, taipyInitialize);
    const [routerJSX, setrouterJSX] = useState("");

    useEffect(() => {
        // Fetch Flask Rendered JSX React Router
        axios
            .get(`${ENDPOINT}/react-router/`)
            .then((result) => {
                setrouterJSX(result.data.router);
                dispatch(createSetRoutesAction(result.data.routes));
            })
            .catch((error) => {
                // Fallback router if there is any error
                setrouterJSX(
                    '<Router><Switch><Route path="/404" exact component={NotFound404} /><Redirect to="/404" /></Switch></Router>'
                );
                console.log(error);
            });
    }, []);

    useEffect(() => {
        initializeWebSocket(state.socket, dispatch);
    }, [state.socket]);

    return (
        <TaipyContext.Provider value={{ state, dispatch }}>
            <ThemeProvider theme={state.theme}>
                <JsxParser disableKeyGeneration={true} bindings={JSXRouterBindings} components={JSXReactRouterComponents as Record<string, ComponentType>} jsx={routerJSX} />
            </ThemeProvider>
        </TaipyContext.Provider>
    );
};

export default App;
