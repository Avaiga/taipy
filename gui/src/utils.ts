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

import { useDynamicProperty } from "taipy-gui";

// id, is_primary, config_id, creation_date, label, tags, properties(key, value), pipelines(id, label), authorized_tags, deletable
export type ScenarioFull = [
    string,
    boolean,
    string,
    string,
    string,
    string[],
    Array<[string, string]>,
    Array<[string, string]>,
    string[],
    boolean
];

export enum ScFProps {
    id,
    is_primary,
    config_id,
    creation_date,
    label,
    tags,
    properties,
    pipelines,
    authorized_tags,
    deletable,
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

export const MainBoxSx = {
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
        backgroundColor: "background.paper",
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

export const useClassNames = (libClassName?: string, dynamicClassName?: string, className?: string) =>
    ((libClassName || "") + " " + (useDynamicProperty(dynamicClassName, className, undefined) || "")).trim();
