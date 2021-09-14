import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import JsxParser from "react-jsx-parser";
import { useLocation } from "react-router-dom";

import { setStyle, setDarkMode, ENDPOINT } from "../../utils";
import { TaipyContext } from "../../context/taipyContext";
import { taipyComponents } from "../Taipy";

const TaipyRendered = () => {
    const location = useLocation();
    const [templateJSX, setTemplateJSX] = useState("");
    const { state } = useContext(TaipyContext);
    useEffect(() => {
        // Fetch JSX Flask Backend Render
        axios
            .get(`${ENDPOINT}/flask-jsx${location.pathname}`)
            .then((result) => {
                // set rendered JSX and CSS style from fetch result
                setTemplateJSX(result.data.jsx);
                setStyle(result.data.style);
                setDarkMode(result.data.darkMode);
            })
            .catch((error) => setTemplateJSX("<h1>No data fetched from backend</h1><br></br>" + error));
    }, [location.pathname]);

    return <JsxParser disableKeyGeneration={true} bindings={state.data} components={taipyComponents} jsx={templateJSX} />;
};

export default TaipyRendered;
