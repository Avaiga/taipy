import React from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";

interface ErrorFallBackProps {
    error: Error;
    resetErrorBoundary: () => void;
}

const ErrorFallback = (props: ErrorFallBackProps) => (
    <Box sx={{ backgroundColor: "error.main" }}>
        <Box>Something went wrong ...</Box>
        <Box>{(props.error as Error).message}</Box>
        <Button onClick={props.resetErrorBoundary}>Try again</Button>
    </Box>
);

export default ErrorFallback;