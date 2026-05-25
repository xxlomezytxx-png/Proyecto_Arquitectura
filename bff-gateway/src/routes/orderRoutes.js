/**
 * @swagger
 * /api/orders:
 *   post:
 *     summary: Create a new order
 *     tags: [Orders]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               books:
 *                 type: array
 *                 items:
 *                   type: object
 *                   properties:
 *                     bookId:
 *                       type: integer
 *                     quantity:
 *                       type: integer
 *     responses:
 *       201:
 *         description: Order created successfully
 */

const express = require('express');

const router = express.Router();

const orderController = require('../controllers/orderController');

router.post('/', orderController.createOrder);

module.exports = router;