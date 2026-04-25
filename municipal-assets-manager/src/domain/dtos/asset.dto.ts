import { z } from 'zod';

export const CreateAssetSchema = z.object({
  name: z.string().min(2),
  description: z.string().optional(),
  type: z.string(),
  location: z.string(),
  status: z.enum(['AVAILABLE', 'LEASED', 'MAINTENANCE']).default('AVAILABLE').optional(),
});

export type CreateAssetDto = z.infer<typeof CreateAssetSchema>;

export const UpdateAssetSchema = CreateAssetSchema.partial();
export type UpdateAssetDto = z.infer<typeof UpdateAssetSchema>;
