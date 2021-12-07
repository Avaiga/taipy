import { Table as ArrowTable } from "apache-arrow";

export enum DataFormat {
    JSON = "JSON",
    APACHE_ARROW = "ARROW",
}

export const parseData = (data: Record<string, unknown>): Record<string, unknown> => {
    if (data) {
        if (data.format && data.format === DataFormat.APACHE_ARROW) {
            const arrowData = ArrowTable.from(new Uint8Array(data.data as ArrayBuffer));
            const tableHeading = arrowData.schema.fields.map((f) => f.name);
            const len = arrowData.count();
            if (data.orient === "records") {
                const convertedData: Array<unknown> = [];
                for (let i = 0; i < len; i++) {
                    const dataRow: Record<string, unknown> = {};
                    for (let j = 0; j < tableHeading.length; j++) {
                        dataRow[tableHeading[j]] = arrowData.getColumnAt(j)?.get(i).valueOf();
                    }
                    convertedData.push(dataRow);
                }
                data.data = convertedData;
            } else if (data.orient === "list") {
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
                data.data = convertedData;
            }
        }
        if (typeof data.dataExtraction === "boolean" && data.dataExtraction) {
            data = data.data as Record<string, unknown>;
        }
    }
    return data;
};
