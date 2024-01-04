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

import React, { ReactNode, useCallback, useEffect, useState } from "react";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Tooltip from "@mui/material/Tooltip";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";
import { TaipyActiveProps, TaipyChangeProps, getUpdateVar } from "./utils";
import TaipyRendered from "../pages/TaipyRendered";
import { createSendUpdateAction } from "../../context/taipyReducers";

interface ExpandableProps extends TaipyActiveProps, TaipyChangeProps {
    expanded?: boolean;
    defaultExpanded?: boolean;
    children?: ReactNode;
    title?: string;
    defaultTitle?: string;
    page?: string;
    partial?: boolean;
}

const Expandable = (props: ExpandableProps) => {
    const { id, expanded, defaultExpanded, title, defaultTitle, page, partial, updateVars, propagate = true } = props;
    const dispatch = useDispatch();
    const [opened, setOpened] = useState(
        defaultExpanded === undefined ? (expanded === undefined ? true : expanded) : defaultExpanded
    );
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    useEffect(() => {
        expanded !== undefined && setOpened(expanded);
    }, [expanded]);

    const onChange = useCallback(
        (_: React.SyntheticEvent<Element, Event>, expanded: boolean) => {
            setOpened(expanded);
            if (updateVars) {
                const expandedVar = getUpdateVar(updateVars, "expanded");
                expandedVar && dispatch(createSendUpdateAction(expandedVar, expanded, module, props.onChange, propagate));
            }
        },
        [dispatch, props.onChange, propagate, updateVars, module]
    );

    return (
        <Tooltip title={hover || ""}>
            <Accordion expanded={opened} onChange={onChange} className={className} id={id} disabled={!active}>
                {title || defaultTitle ? (
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>{title || defaultTitle}</AccordionSummary>
                ) : null}
                <AccordionDetails>
                    {page ? <TaipyRendered path={"/" + page} partial={partial} fromBlock={true} /> : null}
                    {props.children}
                </AccordionDetails>
            </Accordion>
        </Tooltip>
    );
};

export default Expandable;
