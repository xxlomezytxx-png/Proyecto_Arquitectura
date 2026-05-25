/**
 * @swagger
 * /api/assistant/ask:
 *   post:
 *     summary: Ask AI Assistant
 *     tags: [Assistant]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               question:
 *                 type: string
 *     responses:
 *       200:
 *         description: AI response returned successfully
 */

const express = require('express');

const router = express.Router();

const assistantController = require('../controllers/assistantController');

router.post('/ask', assistantController.askAssistant);

module.exports = router;