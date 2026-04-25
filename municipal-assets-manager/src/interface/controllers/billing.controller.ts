import { Request, Response } from 'express';
import { InvoiceService } from '../../application/services/invoice.service';
import { PaymentService } from '../../application/services/payment.service';

const invoiceService = new InvoiceService();
const paymentService = new PaymentService();

export class BillingController {
  async generateInvoices(req: Request, res: Response) {
    try {
      const invoices = await invoiceService.generateMonthlyInvoices();
      res.json({ success: true, data: invoices });
    } catch (error: any) {
      res.status(400).json({ success: false, error: error.message });
    }
  }

  async getInvoiceById(req: Request, res: Response) {
    const id = req.params.id as string;
    const invoice = await invoiceService.findById(id);
    if (!invoice) return res.status(404).json({ success: false, error: 'Invoice not found' });
    res.json({ success: true, data: invoice });
  }

  async pay(req: Request, res: Response) {
    try {
      const payment = await paymentService.processPayment(req.body);
      res.status(201).json({ success: true, data: payment });
    } catch (error: any) {
      res.status(400).json({ success: false, error: error.message });
    }
  }
}
