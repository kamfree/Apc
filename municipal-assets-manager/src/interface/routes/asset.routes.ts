import { Router } from 'express';
import { AssetController } from '../controllers/asset.controller';
import { authenticateJWT, authorizeRole } from '../middleware/auth';

const router = Router();
const controller = new AssetController();

router.get('/', authenticateJWT, (req, res) => controller.getAll(req, res));
router.get('/:id', authenticateJWT, (req, res) => controller.getById(req, res));
router.post('/', authenticateJWT, authorizeRole(['ADMIN']), (req, res) => controller.create(req, res));
router.put('/:id', authenticateJWT, authorizeRole(['ADMIN']), (req, res) => controller.update(req, res));

export default router;
