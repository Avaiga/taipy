/*
 * Copyright 2021-2024 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import { FileUploadData, FileUploadReturn } from "./fileupload.utils";

const worker = new Worker(new URL("./fileupload.worker.ts", import.meta.url));

const UPLOAD_URL = "/taipy-uploads";

export const uploadFile = (
    varName: string,
    context: string | undefined,
    onAction: string | undefined,
    uploadData: string | undefined,
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
        worker.postMessage({ files, uploadUrl, varName, context, onAction, uploadData, id } as FileUploadData);
    });
};
