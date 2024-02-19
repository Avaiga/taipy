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
    _variables: VariableModuleData;

    constructor(variableModuleData: VariableModuleData) {
        this._data = {};
        this._variables = {};
        this.init(variableModuleData);
    }

    init(variableModuleData: VariableModuleData) {
        // Identify changes between the new and old data
        const changes: VariableModuleData = {};
        for (const context in this._variables) {
            if (!(context in variableModuleData)) {
                changes[context] = this._variables[context];
                continue;
            }
            for (const variable in this._variables[context]) {
                if (!(variable in variableModuleData[context])) {
                    if (!(context in changes)) {
                        changes[context] = {};
                    }
                    changes[context][variable] = this._variables[context][variable];
                }
            }
        }
        if (changes) {
            console.error("Unmatched data tree! Removed changes: ", changes);
        }
        // Reset the initial data
        this._variables = variableModuleData;
        this._data = {};
        for (const context in this._variables) {
            for (const variable in this._variables[context]) {
                const vData = this._variables[context][variable];
                this._data[vData["encoded_name"]] = vData.value;
            }
        }
    }

    getEncodedName(varName: string, module: string): string | undefined {
        if (module in this._variables && varName in this._variables[module]) {
            return this._variables[module][varName].encoded_name;
        }
        return undefined;
    }

    // return [name, moduleName]
    getName(encodedName: string): [string, string] | undefined {
        for (const context in this._variables) {
            for (const variable in this._variables[context]) {
                const vData = this._variables[context][variable];
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
        for (const context in this._variables) {
            for (const variable in this._variables[context]) {
                const vData = this._variables[context][variable];
                if (vData.encoded_name === encodedName) {
                    return { ...vData, value: this._data[encodedName] };
                }
            }
        }
        return undefined;
    }

    getDataTree(): VariableModuleData {
        return this._variables;
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
