export interface TaipyImage {
    path: string;
    text: string;
}

export interface LovItem {
    id: string;
    item: string | TaipyImage;
    children?: LovItem[];
}

export interface MenuProps {
    label?: string;
    width?: string;
    tp_onAction?: string;
    inactiveIds?: string[];
    lov?: LovItem[];
    value?: string;
    active?: boolean;
    className?: string;
}
