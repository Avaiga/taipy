// need to mock the worker as import.meta.url is not supported yet by jest
jest.mock("../src/workers/fileupload", () => {
    return {
        __esModule: true,
        uploadFile: (
            varName,
            files,
            progressCallback,
            id,
            uploadUrl
        ) => new Promise((resolve, reject) => {
            resolve("mocked");
        }),
    };
});