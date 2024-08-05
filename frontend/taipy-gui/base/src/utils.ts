export const getBase = () => {
    return document.getElementsByTagName("base")[0].getAttribute("href");
};
