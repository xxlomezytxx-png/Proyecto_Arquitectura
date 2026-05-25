const axios = require('axios');

const assistantUrl = process.env.AI_SERVICE || process.env.ASSISTANT_SERVICE_URL || 'http://localhost:8011';

const askQuestion = async (questionData) => {

    try {

        const response = await axios.post(
            `${assistantUrl}/assistant/ask`,
            questionData
        );

        return response.data;

    } catch (error) {

        throw new Error('Error communicating with AI Assistant');
    }
};

module.exports = {
    askQuestion
};