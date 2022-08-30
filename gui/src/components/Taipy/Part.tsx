/*
 * Copyright 2022 Avaiga Private Limited
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

import React, { ReactNode } from "react";
import Box from "@mui/material/Box";

import { useDynamicProperty } from "../../utils/hooks";
import TaipyRendered from "../pages/TaipyRendered";

interface PartProps {
    id?: string;
    className?: string;
    render?: boolean;
    defaultRender?: boolean;
    page?: string;
    children?: ReactNode;
    partial?: boolean;
}

const Part = (props: PartProps) => {
    const {id, className, children, page, partial} = props;
    const render = useDynamicProperty(props.render, props.defaultRender, true);
    return render ? (
        <Box id={id} className={className}>
            {page ? <TaipyRendered path={"/" + page} partial={partial} fromBlock={true} /> : null}
            {children}
        </Box>
    ) : null;
};

export default Part;
