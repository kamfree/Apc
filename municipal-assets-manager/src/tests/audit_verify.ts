import { AuditLogService } from '../application/services/audit.service';
import { AssetService } from '../application/services/asset.service';
import prisma from '../infrastructure/prisma';

async function testAudit() {
  const auditService = new AuditLogService();
  const assetService = new AssetService();

  try {
    console.log('--- Starting Audit Test ---');

    // 1. Perform an action
    const asset = await assetService.create({
      name: 'Audit Test Asset',
      type: 'BUILDING',
      location: 'Constantine'
    });

    // 2. Log the action manually (in a real scenario, this would be in the service or middleware)
    await auditService.log({
      action: 'CREATE',
      entityName: 'Asset',
      entityId: asset.id,
      changes: { name: asset.name, type: asset.type }
    });
    console.log('Action logged');

    // 3. Verify audit log existence
    const logs = await auditService.findByEntity('Asset', asset.id);
    if (logs.length > 0 && logs[0].action === 'CREATE') {
      console.log('Audit log verified in database');
    } else {
      throw new Error('Audit log not found or incorrect');
    }

    console.log('--- Audit Test Passed ---');
    process.exit(0);
  } catch (error) {
    console.error('Audit Test Failed:', error);
    process.exit(1);
  }
}

testAudit();
