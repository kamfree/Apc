import prisma from '../../infrastructure/prisma';

export class ReportingService {
  async getDashboardStats() {
    const totalAssets = await prisma.asset.count();
    const leasedAssets = await prisma.asset.count({ where: { status: 'LEASED' } });
    const availableAssets = await prisma.asset.count({ where: { status: 'AVAILABLE' } });

    const occupancyRate = totalAssets > 0 ? (leasedAssets / totalAssets) * 100 : 0;

    const totalRevenue = await prisma.payment.aggregate({
      _sum: {
        amount: true,
      },
    });

    const pendingInvoicesAmount = await prisma.invoice.aggregate({
      where: { status: { in: ['UNPAID', 'PARTIAL'] } },
      _sum: {
        amount: true,
      },
    });

    return {
      assets: {
        total: totalAssets,
        leased: leasedAssets,
        available: availableAssets,
        occupancyRate: Math.round(occupancyRate * 100) / 100,
      },
      financials: {
        totalRevenue: totalRevenue._sum.amount || 0,
        pendingInvoicesAmount: pendingInvoicesAmount._sum.amount || 0,
      }
    };
  }

  async getRevenueByType() {
     // Complex query simplified for SQLite/Prisma
     const assets = await prisma.asset.findMany({
         include: {
             leases: {
                 include: {
                     invoices: {
                         include: {
                             payments: true
                         }
                     }
                 }
             }
         }
     });

     const revenueByType: Record<string, number> = {};

     assets.forEach(asset => {
         let typeRevenue = 0;
         asset.leases.forEach(lease => {
             lease.invoices.forEach(invoice => {
                 invoice.payments.forEach(payment => {
                     typeRevenue += payment.amount;
                 });
             });
         });
         revenueByType[asset.type] = (revenueByType[asset.type] || 0) + typeRevenue;
     });

     return revenueByType;
  }
}
