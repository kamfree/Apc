import prisma from '../../infrastructure/prisma';
import { CreateTenantDto, UpdateTenantDto } from '../../domain/dtos/tenant.dto';

export class TenantService {
  async create(data: CreateTenantDto) {
    return prisma.tenant.create({ data });
  }

  async findAll() {
    return prisma.tenant.findMany();
  }

  async findById(id: string) {
    return prisma.tenant.findUnique({ where: { id } });
  }

  async update(id: string, data: UpdateTenantDto) {
    return prisma.tenant.update({
      where: { id },
      data,
    });
  }

  async delete(id: string) {
    return prisma.tenant.delete({ where: { id } });
  }
}
