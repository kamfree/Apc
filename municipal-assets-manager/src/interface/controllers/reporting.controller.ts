import { Request, Response } from 'express';
import { ReportingService } from '../../application/services/reporting.service';

const reportingService = new ReportingService();

export class ReportingController {
  async getStats(req: Request, res: Response) {
    const stats = await reportingService.getDashboardStats();
    res.json({ success: true, data: stats });
  }

  async getRevenueByType(req: Request, res: Response) {
    const revenue = await reportingService.getRevenueByType();
    res.json({ success: true, data: revenue });
  }
}
