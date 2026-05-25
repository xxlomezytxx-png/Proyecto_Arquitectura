const swaggerJsdoc = require('swagger-jsdoc');

const options = {

    definition: {
        openapi: '3.0.0',
        info: {
            title: 'BFF Gateway API',
            version: '1.0.0',
            description: 'Documentation for Dev6 BFF Advanced'
        },
        servers: [
            {
                url: 'http://localhost:3000'
            }
        ]
    },

    apis: ['./src/routes/*.js']
};

const swaggerSpec = swaggerJsdoc(options);

module.exports = swaggerSpec;