const orderService = require('../services/orderService');

const createOrder = async (req, res, next) => {

    try {

        const order = await orderService.createOrder(req.body);

        res.status(201).json(order);

    } catch (error) {

        next(error);
    }
};

module.exports = {
    createOrder
};