import { Router } from 'express';
import { LeaseController } from '../controllers/lease.controller';
import { authenticateJWT, authorizeRole } from '../middleware/auth';

const router = Router();
const controller = new LeaseController();

router.get('/', authenticateJWT, (req, res) => controller.getAll(req, res));
router.get('/:id', authenticateJWT, (req, res) => controller.getById(req, res));
router.post('/', authenticateJWT, (req, res) => controller.create(req, res));
router.post('/:id/approve', authenticateJWT, authorizeRole(['ADMIN']), (req, res) => controller.approve(req, res));

export default router;
