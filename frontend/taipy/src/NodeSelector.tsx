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

import React from "react";
import Box from "@mui/material/Box";

import { CoreProps, MainTreeBoxSx } from "./utils";
import { Cycles, DataNodes, NodeType, Scenarios } from "./utils/types";
import CoreSelector from "./CoreSelector";
import { getComponentClassName, useClassNames } from "taipy-gui";

interface NodeSelectorProps extends CoreProps {
    innerDatanodes?: Cycles | Scenarios | DataNodes;
    onChange?: string;
    error?: string;
    displayCycles: boolean;
    showPrimaryFlag: boolean;
    value?: string;
    defaultValue?: string;
    height: string;
    showPins?: boolean;
    multiple?: boolean;
    updateDnVars?: string;
    filter?: string;
    sort?: string;
    showSearch?: boolean;
}

const NodeSelector = (props: NodeSelectorProps) => {
    const { showPins = true, multiple = false, updateDnVars = "", showSearch = true } = props;
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    return (
        <Box sx={MainTreeBoxSx} id={props.id} className={`${className} ${getComponentClassName(props.children)}`}>
            <CoreSelector
                {...props}
                entities={props.innerDatanodes}
                leafType={NodeType.NODE}
                lovPropertyName="innerDatanodes"
                showPins={showPins}
                multiple={multiple}
                showSearch={showSearch}
                updateCoreVars={updateDnVars}
            />
            <Box>{props.error}</Box>
            {props.children}
        </Box>
    );
};

export default NodeSelector;
