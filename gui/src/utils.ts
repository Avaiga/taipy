/*
 * Copyright 2023 Avaiga Private Limited
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
import { Theme, alpha } from "@mui/material";
import { PopoverOrigin } from "@mui/material/Popover";

import { useDynamicProperty } from "taipy-gui";

export type ScenarioFull = [
    string,     // id
    boolean,    // is_primary
    string,     // config_id
    string,     // creation_date
    string,     // label
    string[],   // tags
    Array<[string, string]>,    // properties
    Array<[string, string, boolean]>,   // sequences
    string[],   // authorized_tags
    boolean,    // deletable
    boolean,    // promotable
    boolean,    // submittable
    boolean,    // readable
    boolean     // editable
];

export enum ScFProps {
    id,
    is_primary,
    config_id,
    creation_date,
    label,
    tags,
    properties,
    sequences,
    authorized_tags,
    deletable,
    promotable,
    submittable,
    readable,
    editable,
}
export const ScenarioFullLength = Object.keys(ScFProps).length / 2;

export interface ScenarioDict {
    config: string;
    name: string;
    date: string;
    properties: Array<[string, string]>;
}

export const FlagSx = {
    color: "common.white",
    fontSize: "0.75em",
};

export const BadgePos = {
    vertical: "top",
    horizontal: "left",
};

export const BadgeSx = {
    flex: "0 0 auto",

    "& .MuiBadge-badge": {
        fontSize: "1rem",
        width: "1em",
        height: "1em",
        p: 0,
        minWidth: "0",
    },
};

export const MainTreeBoxSx = {
    maxWidth: 300,
    overflowY: "auto",
};

export const BaseTreeViewSx = {
    mb: 2,

    "& .MuiTreeItem-root .MuiTreeItem-content": {
        mb: 0.5,
        py: 1,
        px: 2,
        borderRadius: 0.5,
    },

    "& .MuiTreeItem-iconContainer:empty": {
        display: "none",
    },
    maxHeight: "50vh",
    overflowY: "auto",
};

export const ParentItemSx = {
    "& > .MuiTreeItem-content": {
        ".MuiTreeItem-label": {
            fontWeight: "fontWeightBold",
        },
    },
};

export const tinyIconButtonSx = {
    position: "relative",
    display: "flex",
    width: "1rem",
    height: "1rem",
    fontSize: "0.750rem",

    "&::before": {
        content: "''",
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%,-50%)",
        width: "2rem",
        height: "2rem",
    },

    "& .MuiSvgIcon-root": {
        color: "inherit",
        fontSize: "inherit",
    },
};

export const useClassNames = (libClassName?: string, dynamicClassName?: string, className?: string) =>
    ((libClassName || "") + " " + (useDynamicProperty(dynamicClassName, className, undefined) || "")).trim();

export const disableColor = <T>(color: T, disabled: boolean) => (disabled ? ("disabled" as T) : color);

export const hoverSx = {
    "&:hover": {
        bgcolor: "action.hover",
        cursor: "text",
    },
    mt: 0,
};

export const FieldNoMaxWidth = {
    maxWidth: "none",
};

export const IconPaddingSx = { padding: 0 };

export const MainBoxSx = {};

export const AccordionIconSx = { fontSize: "0.9rem" };

export const AccordionSummarySx = {
    flexDirection: "row-reverse",
    "& .MuiAccordionSummary-expandIconWrapper.Mui-expanded": {
        transform: "rotate(90deg)",
        mr: 1,
    },
    "& .MuiAccordionSummary-content": {
        mr: 1,
    },
};

export const tinySelPinIconButtonSx = (theme: Theme) => ({
    ...tinyIconButtonSx,
    backgroundColor: "secondary.main",
    color: "secondary.contrastText",

    "&:hover": {
        backgroundColor: alpha(theme.palette.secondary.main, 0.75),
        color: "secondary.contrastText",
    },
});

export const popoverOrigin: PopoverOrigin = {
    vertical: "bottom",
    horizontal: "left",
};

export const iconLabelSx = {
    display: "flex",
    alignItems: "center",
    gap: 1,
};

export const tabularHeaderSx = {
    gap: 1,
    alignItems: "center",
    ml: 1,
    pt: 1,
};

export const TableViewType = "table";
export const ChartViewType = "chart";

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
export const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
            width: 250,
        },
    },
};
export const selectSx = { m: 1, width: 300 };
