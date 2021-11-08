import React from "react";
import TaipyRendered from "./TaipyRendered";

interface MainPageProps {
    path: string;
}

const MainPage = (props: MainPageProps) => {
    return <>
        <TaipyRendered path={props.path} />
    </>
}

export default MainPage;