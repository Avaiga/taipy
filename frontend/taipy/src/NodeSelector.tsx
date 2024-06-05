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

import { MainTreeBoxSx, useClassNames } from "./utils";
import { Cycles, DataNodes, NodeType, Scenarios } from "./utils/types";
import CoreSelector from "./CoreSelector";

interface NodeSelectorProps {
    id?: string;
    updateVarName?: string;
    innerDatanodes?: Cycles | Scenarios | DataNodes;
    coreChanged?: Record<string, unknown>;
    updateVars: string;
    onChange?: string;
    error?: string;
    displayCycles: boolean;
    showPrimaryFlag: boolean;
    propagate?: boolean;
    value?: string;
    defaultValue?: string;
    height: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
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
        <Box sx={MainTreeBoxSx} id={props.id} className={className}>
            <CoreSelector
                {...props}
                entities={props.innerDatanodes}
                leafType={NodeType.NODE}
                lovPropertyName="datanodes"
                showPins={showPins}
                multiple={multiple}
                showSearch={showSearch}
                updateCoreVars={updateDnVars}
            />
            <Box>{props.error}</Box>
        </Box>
    );
};

export default NodeSelector;
