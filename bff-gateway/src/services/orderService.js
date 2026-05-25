const axios = require('axios');

const orderServiceUrl =
    process.env.ORDER_SERVICE ||
    process.env.ORDER_SERVICE_URL ||
    'http://localhost:8010';

const createOrder = async (orderData) => {

    try {

        const response = await axios.post(
            `${orderServiceUrl}/orders`,
            orderData
        );

        return response.data;

    } catch (error) {

        if (error.response) {
            const status = error.response.status
            const message =
                error.response.data?.detail ||
                error.response.data?.message ||
                error.response.statusText ||
                error.message
            const err = new Error(message)
            err.status = status
            throw err
        }

        if (error.request) {
            const err = new Error(
                'Order service unavailable. Intenta de nuevo más tarde.'
            )
            err.status = 503
            throw err
        }

        throw error
    }
};

module.exports = {
    createOrder
};