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

import React, { CSSProperties, useMemo, MouseEvent } from "react";
import Avatar from "@mui/material/Avatar";
import CardHeader from "@mui/material/CardHeader";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import Tooltip from "@mui/material/Tooltip";
import { TypographyProps } from "@mui/material";
import { SxProps } from "@mui/system";

import { TaipyActiveProps, TaipyChangeProps, TaipyLabelProps } from "./utils";
import { getInitials } from "../../utils";
import { LovItem } from "../../utils/lov";
import { stringIcon, Icon, IconAvatar, avatarSx } from "../../utils/icon";

export interface SelTreeProps extends LovProps, TaipyLabelProps {
    filter?: boolean;
    multiple?: boolean;
    width?: string | number;
    dropdown?: boolean;
}

export interface LovProps<T = string | string[], U = string> extends TaipyActiveProps, TaipyChangeProps {
    defaultLov?: string;
    lov?: LoV;
    value?: T;
    defaultValue?: U;
    height?: string | number;
    valueById?: boolean;
}

/**
 * A LoV (list of value) element.
 *
 * Each `LoVElt` holds:
 *
 * - Its identifier as a string;
 * - Its label (or icon) as a `stringIcon`;
 * - Potential child elements as an array of `LoVElt`s.
 */
export type LoVElt = [string, stringIcon, LoVElt[]?];

/**
 * A series of LoV elements.
 */
export type LoV = LoVElt[];

const getLovItem = (elt: LoVElt | string, tree = false): LovItem => {
    const it: LovItem = Array.isArray(elt)
        ? {
              id: elt[0],
              item: elt[1] || elt[0],
          }
        : { id: "" + elt, item: "" + elt };
    if (tree) {
        it.children = Array.isArray(elt) && elt.length > 2 ? elt[2]?.map((e) => getLovItem(e, true)) : [];
    }
    return it;
};

export const paperBaseSx = { width: "100%", mb: 2, display: "grid", gridTemplateRows: "auto 1fr" } as CSSProperties;

/**
 * A React hook that returns a LoV list from the LoV default value and the LoV bound value.
 * @param lov - The bound lov value.
 * @param defaultLov - The JSON-stringified default LoV value.
 * @param tree - This flag indicates if the LoV list is a tree or a flat list (default is false).
 * @returns A list of LoV items.
 */
export const useLovListMemo = (lov: LoV | undefined, defaultLov: string, tree = false): LovItem[] =>
    useMemo(() => {
        if (lov) {
            if (!Array.isArray(lov)) {
                console.debug("lov wrong format ", lov);
                return [];
            }
            return lov.map((elt) => getLovItem(elt, tree));
        } else if (defaultLov) {
            let parsedLov;
            try {
                parsedLov = JSON.parse(defaultLov);
            } catch (e) {
                parsedLov = [];
            }
            return parsedLov.map((elt: LoVElt) => getLovItem(elt, tree));
        }
        return [];
    }, [lov, defaultLov, tree]);

const cardSx = { p: 0 } as CSSProperties;

export const LovImage = ({
    item,
    disableTypo,
    height,
    titleTypographyProps,
}: {
    item: Icon;
    disableTypo?: boolean;
    height?: string;
    titleTypographyProps?: TypographyProps<"span", { component?: "span"; }>;
}) => {
    const sx = useMemo(
        () => (height ? { height: height, "& .MuiAvatar-img": { objectFit: "contain" } } : undefined) as SxProps,
        [height]
    );
    return (
        <CardHeader
            sx={cardSx}
            avatar={
                <IconAvatar img={item} sx={sx} />
            }
            title={item.text}
            disableTypography={disableTypo}
            titleTypographyProps={titleTypographyProps}
        />
    );
};

export const showItem = (elt: LovItem, searchValue: string) => {
    return (
        !searchValue ||
        ((typeof elt.item === "string" ? (elt.item as string) : (elt.item as Icon).text) || elt.id)
            .toLowerCase()
            .indexOf(searchValue.toLowerCase()) > -1
    );
};

export interface ItemProps {
    value: string;
    clickHandler: (evt: MouseEvent<HTMLElement>) => void;
    selectedValue: string[] | string;
    item: stringIcon;
    disabled: boolean;
    withAvatar?: boolean;
    titleTypographyProps?: TypographyProps<"span", { component?: "span"; }>;
}

export const SingleItem = ({
    value,
    clickHandler,
    selectedValue,
    item,
    disabled,
    withAvatar = false,
    titleTypographyProps,
}: ItemProps) => (
    <ListItemButton
        onClick={clickHandler}
        data-id={value}
        selected={Array.isArray(selectedValue) ? selectedValue.indexOf(value) !== -1 : selectedValue === value}
        disabled={disabled}
    >
        {typeof item === "string" ? (
            withAvatar ? (
                <ListItemAvatar>
                    <CardHeader
                        sx={cardSx}
                        avatar={
                            <Tooltip title={item}>
                                <Avatar sx={avatarSx}>{getInitials(item)}</Avatar>
                            </Tooltip>
                        }
                        title={item}
                        titleTypographyProps={titleTypographyProps}
                    />
                </ListItemAvatar>
            ) : (
                <ListItemText primary={item} />
            )
        ) : (
            <ListItemAvatar>
                <LovImage item={item} titleTypographyProps={titleTypographyProps} />
            </ListItemAvatar>
        )}
    </ListItemButton>
);

export const isLovParent = (lov: LovItem[] | undefined, id: string, childId: string, path: string[] = []): boolean => {
    if (!lov) {
        return false;
    }
    for (let i = 0; i < lov.length; i++) {
        if (lov[i].id === id && !(lov[i].children || []).length) {
            return false;
        } else if (lov[i].id === childId) {
            return path.includes(id);
        } else if (isLovParent(lov[i].children, id, childId, [...path, lov[i].id])) {
            return true;
        }
    }
    return false;
};
