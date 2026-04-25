import { z } from 'zod';

export const CreateTenantSchema = z.object({
  name: z.string().min(2),
  email: z.string().email().optional(),
  phone: z.string(),
  address: z.string(),
  type: z.enum(['INDIVIDUAL', 'BUSINESS']).default('INDIVIDUAL'),
});

export type CreateTenantDto = z.infer<typeof CreateTenantSchema>;

export const UpdateTenantSchema = CreateTenantSchema.partial();
export type UpdateTenantDto = z.infer<typeof UpdateTenantSchema>;
