import { createContext, Dispatch } from "react";
import { TaipyBaseAction, TaipyState } from "./taipyReducers";

export interface TaipyStore {
    state: TaipyState;
    dispatch: Dispatch<TaipyBaseAction>;
}

export const TaipyContext = createContext<TaipyStore>({state: {data: {}} as TaipyState, dispatch: () => null});
TaipyContext.displayName = 'Taipy Context';
