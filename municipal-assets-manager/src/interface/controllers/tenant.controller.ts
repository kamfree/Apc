import { Request, Response } from 'express';
import { TenantService } from '../../application/services/tenant.service';

const tenantService = new TenantService();

export class TenantController {
  async create(req: Request, res: Response) {
    try {
      const tenant = await tenantService.create(req.body);
      res.status(201).json({ success: true, data: tenant });
    } catch (error: any) {
      res.status(400).json({ success: false, error: error.message });
    }
  }

  async getAll(req: Request, res: Response) {
    const tenants = await tenantService.findAll();
    res.json({ success: true, data: tenants });
  }

  async getById(req: Request, res: Response) {
    const id = req.params.id as string;
    const tenant = await tenantService.findById(id);
    if (!tenant) return res.status(404).json({ success: false, error: 'Tenant not found' });
    res.json({ success: true, data: tenant });
  }

  async update(req: Request, res: Response) {
    try {
      const id = req.params.id as string;
      const tenant = await tenantService.update(id, req.body);
      res.json({ success: true, data: tenant });
    } catch (error: any) {
      res.status(400).json({ success: false, error: error.message });
    }
  }
}
