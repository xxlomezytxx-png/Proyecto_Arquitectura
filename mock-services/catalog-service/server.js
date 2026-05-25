const express = require('express');

const app = express();

app.get('/products/:id', (req, res) => {

    res.json({
        id: req.params.id,
        title: 'Clean Code',
        author: 'Robert C. Martin'
    });
});

app.get('/health', (req, res) => {

    res.json({
        status: 'UP'
    });
});

app.listen(3001, () => {
    console.log('Catalog Service running on port 3001');
});