import { AssetService } from '../application/services/asset.service';
import { TenantService } from '../application/services/tenant.service';

async function testCRUD() {
  const assetService = new AssetService();
  const tenantService = new TenantService();

  try {
    console.log('--- Starting CRUD Test ---');

    // 1. Asset CRUD
    const asset = await assetService.create({
      name: 'Central Market Shop #1',
      description: 'A shop in the central market',
      type: 'SHOP',
      location: 'Algiers Center'
    });
    console.log('Asset created:', asset.name);

    const updatedAsset = await assetService.update(asset.id, { status: 'MAINTENANCE' });
    console.log('Asset updated, new status:', updatedAsset.status);

    // 2. Tenant CRUD
    const tenant = await tenantService.create({
      name: 'Mohamed Brahimi',
      phone: '0555123456',
      address: 'Didouche Mourad St, Algiers',
      email: 'mohamed@example.com',
      type: 'INDIVIDUAL'
    });
    console.log('Tenant created:', tenant.name);

    const foundTenant = await tenantService.findById(tenant.id);
    if (foundTenant?.name === 'Mohamed Brahimi') {
      console.log('Tenant findById passed');
    }

    console.log('--- CRUD Test Passed ---');
    process.exit(0);
  } catch (error) {
    console.error('CRUD Test Failed:', error);
    process.exit(1);
  }
}

testCRUD();
