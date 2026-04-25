import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import prisma from '../../infrastructure/prisma';
import { CreateUserDto, LoginDto } from '../../domain/dtos/user.dto';

const JWT_SECRET = process.env.JWT_SECRET || 'dev-fallback-secret';

export class UserService {
  async register(data: CreateUserDto) {
    const hashedPassword = await bcrypt.hash(data.password, 10);
    const user = await prisma.user.create({
      data: {
        ...data,
        password: hashedPassword,
      },
    });
    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword;
  }

  async login(data: LoginDto) {
    const user = await prisma.user.findUnique({
      where: { email: data.email },
    });

    if (!user) {
      throw new Error('Invalid credentials');
    }

    const isValid = await bcrypt.compare(data.password, user.password);
    if (!isValid) {
      throw new Error('Invalid credentials');
    }

    const token = jwt.sign(
      { id: user.id, email: user.email, role: user.role },
      JWT_SECRET,
      { expiresIn: '24h' }
    );

    return { token, user: { id: user.id, email: user.email, role: user.role, name: user.name } };
  }

  async findById(id: string) {
    return prisma.user.findUnique({
      where: { id },
      select: { id: true, email: true, name: true, role: true },
    });
  }
}
