import { Router } from 'express';
import { UserController } from '../controllers/user.controller';
import { authenticateJWT } from '../middleware/auth';

const router = Router();
const controller = new UserController();

router.post('/register', (req, res) => controller.register(req, res));
router.post('/login', (req, res) => controller.login(req, res));
router.get('/me', authenticateJWT, (req, res) => controller.getMe(req, res));

export default router;
