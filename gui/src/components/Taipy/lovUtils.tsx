import React, { CSSProperties, useMemo } from "react";
import Avatar from "@mui/material/Avatar";
import CardHeader from "@mui/material/CardHeader";

import { TaipyBaseProps, TaipyImage } from "./utils";

export interface LovItem {
    id: string;
    item: string | TaipyImage;
    children?: LovItem[];
}

export interface SelTreeProps extends LovProps {
    filter?: boolean;
    multiple?: boolean;
    width?: string | number;
}

export interface LovProps extends TaipyBaseProps {
    defaultLov?: string;
    lov: LoV;
    value?: string | string[];
    height?: string | number;
}

type LoVElt = [string, string | TaipyImage, LoVElt[]?];

export type LoV = LoVElt[];

const getLovItem = (elt: LoVElt, tree = false): LovItem => {
    const it: LovItem = {
        id: elt[0],
        item: elt[1] || elt[0],
    };
    if (tree) {
        it.children = elt.length > 2 ? elt[2]?.map((e) => getLovItem(e, true)) : [];
    }
    return it;
};

export const boxSx = { width: "100%" } as CSSProperties;
export const paperBaseSx = { width: "100%", mb: 2, display: "grid", gridTemplateRows: "auto 1fr" } as CSSProperties;
export const treeSelBaseSx = { width: "100%", bgcolor: "background.paper", overflowY: "auto" } as CSSProperties;

export const useLovListMemo = (lov: LoV, defaultLov: string, tree = false): LovItem[] =>
    useMemo(() => {
        if (lov) {
            if (lov.length && lov[0][0] === undefined) {
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

const cardSx = { padding: 0 } as CSSProperties;
export const LovImage = ({ item }: { item: TaipyImage }) => (
    <CardHeader sx={cardSx} avatar={<Avatar alt={item.text} src={item.path} />} title={item.text} />
);

export const showItem = (elt: LovItem, searchValue: string) => {
    return (
        !searchValue ||
        ((typeof elt.item === "string" ? (elt.item as string) : (elt.item as TaipyImage).text) || elt.id)
            .toLowerCase()
            .indexOf(searchValue.toLowerCase()) > -1
    );
};
