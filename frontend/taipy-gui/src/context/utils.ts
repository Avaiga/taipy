import { TAIPY_CLIENT_ID } from "./wsUtils";

export const getLocalStorageValue = <T = string>(key: string, defaultValue: T, values?: T[]) => {
    const val = localStorage && (localStorage.getItem(key) as unknown as T);
    return !val ? defaultValue : !values ? val : values.indexOf(val) == -1 ? defaultValue : val;
};

export const storeClientId = (id: string) => localStorage && localStorage.setItem(TAIPY_CLIENT_ID, id);

export interface IdMessage {
    id: string;
}
