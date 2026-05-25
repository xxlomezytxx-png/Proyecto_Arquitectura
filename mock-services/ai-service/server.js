const express = require('express');

const app = express();

app.use(express.json());

app.post('/assistant/ask', (req, res) => {

    const question = req.body.question;

    let answer = '';

    if (question.toLowerCase().includes('clean code')) {

        answer =
            'Sí, el libro Clean Code tiene disponibilidad de 10 unidades y un precio de 80000.';
    } else {

        answer =
            'No tengo información disponible para esa consulta.';
    }

    res.json({
        answer
    });
});

app.get('/health', (req, res) => {

    res.json({
        status: 'UP'
    });
});

app.listen(3005, () => {
    console.log('AI Assistant Service running on port 3005');
});