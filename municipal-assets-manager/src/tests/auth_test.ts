import { UserService } from '../application/services/user.service';
import jwt from 'jsonwebtoken';

async function testAuth() {
  const userService = new UserService();
  const JWT_SECRET = process.env.JWT_SECRET || 'super-secret-key';

  try {
    console.log('--- Starting Auth Test ---');

    // 1. Register a user
    const userData = {
      email: `test-${Date.now()}@example.com`,
      password: 'password123',
      name: 'Test User',
      role: 'ADMIN' as const
    };

    const user = await userService.register(userData);
    console.log('User registered:', user.email);

    // 2. Login
    const loginResult = await userService.login({
      email: userData.email,
      password: userData.password
    });
    console.log('Login successful, token generated');

    // 3. Verify Token
    const decoded = jwt.verify(loginResult.token, JWT_SECRET) as any;
    if (decoded.email === userData.email && decoded.role === 'ADMIN') {
      console.log('Token verification passed');
    } else {
      throw new Error('Token verification failed');
    }

    console.log('--- Auth Test Passed ---');
    process.exit(0);
  } catch (error) {
    console.error('Auth Test Failed:', error);
    process.exit(1);
  }
}

testAuth();
