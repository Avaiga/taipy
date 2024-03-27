const handleLoadEvent = (e: ProgressEvent) => {
    if (e.type == "progress") {
        console.log(`${e.type}: ${e.loaded} bytes transferred Received of ${e.total}`);
    } else if (e.type == "loadstart") {
        console.log(`${e.type}: started`);
    } else if (e.type == "error") {
        console.log(`${e.type}: error`);
    } else if (e.type == "loadend") {
        console.log(`${e.type}: completed`);
    }
};

const addListeners = (xhr: XMLHttpRequest, onLoaded?: () => void) => {
    xhr.addEventListener("loadstart", handleLoadEvent);
    xhr.addEventListener("load", handleLoadEvent);
    xhr.addEventListener("loadend", onLoaded || handleLoadEvent);
    xhr.addEventListener("progress", handleLoadEvent);
    xhr.addEventListener("error", handleLoadEvent);
    xhr.addEventListener("abort", handleLoadEvent);
};

export const runXHR = (downloadLink: HTMLAnchorElement | undefined, url: string, name?: string, onAction?: ()=> void) => {
    const request = new XMLHttpRequest();
    addListeners(request, onAction);
    request.open("GET", url, true);
    request.responseType = "blob";
    request.onload = function () {
        const aDownloadLink = downloadLink || document.createElement("a");
        aDownloadLink.href = window.URL.createObjectURL(request.response);
        downloadLink || (aDownloadLink.download = name || "file");
        aDownloadLink.click();
        setTimeout(() => aDownloadLink.href = "", 1);
    };
    request.send();
    return request;
};
