import { Request, Response } from 'express';
import { LeaseService } from '../../application/services/lease.service';
import { AuthRequest } from '../middleware/auth';

const leaseService = new LeaseService();

export class LeaseController {
  async create(req: Request, res: Response) {
    try {
      const lease = await leaseService.create(req.body);
      res.status(201).json({ success: true, data: lease });
    } catch (error: any) {
      res.status(400).json({ success: false, error: error.message });
    }
  }

  async getAll(req: Request, res: Response) {
    const leases = await leaseService.findAll();
    res.json({ success: true, data: leases });
  }

  async getById(req: Request, res: Response) {
    const id = req.params.id as string;
    const lease = await leaseService.findById(id);
    if (!lease) return res.status(404).json({ success: false, error: 'Lease not found' });
    res.json({ success: true, data: lease });
  }

  async approve(req: AuthRequest, res: Response) {
    try {
      const id = req.params.id as string;
      const userId = req.user?.id as string;
      const lease = await leaseService.approve(id, userId);
      res.json({ success: true, data: lease });
    } catch (error: any) {
      res.status(400).json({ success: false, error: error.message });
    }
  }
}
