import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import JsxParser from "react-jsx-parser";
import { useLocation } from "react-router-dom";

import { setStyle, setDarkMode, ENDPOINT, setTimezone } from "../../utils";
import { TaipyContext } from "../../context/taipyContext";
import { taipyComponents } from "../Taipy";

const TaipyRendered = () => {
    const location = useLocation();
    const [JSX, setJSX] = useState("");
    const { state } = useContext(TaipyContext);

    const path = (state.locations && state.locations[location.pathname]) || location.pathname;

    useEffect(() => {
        // Fetch JSX Flask Backend Render
        axios
            .get(`${ENDPOINT}/flask-jsx${path}`)
            .then((result) => {
                // set rendered JSX and CSS style from fetch result
                setJSX(result.data.jsx);
                setStyle(result.data.style);
                setDarkMode(result.data.darkMode);
                setTimezone(result.data.timezone);
            })
            .catch((error) => setJSX("<h1>No data fetched from backend</h1><br></br>" + error));
    }, [path]);

    return <JsxParser disableKeyGeneration={true} bindings={state.data} components={taipyComponents} jsx={JSX} />;
};

export default TaipyRendered;
