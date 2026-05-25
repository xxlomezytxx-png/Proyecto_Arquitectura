/**
 * @swagger
 * /api/products/{id}:
 *   get:
 *     summary: Get complete product information
 *     tags: [Products]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: Book ID
 *     responses:
 *       200:
 *         description: Book information retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 id:
 *                   type: string
 *                 title:
 *                   type: string
 *                 author:
 *                   type: string
 *                 stock:
 *                   type: integer
 *                 available:
 *                   type: boolean
 *                 price:
 *                   type: integer
 */

const express = require('express');

const router = express.Router();

const bookController = require('../controllers/bookController');

router.get('/:id', bookController.getBookById);

module.exports = router;