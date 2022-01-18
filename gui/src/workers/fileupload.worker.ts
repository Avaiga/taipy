import { FileUploadData, FileUploadReturn } from "./fileupload.utils";

const uploadFile = (
    blobOrFile: Blob,
    uploadUrl: string,
    varName: string,
    part: number,
    total: number,
    fileName: string,
    multiple: boolean,
    id: string
) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${uploadUrl}?client_id=${id}`, false);
    xhr.onerror = (e) => self.postMessage({ message: "Error: " + e, error: true });
    xhr.onload = (e) =>
        self.postMessage({
            progress: e.lengthComputable ? (e.loaded / e.total) * 100 : 0,
            done: false,
        } as FileUploadReturn);
    const fdata = new FormData();
    fdata.append("blob", blobOrFile, fileName);
    fdata.append("part", part.toString());
    fdata.append("total", total.toString());
    fdata.append("var_name", varName);
    fdata.append("multiple", multiple ? "True" : "False");
    xhr.send(fdata);
};

// 1MB chunk sizes.
const BYTES_PER_CHUNK = 1024 * 1024;

const process = (files: FileList, uploadUrl: string, varName: string, id: string) => {
    if (files) {
        for (let i = 0; i < files.length; i++) {
            const blob = files[i];
            const size = blob.size;

            let start = 0;
            let end = BYTES_PER_CHUNK;
            const tot = Math.ceil(size / BYTES_PER_CHUNK);

            while (start < size) {
                const chunk = blob.slice(start, end);

                uploadFile(
                    chunk,
                    uploadUrl,
                    varName,
                    start / BYTES_PER_CHUNK,
                    tot,
                    blob.name,
                    i == 0 ? false : files.length > 0,
                    id
                );

                start = end;
                end = start + BYTES_PER_CHUNK;
            }
            self.postMessage({
                progress: 100,
                message: blob.name + " Uploaded Succesfully",
                done: true,
            } as FileUploadReturn);
        }
    }
};

self.onmessage = (e: MessageEvent<FileUploadData>) => {
    process(e.data.files, e.data.uploadUrl, e.data.varName, e.data.id);
};
