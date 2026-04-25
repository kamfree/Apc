import prisma from '../../infrastructure/prisma';
import { CreateLeaseDto, UpdateLeaseDto } from '../../domain/dtos/lease.dto';

export class LeaseService {
  async create(data: CreateLeaseDto) {
    // 1. Check for overlapping leases for the same asset
    const overlappingLease = await prisma.lease.findFirst({
      where: {
        assetId: data.assetId,
        status: { in: ['PENDING', 'ACTIVE'] },
        OR: [
          {
            startDate: { lte: data.endDate },
            endDate: { gte: data.startDate },
          },
        ],
      },
    });

    if (overlappingLease) {
      throw new Error('Overlapping lease exists for this asset and period.');
    }

    // 2. Create the lease (default status is PENDING)
    return prisma.lease.create({
      data: {
        ...data,
        status: 'PENDING',
      },
    });
  }

  async approve(id: string, userId: string) {
    const lease = await prisma.lease.findUnique({ where: { id } });
    if (!lease) throw new Error('Lease not found');
    if (lease.status !== 'PENDING') throw new Error('Lease is not in PENDING status');

    return prisma.$transaction(async (tx) => {
      const updatedLease = await tx.lease.update({
        where: { id },
        data: {
          status: 'ACTIVE',
          approvedBy: userId,
        },
      });

      // Update asset status to LEASED
      await tx.asset.update({
        where: { id: lease.assetId },
        data: { status: 'LEASED' },
      });

      return updatedLease;
    });
  }

  async findAll() {
    return prisma.lease.findMany({ include: { asset: true, tenant: true } });
  }

  async findById(id: string) {
    return prisma.lease.findUnique({
      where: { id },
      include: { asset: true, tenant: true, invoices: true },
    });
  }
}
