const express = require('express');

const app = express();

app.get('/pricing/:id', (req, res) => {

    res.json({
        price: 80000
    });
});

app.get('/health', (req, res) => {

    res.json({
        status: 'UP'
    });
});

app.listen(3003, () => {
    console.log('Pricing Service running on port 3003');
});