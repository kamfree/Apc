import prisma from '../../infrastructure/prisma';

export interface AuditData {
  userId?: string;
  action: string;
  entityName: string;
  entityId: string;
  changes?: any;
}

export class AuditLogService {
  async log(data: AuditData) {
    return prisma.auditLog.create({
      data: {
        userId: data.userId,
        action: data.action,
        entityName: data.entityName,
        entityId: data.entityId,
        changes: data.changes ? JSON.stringify(data.changes) : null,
      },
    });
  }

  async findByEntity(entityName: string, entityId: string) {
    return prisma.auditLog.findMany({
      where: { entityName, entityId },
      orderBy: { timestamp: 'desc' },
    });
  }
}
