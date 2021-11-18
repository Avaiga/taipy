import React, { ReactNode, useCallback, useState } from "react";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

import { useDynamicProperty } from "../../utils/hooks";
import { TaipyBaseProps } from "./utils";

interface ExpandableProps extends TaipyBaseProps {
    expanded?: boolean;
    children?: ReactNode;
    value?: string;
}

const Expandable = (props: ExpandableProps) => {
    const { id, expanded = true, value, defaultValue, className } = props;
    const [opened, setOpened] = useState(expanded);
    const active = useDynamicProperty(props.active, props.defaultActive, true);

    const onChange = useCallback(() => setOpened((op) => !op), []);
    return (
        <Accordion expanded={opened} onChange={onChange} className={className} id={id} disabled={!active}>
            {value || defaultValue ? (
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>{value || defaultValue}</AccordionSummary>
            ) : null}
            <AccordionDetails>{props.children}</AccordionDetails>
        </Accordion>
    );
};

export default Expandable;
