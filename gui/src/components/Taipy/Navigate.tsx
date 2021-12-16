import React, { useContext, useEffect } from "react";
import { Navigate as RouterNavigate } from "react-router-dom";
import { TaipyContext } from "../../context/taipyContext";
import { createNavigateAction } from "../../context/taipyReducers";

interface NavigateProps {
    to?: string;
}

const Navigate = ({ to }: NavigateProps) => {
    const { dispatch} =useContext(TaipyContext);

    useEffect(() => {
        to && dispatch(createNavigateAction())
    }, [to, dispatch]);

    return (to ? <RouterNavigate to={"/"+to} /> : null)};

export default Navigate;
