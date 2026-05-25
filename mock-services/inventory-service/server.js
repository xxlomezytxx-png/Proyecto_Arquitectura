const express = require('express');

const app = express();

app.get('/inventory/:id', (req, res) => {

    res.json({
        stock: 10,
        available: true
    });
});

app.get('/health', (req, res) => {

    res.json({
        status: 'UP'
    });
});

app.listen(3002, () => {
    console.log('Inventory Service running on port 3002');
});