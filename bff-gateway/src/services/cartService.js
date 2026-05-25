const axios = require('axios');

const CART_SERVICE = 'http://localhost:3006';

const getCart = async () => {

    const response = await axios.get(
        `${CART_SERVICE}/cart`
    );

    return response.data;
};

const addToCart = async (bookData) => {

    const response = await axios.post(
        `${CART_SERVICE}/cart`,
        bookData
    );

    return response.data;
};

const removeFromCart = async (bookId) => {

    const response = await axios.delete(
        `${CART_SERVICE}/cart/${bookId}`
    );

    return response.data;
};

module.exports = {
    getCart,
    addToCart,
    removeFromCart
};