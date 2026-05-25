const bookService = require('../services/bookService');

const getBookById = async (req, res, next) => {

    try {

        const book = await bookService.getCompleteBook(req.params.id);

        res.json(book);

    } catch (error) {

        next(error);
    }
};

module.exports = {
    getBookById
};