import { TaipyApp, createApp, OnChangeHandler, OnInitHandler } from "./app";
import { VariableModuleData } from "./variableManager";

export default TaipyApp;
export { TaipyApp, createApp };
export type { OnChangeHandler, OnInitHandler, VariableModuleData };

window.addEventListener("beforeunload", () => {
    document.cookie = "tprh=;path=/;Max-Age=-99999999;";
});
