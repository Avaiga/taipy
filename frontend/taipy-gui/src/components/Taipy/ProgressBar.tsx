/*
 * Copyright 2021-2024 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import * as React from "react";
import { useEffect, useState } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import LinearProgress from "@mui/material/LinearProgress";
import Box from "@mui/material/Box";

interface ProgressBarProps {
    linear?: boolean;
    //showProgress?: boolean;
}

const Progress = (props: ProgressBarProps) => {
    const { linear } = props;
    const [value, setValue] = useState(false); //By default the circular element will be rendered. If the user declares the `linear` param as true, then the linear element will be rendered otherwise circular.

    useEffect(() => {
        setValue((val) => {
            if (props.linear !== undefined) return props.linear;
            return val;
        });
    }, [props.linear, linear]);

    return (
        <>
            {value == true ? (
                <Box sx={{ width: "100%" }}>
                    <LinearProgress />
                </Box>
            ) : (
                <Box sx={{ display: "flex" }}>
                    <CircularProgress />
                </Box>
            )}
        </>
    );
};

export default Progress;
