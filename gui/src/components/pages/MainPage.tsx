import React, { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import TaipyRendered from "./TaipyRendered";

interface MainPageProps {
    path: string;
    route: string;
}

const MainPage = (props: MainPageProps) => {
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        if (props.route && location.pathname == "/") {
           navigate(props.route);
        }
    }, [location.pathname, navigate, props.route]);

    return <TaipyRendered path={props.path} />;
};

export default MainPage;
