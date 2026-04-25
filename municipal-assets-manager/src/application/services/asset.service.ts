import prisma from '../../infrastructure/prisma';
import { CreateAssetDto, UpdateAssetDto } from '../../domain/dtos/asset.dto';

export class AssetService {
  async create(data: CreateAssetDto) {
    return prisma.asset.create({ data });
  }

  async findAll() {
    return prisma.asset.findMany();
  }

  async findById(id: string) {
    return prisma.asset.findUnique({ where: { id } });
  }

  async update(id: string, data: UpdateAssetDto) {
    return prisma.asset.update({
      where: { id },
      data,
    });
  }

  async delete(id: string) {
    return prisma.asset.delete({ where: { id } });
  }
}
