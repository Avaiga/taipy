import React, { ReactNode, useCallback, useEffect, useState } from "react";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Tooltip from "@mui/material/Tooltip";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

import { useDynamicProperty } from "../../utils/hooks";
import { TaipyActiveProps } from "./utils";
import TaipyRendered from "../pages/TaipyRendered";

interface ExpandableProps extends TaipyActiveProps {
    expanded?: boolean;
    defaultExpanded?: boolean;
    children?: ReactNode;
    title?: string;
    defaultTitle?: string;
    page?: string;
}

const Expandable = (props: ExpandableProps) => {
    const { id, expanded = true, defaultExpanded, title, defaultTitle, className, page } = props;
    const [opened, setOpened] = useState(defaultExpanded === undefined ? expanded : defaultExpanded);

    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    useEffect(() => {
        expanded !== undefined && setOpened(expanded);
    }, [expanded]);

    const onChange = useCallback(() => setOpened((op) => !op), []);

    return (
        <Tooltip title={hover || ""}>
            <Accordion expanded={opened} onChange={onChange} className={className} id={id} disabled={!active}>
                {title || defaultTitle ? (
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>{title || defaultTitle}</AccordionSummary>
                ) : null}
                <AccordionDetails>
                    {page ? <TaipyRendered path={"/" + page} /> : null}
                    {props.children}
                </AccordionDetails>
            </Accordion>
        </Tooltip>
    );
};

export default Expandable;
