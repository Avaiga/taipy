/** @type {import('ts-jest/dist/types').InitialOptionsTsJest} */
module.exports = {
 // testEnvironment: 'jest-environment-jsdom',
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFiles: ['./test-config/jest.env.js', './test-config/createObjectUrl.js', './test-config/Canvas.js']
};
