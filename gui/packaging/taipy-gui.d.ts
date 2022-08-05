export interface TaipyState {
}
export interface TaipyBaseAction {
}
export interface TaipyStore {
	state: TaipyState;
	dispatch: import("react").Dispatch<TaipyBaseAction>;
}
export declare const TaipyContext: import("react").Context<TaipyStore>;

// utils
export declare const useDynamicProperty: <T>(value: T, defaultValue: T, defaultStatic: T) => T;

// Reducers
export declare const createSendActionNameAction: (name: string | undefined, value: unknown, ...args: unknown[]) => TaipyBaseAction;
export declare const createSendUpdateAction: (name: string | undefined, value: unknown, onChange?: string, propagate?: boolean, relName?: string) => TaipyBaseAction;

//Comps
export declare const Router: () => JSX.Element;