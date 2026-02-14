import { generateApi } from 'swagger-typescript-api';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BACKEND_DIR = path.resolve(__dirname, '../../backend');
const FRONTEND_SRC_DIR = path.resolve(__dirname, '../src');
const OUTPUT_DIR = path.join(FRONTEND_SRC_DIR, 'api');
const OPENAPI_JSON_PATH = path.join(BACKEND_DIR, 'openapi.json');

async function generate() {
    try {
        console.log('1. Extracting OpenAPI schema from backend...');
        // Ensure the backend script exists
        const scriptPath = path.join(BACKEND_DIR, 'scripts', 'extract_openapi.py');
        if (!fs.existsSync(scriptPath)) {
            throw new Error(`Backend script not found at ${scriptPath}`);
        }

        // Run the python script to extract openapi.json
        // We assume python is in the path. You might need to use 'python3' or a venv path.
        // For this environment, we'll try 'python'.
        await execPromise(`python "${scriptPath}" "${OPENAPI_JSON_PATH}"`);
        console.log('   OpenAPI schema extracted successfully.');

        console.log('2. Generating TypeScript interfaces...');
        if (!fs.existsSync(OUTPUT_DIR)) {
            fs.mkdirSync(OUTPUT_DIR, { recursive: true });
        }

        await generateApi({
            name: 'types.d.ts',
            output: OUTPUT_DIR,
            input: OPENAPI_JSON_PATH,
            generateClient: false, // We only want types for now
            generateRouteTypes: false,
        });

        console.log(`   Types generated at ${path.join(OUTPUT_DIR, 'types.d.ts')}`);

    } catch (error) {
        console.error('Error generating types:', error);
        process.exit(1);
    }
}

generate();
