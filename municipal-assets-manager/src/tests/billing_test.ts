import { LeaseService } from '../application/services/lease.service';
import { AssetService } from '../application/services/asset.service';
import { TenantService } from '../application/services/tenant.service';
import { InvoiceService } from '../application/services/invoice.service';
import { PaymentService } from '../application/services/payment.service';

async function testBilling() {
  const leaseService = new LeaseService();
  const assetService = new AssetService();
  const tenantService = new TenantService();
  const invoiceService = new InvoiceService();
  const paymentService = new PaymentService();

  try {
    console.log('--- Starting Billing Test ---');

    // 1. Setup Active Lease
    const asset = await assetService.create({ name: 'Shop #10', type: 'SHOP', location: 'Oran' });
    const tenant = await tenantService.create({ name: 'Ahmed', phone: '0661000000', address: 'Oran', type: 'INDIVIDUAL' });
    const lease = await leaseService.create({
      assetId: asset.id,
      tenantId: tenant.id,
      startDate: new Date(),
      endDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
      amount: 20000
    });

    // Approve to make it active
    await leaseService.approve(lease.id, 'system-admin');
    console.log('Active lease created');

    // 2. Generate Invoices
    const invoices = await invoiceService.generateMonthlyInvoices();
    const myInvoice = invoices.find(i => i.leaseId === lease.id);
    if (!myInvoice) throw new Error('Invoice not generated for active lease');
    console.log('Invoice generated, status:', myInvoice.status);

    // 3. Process Partial Payment
    await paymentService.processPayment({
      invoiceId: myInvoice.id,
      amount: 10000,
      method: 'CASH'
    });

    let updatedInvoice = await invoiceService.findById(myInvoice.id);
    if (updatedInvoice?.status === 'PARTIAL') {
      console.log('Partial payment processed correctly');
    } else {
      throw new Error(`Expected PARTIAL, got ${updatedInvoice?.status}`);
    }

    // 4. Process Full Payment
    await paymentService.processPayment({
      invoiceId: myInvoice.id,
      amount: 10000,
      method: 'TRANSFER'
    });

    updatedInvoice = await invoiceService.findById(myInvoice.id);
    if (updatedInvoice?.status === 'PAID') {
      console.log('Full payment processed correctly, status is PAID');
    } else {
      throw new Error(`Expected PAID, got ${updatedInvoice?.status}`);
    }

    console.log('--- Billing Test Passed ---');
    process.exit(0);
  } catch (error) {
    console.error('Billing Test Failed:', error);
    process.exit(1);
  }
}

testBilling();
