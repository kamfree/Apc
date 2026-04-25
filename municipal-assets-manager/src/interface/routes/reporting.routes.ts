import { Router } from 'express';
import { ReportingController } from '../controllers/reporting.controller';
import { authenticateJWT, authorizeRole } from '../middleware/auth';

const router = Router();
const controller = new ReportingController();

router.get('/stats', authenticateJWT, (req, res) => controller.getStats(req, res));
router.get('/revenue-by-type', authenticateJWT, (req, res) => controller.getRevenueByType(req, res));

export default router;
