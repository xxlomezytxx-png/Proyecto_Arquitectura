const express = require('express');

const app = express();

app.use(express.json());

app.post('/orders', (req, res) => {

    res.status(201).json({
        orderId: 101,
        status: 'CONFIRMED',
        total: 160000,
        items: req.body.books
    });
});

app.get('/health', (req, res) => {

    res.json({
        status: 'UP'
    });
});

app.listen(3004, () => {
    console.log('Order Service running on port 3004');
});