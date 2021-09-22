import React, { useEffect, useReducer, useState, useRef, ComponentType } from "react";
import JsxParser from "react-jsx-parser";
import axios from "axios";

import { ENDPOINT } from "./utils";
import { TaipyContext } from "./context/taipyContext";
import { initializeWebSocket, INITIAL_STATE, taipyInitialize, taipyReducer } from "./context/taipyReducers";
import { JSXReactRouterComponents, JSXRouterBindings } from "./components/Taipy";


const App = () => {
    const hasMounted = useRef(false);
    const [state, dispatch] = useReducer(taipyReducer, INITIAL_STATE, taipyInitialize);
    const [routerJSX, setrouterJSX] = useState("");

    useEffect(() => {
        // Fetch Flask Rendered JSX React Router
        axios
            .get(`${ENDPOINT}/react-router/`)
            .then((result) => {
                if (!hasMounted.current) {
                    setrouterJSX(result.data.router);
                }
            })
            .catch((error) => {
                // Fallback router if there is any error
                setrouterJSX(
                    '<Router><Switch><Route path="/404" exact component={NotFound404} /><Redirect to="/404" /></Switch></Router>'
                );
                console.log(error);
            });
        return () => {
            hasMounted.current = true;
        };
    }, []);

    useEffect(() => {
        initializeWebSocket(state.socket, dispatch);
    }, [state.socket]);

    return (
        <TaipyContext.Provider value={{ state, dispatch }}>
            <JsxParser disableKeyGeneration={true} bindings={JSXRouterBindings} components={JSXReactRouterComponents as Record<string, ComponentType>} jsx={routerJSX} />
        </TaipyContext.Provider>
    );
};

export default App;
