import { stringIcon } from "./icon";

export interface LovItem {
    id: string;
    item: stringIcon;
    children?: LovItem[];
}

export interface MenuProps {
    label?: string;
    width?: string;
    tp_onAction?: string;
    inactiveIds?: string[];
    lov?: LovItem[];
    active?: boolean;
    className?: string;
}
