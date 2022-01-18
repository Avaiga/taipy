import { URL as NodeURL } from "url";
import { FileUploadData, FileUploadReturn } from "./fileupload.utils";

const worker = new Worker(new URL("./fileupload.worker.ts", import.meta.url) as NodeURL);

const UPLOAD_URL = "/taipy-uploads";

const uploadFile = (
    varName: string,
    files: FileList,
    progressCallback: (val: number) => void,
    id: string,
    uploadUrl = UPLOAD_URL
): Promise<string> => {
    return new Promise((resolve, reject) => {
        worker.onmessage = (evt: MessageEvent<FileUploadReturn>) => {
            if (evt.data.error) {
                reject(evt.data.message);
            } else if (evt.data.done) {
                resolve(evt.data.message);
            } else {
                progressCallback(evt.data.progress);
            }
        };
        worker.onerror = (evt: ErrorEvent) => reject(evt);
        worker.postMessage({ files: files, uploadUrl: uploadUrl, varName: varName, id: id } as FileUploadData);
    });
};

export default uploadFile;
