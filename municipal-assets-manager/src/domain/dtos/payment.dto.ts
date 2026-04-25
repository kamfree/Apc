import { z } from 'zod';

export const CreatePaymentSchema = z.object({
  invoiceId: z.string().uuid(),
  amount: z.number().positive(),
  method: z.enum(['CASH', 'CHECK', 'TRANSFER']),
  reference: z.string().optional(),
});

export type CreatePaymentDto = z.infer<typeof CreatePaymentSchema>;
