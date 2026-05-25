const assistantService = require('../services/assistantService');

const askAssistant = async (req, res, next) => {

    try {

        const response = await assistantService.askQuestion(req.body);

        res.json(response);

    } catch (error) {

        next(error);
    }
};

module.exports = {
    askAssistant
};