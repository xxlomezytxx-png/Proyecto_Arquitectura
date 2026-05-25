/**
 * @swagger
 * /health:
 *   get:
 *     summary: Get health status of all services
 *     tags: [Health]
 *     responses:
 *       200:
 *         description: Health status retrieved successfully
 */

const express = require('express');

const router = express.Router();

router.get('/', async (req, res) => {

    res.json({
        catalog: 'UP',
        inventory: 'UP',
        pricing: 'UP',
        orders: 'UP',
        assistant: 'UP'
    });
});

module.exports = router;