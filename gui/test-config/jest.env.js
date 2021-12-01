// setup file for jest
const dotenv = require('dotenv');
const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;
dotenv.config({ path: './.env.test' });
