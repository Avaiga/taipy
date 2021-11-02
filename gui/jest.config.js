/** @type {import('ts-jest/dist/types').InitialOptionsTsJest} */
module.exports = {
 // testEnvironment: 'jest-environment-jsdom',
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFiles: ['./jest.env.js']
};
