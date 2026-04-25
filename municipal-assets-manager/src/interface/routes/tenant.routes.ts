import { Router } from 'express';
import { TenantController } from '../controllers/tenant.controller';
import { authenticateJWT, authorizeRole } from '../middleware/auth';

const router = Router();
const controller = new TenantController();

router.get('/', authenticateJWT, (req, res) => controller.getAll(req, res));
router.get('/:id', authenticateJWT, (req, res) => controller.getById(req, res));
router.post('/', authenticateJWT, (req, res) => controller.create(req, res));
router.put('/:id', authenticateJWT, (req, res) => controller.update(req, res));

export default router;
