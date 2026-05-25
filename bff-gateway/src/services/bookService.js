const axios = require('axios');

const getCompleteBook = async (bookId) => {

    try {

        const catalogResponse = await axios.get(
            `${process.env.CATALOG_SERVICE}/products/${bookId}`
        );

        const inventoryResponse = await axios.get(
            `${process.env.INVENTORY_SERVICE}/inventory/${bookId}`
        );

        const pricingResponse = await axios.get(
            `${process.env.PRICING_SERVICE}/pricing/${bookId}`
        );

        return {
            id: catalogResponse.data.id,
            title: catalogResponse.data.title,
            author: catalogResponse.data.author,
            stock: inventoryResponse.data.stock,
            available: inventoryResponse.data.available,
            price: pricingResponse.data.price
        };

    } catch (error) {

        console.error(error.message);

        throw new Error('Error consuming microservices');
    }
};

module.exports = {
    getCompleteBook
};