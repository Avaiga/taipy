export enum DataFormat {
    JSON = "JSON",
    APACHE_ARROW = "ARROW",
}

export const parseData = (data: Record<string, unknown>): Promise<Record<string, unknown>> => {
    if (data?.format === DataFormat.APACHE_ARROW) {
        const multi = typeof data.multi === "boolean" && data.multi;
        const orient = data.orient;
        const pData = multi ? (data.data as Array<unknown>) : [data.data];
        return new Promise((resolve, reject) => {
            import("apache-arrow").then(({Table}) => {
                const res = pData.map((d) => {
                    const arrowData = Table.from(new Uint8Array(d as ArrayBuffer));
                    const tableHeading = arrowData.schema.fields.map((f) => f.name);
                    const len = arrowData.count();
                    if (orient === "records") {
                        const convertedData: Array<unknown> = [];
                        for (let i = 0; i < len; i++) {
                            const dataRow: Record<string, unknown> = {};
                            for (let j = 0; j < tableHeading.length; j++) {
                                dataRow[tableHeading[j]] = arrowData.getColumnAt(j)?.get(i).valueOf();
                            }
                            convertedData.push(dataRow);
                        }
                        return convertedData;
                    } else if (orient === "list") {
                        const convertedData: Record<string, unknown> = {};
                        for (let i = 0; i < tableHeading.length; i++) {
                            const dataRow: Array<unknown> = [];
                            const col = arrowData.getColumnAt(i);
                            if (col) {
                                for (let j = 0; j < len; j++) {
                                    dataRow.push(col.get(j).valueOf());
                                }
                            }
                            convertedData[tableHeading[i]] = dataRow;
                        }
                        return convertedData;
                    }
                });
                if (typeof data.dataExtraction === "boolean" && data.dataExtraction) {
                    data = (multi ? res : res[0]) as Record<string, unknown>;
                } else {
                    data.data = multi ? res : res[0];
                }
                resolve(data);    
            }).catch(reject);
        });
    } else if (typeof data?.dataExtraction === "boolean" && data.dataExtraction) {
        data = data.data as Record<string, unknown>;
    }
    return new Promise((resolve) => {
        resolve(data);
    });
};
