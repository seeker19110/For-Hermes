/**
 * Mock for @sodax/sdk
 */
export declare class Sodax {
    static initialize: jest.Mock<any, any, any>;
    swaps: {
        getQuote: jest.Mock<any, any, any>;
        executeSwap: jest.Mock<any, any, any>;
        cancelIntent: jest.Mock<any, any, any>;
    };
    bridge: {
        getBridgeableTokens: jest.Mock<any, any, any>;
        bridge: jest.Mock<any, any, any>;
    };
    moneyMarket: {
        supply: jest.Mock<any, any, any>;
        withdraw: jest.Mock<any, any, any>;
        borrow: jest.Mock<any, any, any>;
        repay: jest.Mock<any, any, any>;
        getUserAccountDataOnSpoke: jest.Mock<any, any, any>;
    };
}
export declare const Intent: {};
//# sourceMappingURL=sdk.d.ts.map