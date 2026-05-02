import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
    input: 'http://127.0.0.1:4267/openapi.json',
    output: 'src/lib/api',
    plugins: [
        '@hey-api/client-fetch',
        {
            name: '@hey-api/sdk',
            operations: {
                strategy: 'byTags',
            },
        },
    ],
});
