import { z } from 'zod';

export const CreateUserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
  name: z.string().min(2),
  role: z.enum(['ADMIN', 'AGENT']).default('AGENT'),
});

export type CreateUserDto = z.infer<typeof CreateUserSchema>;

export const LoginSchema = z.object({
  email: z.string().email(),
  password: z.string(),
});

export type LoginDto = z.infer<typeof LoginSchema>;
