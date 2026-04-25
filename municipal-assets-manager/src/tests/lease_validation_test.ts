import { LeaseService } from '../application/services/lease.service';
import { AssetService } from '../application/services/asset.service';
import { TenantService } from '../application/services/tenant.service';

async function testLeaseValidation() {
  const leaseService = new LeaseService();
  const assetService = new AssetService();
  const tenantService = new TenantService();

  try {
    console.log('--- Starting Lease Validation Test ---');

    // 1. Setup Asset and Tenant
    const asset = await assetService.create({
      name: 'Office B2',
      type: 'OFFICE',
      location: 'El Biar'
    });
    const tenant = await tenantService.create({
      name: 'Tech Corp',
      phone: '021000000',
      address: 'Algiers',
      type: 'BUSINESS'
    });

    // 2. Create first lease
    const startDate1 = new Date('2024-01-01');
    const endDate1 = new Date('2024-12-31');
    const lease1 = await leaseService.create({
      assetId: asset.id,
      tenantId: tenant.id,
      startDate: startDate1,
      endDate: endDate1,
      amount: 50000
    });
    console.log('Lease 1 created');

    // 3. Try to create overlapping lease
    const startDate2 = new Date('2024-06-01');
    const endDate2 = new Date('2025-05-31');
    try {
      await leaseService.create({
        assetId: asset.id,
        tenantId: tenant.id,
        startDate: startDate2,
        endDate: endDate2,
        amount: 60000
      });
      throw new Error('Overlapping lease should not have been created');
    } catch (error: any) {
      if (error.message === 'Overlapping lease exists for this asset and period.') {
        console.log('Validation passed: Overlapping lease blocked correctly');
      } else {
        throw error;
      }
    }

    // 4. Create non-overlapping lease
    const startDate3 = new Date('2025-01-01');
    const endDate3 = new Date('2025-12-31');
    await leaseService.create({
      assetId: asset.id,
      tenantId: tenant.id,
      startDate: startDate3,
      endDate: endDate3,
      amount: 55000
    });
    console.log('Lease 2 (non-overlapping) created');

    console.log('--- Lease Validation Test Passed ---');
    process.exit(0);
  } catch (error) {
    console.error('Lease Validation Test Failed:', error);
    process.exit(1);
  }
}

testLeaseValidation();
