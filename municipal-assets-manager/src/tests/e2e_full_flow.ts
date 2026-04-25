import { AssetService } from '../application/services/asset.service';
import { TenantService } from '../application/services/tenant.service';
import { LeaseService } from '../application/services/lease.service';
import { InvoiceService } from '../application/services/invoice.service';
import { PaymentService } from '../application/services/payment.service';
import { UserService } from '../application/services/user.service';
import { ReportingService } from '../application/services/reporting.service';

async function fullFlow() {
  const assetService = new AssetService();
  const tenantService = new TenantService();
  const leaseService = new LeaseService();
  const invoiceService = new InvoiceService();
  const paymentService = new PaymentService();
  const userService = new UserService();
  const reportingService = new ReportingService();

  try {
    console.log('--- Starting Full Flow Integration Test ---');

    // 1. Create Admin User
    const admin = await userService.register({
        email: `admin-${Date.now()}@example.com`,
        password: 'admin-password',
        name: 'Admin User',
        role: 'ADMIN'
    });
    console.log('Step 1: Admin user created');

    // 2. Create Asset
    const asset = await assetService.create({
        name: 'Commercial Space A1',
        type: 'COMMERCIAL',
        location: 'Algiers Center',
        status: 'AVAILABLE'
    });
    console.log('Step 2: Asset created');

    // 3. Create Tenant
    const tenant = await tenantService.create({
        name: 'Sarl Algeria Business',
        phone: '021112233',
        address: '123 Business Rd',
        type: 'BUSINESS'
    });
    console.log('Step 3: Tenant created');

    // 4. Create Lease (Pending)
    const lease = await leaseService.create({
        assetId: asset.id,
        tenantId: tenant.id,
        startDate: new Date(),
        endDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
        amount: 150000
    });
    console.log('Step 4: Lease created (PENDING)');

    // 5. Approve Lease
    await leaseService.approve(lease.id, admin.id);
    console.log('Step 5: Lease approved (ACTIVE)');

    // 6. Generate Invoice
    const invoices = await invoiceService.generateMonthlyInvoices();
    const myInvoice = invoices.find(i => i.leaseId === lease.id);
    if (!myInvoice) throw new Error('Invoice not generated');
    console.log('Step 6: Monthly invoice generated');

    // 7. Make Payment
    await paymentService.processPayment({
        invoiceId: myInvoice.id,
        amount: 150000,
        method: 'TRANSFER',
        reference: 'TRX-999'
    });
    console.log('Step 7: Full payment processed');

    // 8. Verify Dashboard Stats
    const stats = await reportingService.getDashboardStats();
    console.log('Step 8: Final Dashboard Stats:', JSON.stringify(stats, null, 2));

    if (stats.assets.total >= 1 && stats.financials.totalRevenue >= 150000) {
        console.log('--- Full Flow Integration Test Passed ---');
        process.exit(0);
    } else {
        throw new Error('Stats verification failed');
    }

  } catch (error) {
    console.error('Integration Test Failed:', error);
    process.exit(1);
  }
}

fullFlow();
