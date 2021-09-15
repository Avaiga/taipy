import { createContext, Dispatch } from "react";
import { TaipyAction, TaipyState } from "./taipyReducers";

export interface TaipyStore {
    state: TaipyState;
    dispatch: Dispatch<TaipyAction>;
}

export const TaipyContext = createContext<TaipyStore>({state: {data: {}} as TaipyState, dispatch: () => null});
TaipyContext.displayName = 'Taipy Context';
