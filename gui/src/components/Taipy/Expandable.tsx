import React, { ReactNode, useCallback, useEffect, useState } from "react";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

import { useDynamicProperty } from "../../utils/hooks";
import { TaipyBaseProps } from "./utils";

interface ExpandableProps extends TaipyBaseProps {
    expanded?: boolean;
    defaultExpanded?: boolean;
    children?: ReactNode;
    title?: string;
    defaultTitle?: string;
}

const Expandable = (props: ExpandableProps) => {
    const { id, expanded = true, defaultExpanded, title, defaultTitle, className } = props;
    const [opened, setOpened] = useState(defaultExpanded === undefined ? expanded : defaultExpanded );
    const active = useDynamicProperty(props.active, props.defaultActive, true);

    useEffect(() => {expanded !== undefined && setOpened(expanded)}, [expanded]);

    const onChange = useCallback(() => setOpened((op) => !op), []);

    return (
        <Accordion expanded={opened} onChange={onChange} className={className} id={id} disabled={!active}>
            {title || defaultTitle ? (
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>{title || defaultTitle}</AccordionSummary>
            ) : null}
            <AccordionDetails>{props.children}</AccordionDetails>
        </Accordion>
    );
};

export default Expandable;
