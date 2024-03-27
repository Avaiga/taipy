import { TaipyApp, createApp, OnChangeHandler, OnInitHandler } from "./app";
import { ModuleData } from "./dataManager";

export default TaipyApp;
export { TaipyApp, createApp };
export type { OnChangeHandler, OnInitHandler, ModuleData };

window.addEventListener("beforeunload", () => {
    document.cookie = "tprh=;path=/;Max-Age=-99999999;";
    localStorage.removeItem("tp_cp_meta");
});
