import prisma from '../../infrastructure/prisma';
import { CreatePaymentDto } from '../../domain/dtos/payment.dto';

export class PaymentService {
  async processPayment(data: CreatePaymentDto) {
    return prisma.$transaction(async (tx) => {
      // 1. Get invoice
      const invoice = await tx.invoice.findUnique({
        where: { id: data.invoiceId },
        include: { payments: true },
      });

      if (!invoice) throw new Error('Invoice not found');
      if (invoice.status === 'PAID') throw new Error('Invoice already paid');

      // 2. Create payment record
      const payment = await tx.payment.create({
        data: {
          ...data,
          paymentDate: new Date(),
        },
      });

      // 3. Reconcile invoice status
      const totalPaid = invoice.payments.reduce((sum, p) => sum + p.amount, 0) + data.amount;

      let newStatus = 'PARTIAL';
      if (totalPaid >= invoice.amount) {
        newStatus = 'PAID';
      }

      await tx.invoice.update({
        where: { id: invoice.id },
        data: { status: newStatus },
      });

      return payment;
    });
  }

  async findByInvoiceId(invoiceId: string) {
    return prisma.payment.findMany({ where: { invoiceId } });
  }
}
