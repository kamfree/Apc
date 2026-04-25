import prisma from '../../infrastructure/prisma';

export class InvoiceService {
  async generateMonthlyInvoices() {
    const activeLeases = await prisma.lease.findMany({
      where: { status: 'ACTIVE' },
    });

    const results = [];
    const now = new Date();
    const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    const dueDate = new Date(now.getFullYear(), now.getMonth(), 15); // Due on 15th

    for (const lease of activeLeases) {
      // Check if invoice already exists for this month and lease
      const existingInvoice = await prisma.invoice.findFirst({
        where: {
          leaseId: lease.id,
          createdAt: {
            gte: firstDayOfMonth,
          },
        },
      });

      if (!existingInvoice) {
        const invoice = await prisma.invoice.create({
          data: {
            leaseId: lease.id,
            amount: lease.amount,
            dueDate: dueDate,
            status: 'UNPAID',
          },
        });
        results.push(invoice);
      }
    }
    return results;
  }

  async findById(id: string) {
    return prisma.invoice.findUnique({
      where: { id },
      include: { lease: { include: { asset: true, tenant: true } }, payments: true },
    });
  }
}
