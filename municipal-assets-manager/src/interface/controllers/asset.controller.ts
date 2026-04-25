import { Request, Response } from 'express';
import { AssetService } from '../../application/services/asset.service';

const assetService = new AssetService();

export class AssetController {
  async create(req: Request, res: Response) {
    try {
      const asset = await assetService.create(req.body);
      res.status(201).json({ success: true, data: asset });
    } catch (error: any) {
      res.status(400).json({ success: false, error: error.message });
    }
  }

  async getAll(req: Request, res: Response) {
    const assets = await assetService.findAll();
    res.json({ success: true, data: assets });
  }

  async getById(req: Request, res: Response) {
    const id = req.params.id as string;
    const asset = await assetService.findById(id);
    if (!asset) return res.status(404).json({ success: false, error: 'Asset not found' });
    res.json({ success: true, data: asset });
  }

  async update(req: Request, res: Response) {
    try {
      const id = req.params.id as string;
      const asset = await assetService.update(id, req.body);
      res.json({ success: true, data: asset });
    } catch (error: any) {
      res.status(400).json({ success: false, error: error.message });
    }
  }
}
