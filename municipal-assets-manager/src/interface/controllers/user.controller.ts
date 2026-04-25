import { Request, Response } from 'express';
import { UserService } from '../../application/services/user.service';

const userService = new UserService();

export class UserController {
  async register(req: Request, res: Response) {
    try {
      const user = await userService.register(req.body);
      res.status(201).json({ success: true, data: user });
    } catch (error: any) {
      res.status(400).json({ success: false, error: error.message });
    }
  }

  async login(req: Request, res: Response) {
    try {
      const result = await userService.login(req.body);
      res.json({ success: true, data: result });
    } catch (error: any) {
      res.status(401).json({ success: false, error: error.message });
    }
  }

  async getMe(req: any, res: Response) {
    const user = await userService.findById(req.user.id);
    res.json({ success: true, data: user });
  }
}
