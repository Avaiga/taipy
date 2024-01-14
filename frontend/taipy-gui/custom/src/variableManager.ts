export interface VariableModuleData {
    [key: string]: VariableName;
}

interface VariableName {
    [key: string]: VariableData;
}

interface VariableData {
    type: string;
    value: unknown;
    encoded_name: string;
}

// This class hold the information of variables and real-time value of variables
export class VariableManager {
    // key: encoded name, value: real-time value
    _data: Record<string, unknown>;
    // Initial data fetched from taipy-gui backend
    _variableData: VariableModuleData;

    constructor(variableModuleData: VariableModuleData) {
        this._data = {};
        this._variableData = {};
        this.resetInitData(variableModuleData);
    }

    resetInitData(variableModuleData: VariableModuleData) {
        this._variableData = variableModuleData;
        this._data = {};
        for (const context in this._variableData) {
            for (const variable in this._variableData[context]) {
                const vData = this._variableData[context][variable];
                this._data[vData["encoded_name"]] = vData.value;
            }
        }
    }

    getEncodedName(varName: string, module: string): string | undefined {
        if (module in this._variableData && varName in this._variableData[module]) {
            return this._variableData[module][varName].encoded_name;
        }
        return undefined;
    }

    // return [name, moduleName]
    getName(encodedName: string): [string, string] | undefined {
        for (const context in this._variableData) {
            for (const variable in this._variableData[context]) {
                const vData = this._variableData[context][variable];
                if (vData.encoded_name === encodedName) {
                    return [variable, context];
                }
            }
        }
        return undefined;
    }

    get(encodedName: string): unknown {
        if (!(encodedName in this._data)) {
            throw new Error(`${encodedName} is not available in Taipy Gui`);
        }
        return this._data[encodedName];
    }

    getInfo(encodedName: string): VariableData | undefined {
        for (const context in this._variableData) {
            for (const variable in this._variableData[context]) {
                const vData = this._variableData[context][variable];
                if (vData.encoded_name === encodedName) {
                    return { ...vData, value: this._data[encodedName] };
                }
            }
        }
        return undefined;
    }

    getDataTree(): VariableModuleData {
        return this._variableData;
    }

    getAllData(): Record<string, unknown> {
        return this._data;
    }

    update(encodedName: string, value: unknown) {
        if (!(encodedName in this._data)) {
            throw new Error(`${encodedName} is not available in Taipy Gui`);
        }
        this._data[encodedName] = value;
    }
}
