import { generateHeaderClassName } from "./tableUtils";

describe("generateHeaderClassName", () => {
    it("should generate a CSS class name with a hyphen prefix and convert to lowercase", () => {
        const result = generateHeaderClassName("ColumnName");
        expect(result).toBe("-columnname");
    });

    it("should replace spaces and special characters with hyphens", () => {
        const result = generateHeaderClassName("Column Name@123!");
        expect(result).toBe("-column-name-123-");
    });

    it("should remove multiple hyphens in a row", () => {
        const result = generateHeaderClassName("Column--Name");
        expect(result).toBe("-column-name");
    });

    it("should handle empty strings and return an empty string", () => {
        const result = generateHeaderClassName("");
        expect(result).toBe("");
    });

    it("should return empty string for the undefined", () => {
        const result = generateHeaderClassName(undefined);
        expect(result).toBe("");
    });
});
