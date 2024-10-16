jest.mock(
    "taipy-gui",
    () => ({
        useDispatch: jest.fn(() => jest.fn()),
        useModule: jest.fn(),
        createSendActionNameAction: jest.fn(),
        getUpdateVar: jest.fn((a, b) => b),
        createSendUpdateAction: jest.fn(),
        useDynamicProperty: jest.fn(),
        getComponentClassName: jest.fn(),
        useDispatchRequestUpdateOnFirstRender: jest.fn(),
        useClassNames: jest.fn((a, b, c) => c || b || a || ""),
    }),
    { virtual: true }
);
