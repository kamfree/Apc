import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import userRoutes from './routes/user.routes';
import assetRoutes from './routes/asset.routes';
import tenantRoutes from './routes/tenant.routes';
import leaseRoutes from './routes/lease.routes';
import billingRoutes from './routes/billing.routes';
import reportingRoutes from './routes/reporting.routes';

dotenv.config();

const app = express();
const port = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.use('/api/users', userRoutes);
app.use('/api/assets', assetRoutes);
app.use('/api/tenants', tenantRoutes);
app.use('/api/leases', leaseRoutes);
app.use('/api/billing', billingRoutes);
app.use('/api/reporting', reportingRoutes);

app.get('/health', (req, res) => {
  res.json({ success: true, status: 'OK', timestamp: new Date().toISOString() });
});

if (require.main === module) {
  app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
  });
}

export default app;
