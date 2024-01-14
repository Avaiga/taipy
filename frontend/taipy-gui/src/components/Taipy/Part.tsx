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

import React, { ReactNode, useContext, useMemo } from "react";
import Box from "@mui/material/Box";

import { useClassNames, useDynamicProperty } from "../../utils/hooks";
import TaipyRendered from "../pages/TaipyRendered";
import { TaipyBaseProps } from "./utils";
import { TaipyContext } from "../../context/taipyContext";

interface PartProps extends TaipyBaseProps {
    render?: boolean;
    defaultRender?: boolean;
    page?: string;
    defaultPage?: string;
    children?: ReactNode;
    defaultPartial?: boolean;
    partial?: boolean;
    height?: string;
    defaultHeight?: string;
}

const IframeStyle = {
    width: "100%",
    height: "100%",
};

const Part = (props: PartProps) => {
    const { id, children, partial, defaultPartial } = props;
    const { state } = useContext(TaipyContext);

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const render = useDynamicProperty(props.render, props.defaultRender, true);
    const height = useDynamicProperty(props.height, props.defaultHeight, undefined);
    const page = useDynamicProperty(props.page, props.defaultPage, "");
    const iFrame = useMemo(() => {
        if (page && !defaultPartial) {
            if (/^https?\:\/\//.test(page)) {
                return true;
            }
            const sPage = "/" + page;
            return !Object.keys(state.locations || {}).some((route) => sPage === route);
        }
        return false;
    }, [state.locations, page, defaultPartial]);

    const boxSx = useMemo(() => (height ? { height: height } : undefined), [height]);
    return render ? (
        <Box id={id} className={className} sx={boxSx}>
            {iFrame ? (
                <iframe src={page} style={IframeStyle} />
            ) : page ? (
                <TaipyRendered path={"/" + page} partial={partial} fromBlock={true} />
            ) : null}
            {children}
        </Box>
    ) : null;
};

export default Part;
