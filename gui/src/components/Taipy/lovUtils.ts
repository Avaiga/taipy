import { TaipyImage, TaipyInputProps } from "./utils";

export interface LovItem {
    id: string;
    item: string | TaipyImage;
}

export interface LovProps extends TaipyInputProps {
    defaultLov: string;
    lov: [string, string | TaipyImage][];
}
