import { WsMessage } from "../../src/context/wsUtils";
import { TaipyApp } from "./app";

export abstract class WsAdapter {
    abstract supportedMessageTypes: string[];

    abstract handleWsMessage(message: WsMessage, app: TaipyApp): void;
}
