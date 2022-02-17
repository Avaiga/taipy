import { stringImage } from "./image";

export interface LovItem {
    id: string;
    item: stringImage;
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
