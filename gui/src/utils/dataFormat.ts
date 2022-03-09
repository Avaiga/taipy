import { Table as ArrowTable } from "apache-arrow";

export enum DataFormat {
    JSON = "JSON",
    APACHE_ARROW = "ARROW",
}

export const parseData = (data: Record<string, unknown>): Record<string, unknown> => {
    if (data) {
        if (data.format !== undefined) {
            const multi = typeof data.multi === "boolean" && data.multi;
            const arrow = data.format === DataFormat.APACHE_ARROW;
            const orient = data.orient;
            const pData = multi ? (data.data as Array<unknown>) : [data.data];
            const res = arrow
                ? pData.map((d) => {
                      const arrowData = ArrowTable.from(new Uint8Array(d as ArrayBuffer));
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
                  })
                : pData;
            if (typeof data.dataExtraction === "boolean" && data.dataExtraction) {
                data = (multi ? res : res[0]) as Record<string, unknown>;
            } else {
                data.data = multi ? res : res[0];
            }
        }
    }
    return data;
};
