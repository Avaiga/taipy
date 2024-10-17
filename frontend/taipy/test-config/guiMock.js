jest.mock("taipy-gui", () => ({
    useDispatch: jest.fn(() => jest.fn()),
    useModule: jest.fn(),
    createSendActionNameAction: jest.fn(),
    getUpdateVar: jest.fn((a, b) => b),
    createSendUpdateAction: jest.fn(),
    useDynamicProperty: jest.fn((a, b, c) => (typeof a == "undefined" ? (typeof b == "undefined" ? c : b) : a)),
    getComponentClassName: jest.fn(),
    useDispatchRequestUpdateOnFirstRender: jest.fn(),
    useClassNames: jest.fn((a, b, c) => c || b || a || ""),
    getSuffixedClassNames: jest.fn()
}));
