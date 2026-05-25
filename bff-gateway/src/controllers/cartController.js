const cartService = require('../services/cartService');

const getCart = async (req, res, next) => {

    try {

        const cart = await cartService.getCart();

        res.json(cart);

    } catch (error) {

        next(error);
    }
};

const addToCart = async (req, res, next) => {

    try {

        const response = await cartService.addToCart(req.body);

        res.status(201).json(response);

    } catch (error) {

        next(error);
    }
};

const removeFromCart = async (req, res, next) => {

    try {

        const response = await cartService.removeFromCart(
            req.params.bookId
        );

        res.json(response);

    } catch (error) {

        next(error);
    }
};

module.exports = {
    getCart,
    addToCart,
    removeFromCart
};