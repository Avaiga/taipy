export interface FileUploadData {
    varName: string;
    files: FileList;
    uploadUrl: string;
    id: string;
}

export interface FileUploadReturn {
    message: string;
    progress: number;
    done: boolean;
    error: boolean;
}
