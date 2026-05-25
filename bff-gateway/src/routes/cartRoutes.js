/**
 * @swagger
 * /api/cart:
 *   get:
 *     summary: Get shopping cart
 *     tags: [Cart]
 *     responses:
 *       200:
 *         description: Cart retrieved successfully
 *
 *   post:
 *     summary: Add book to cart
 *     tags: [Cart]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               bookId:
 *                 type: integer
 *               title:
 *                 type: string
 *               quantity:
 *                 type: integer
 *     responses:
 *       201:
 *         description: Book added to cart
 *
 * /api/cart/{bookId}:
 *   delete:
 *     summary: Remove book from cart
 *     tags: [Cart]
 *     parameters:
 *       - in: path
 *         name: bookId
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Book removed from cart
 */

const express = require('express');

const router = express.Router();

const cartController = require('../controllers/cartController');

router.get('/', cartController.getCart);

router.post('/', cartController.addToCart);

router.delete('/:bookId', cartController.removeFromCart);

module.exports = router;