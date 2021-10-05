import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import JsxParser from "react-jsx-parser";
import { useLocation } from "react-router-dom";

import { setStyle, ENDPOINT } from "../../utils";
import { TaipyContext } from "../../context/taipyContext";
import { taipyComponents } from "../Taipy";
import { unregisteredRender, renderError } from "../Taipy/Unregistered";

interface TaipyRenderedProps {
    path?: string;
}

const TaipyRendered = (props: TaipyRenderedProps) => {
    const location = useLocation();
    const [JSX, setJSX] = useState("");
    const { state } = useContext(TaipyContext);

    const path = props.path || (state.locations && state.locations[location.pathname]) || location.pathname;

    useEffect(() => {
        // Fetch JSX Flask Backend Render
        axios
            .get(`${ENDPOINT}/flask-jsx${path}`)
            .then((result) => {
                // set rendered JSX and CSS style from fetch result
                result?.data?.jsx && setJSX(result.data.jsx);
                result?.data?.style && setStyle(result.data.style);
            })
            .catch((error) => setJSX(`<h1>No data fetched from backend from ${path}</h1><br></br>${error}`));
    }, [path]);

    return (
        <JsxParser
            disableKeyGeneration={true}
            bindings={state.data}
            components={taipyComponents}
            jsx={JSX}
            renderUnrecognized={unregisteredRender}
            allowUnknownElements={false}
            renderError={renderError}
        />
    );
};

export default TaipyRendered;
