import React from "react";
import Typography from "@mui/material/Typography";
import { useLocation } from "react-router";

const NotFound404 = () => {
    const location = useLocation();
    return <Typography variant="h1">{location.pathname} Not Found!</Typography>;
}

export default NotFound404;
