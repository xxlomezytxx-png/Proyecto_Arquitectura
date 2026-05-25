const express = require('express');
const cors = require('cors');
const morgan = require('morgan');

const swaggerUi = require('swagger-ui-express');
const swaggerSpec = require('./docs/swagger');

const errorHandler = require('./middlewares/errorHandler');

const app = express();

app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

app.use(
    '/api-docs',
    swaggerUi.serve,
    swaggerUi.setup(swaggerSpec)
);

app.use('/api/products', require('./routes/bookRoutes'));
app.use('/api/orders', require('./routes/orderRoutes'));
app.use('/api/cart', require('./routes/cartRoutes'));
app.use('/api/assistant', require('./routes/assistantRoutes'));
app.use('/health', require('./routes/healthRoutes'));

app.get('/', (req, res) => {
    res.json({
        message: 'BFF Gateway Running'
    });
});

app.use(errorHandler);

module.exports = app;