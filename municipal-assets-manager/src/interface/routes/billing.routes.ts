import { Router } from 'express';
import { BillingController } from '../controllers/billing.controller';
import { authenticateJWT, authorizeRole } from '../middleware/auth';

const router = Router();
const controller = new BillingController();

router.post('/generate', authenticateJWT, authorizeRole(['ADMIN']), (req, res) => controller.generateInvoices(req, res));
router.get('/invoices/:id', authenticateJWT, (req, res) => controller.getInvoiceById(req, res));
router.post('/pay', authenticateJWT, (req, res) => controller.pay(req, res));

export default router;
