import { z } from 'zod';

export const CreateLeaseSchema = z.object({
  assetId: z.string().uuid(),
  tenantId: z.string().uuid(),
  startDate: z.coerce.date(),
  endDate: z.coerce.date(),
  amount: z.number().positive(),
});

export type CreateLeaseDto = z.infer<typeof CreateLeaseSchema>;

export const UpdateLeaseSchema = CreateLeaseSchema.partial().extend({
    status: z.enum(['PENDING', 'ACTIVE', 'TERMINATED', 'EXPIRED']).optional(),
    approvedBy: z.string().optional(),
});
export type UpdateLeaseDto = z.infer<typeof UpdateLeaseSchema>;
