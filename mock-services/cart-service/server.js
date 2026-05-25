const express = require('express');

const app = express();

app.use(express.json());

let cart = [];

app.get('/cart', (req, res) => {

    res.json(cart);
});

app.post('/cart', (req, res) => {

    cart.push(req.body);

    res.status(201).json({
        message: 'Book added to cart',
        cart
    });
});

app.delete('/cart/:bookId', (req, res) => {

    cart = cart.filter(
        item => item.bookId != req.params.bookId
    );

    res.json({
        message: 'Book removed from cart',
        cart
    });
});

app.listen(3006, () => {
    console.log('Cart Service running on port 3006');
});