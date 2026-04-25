import { test, expect } from '@playwright/test';

test('has title and dashboard link', async ({ page }) => {
  await page.goto('http://localhost:3000');
  const heading = page.getByRole('heading', { name: /Municipal Assets Manager/ });
  await expect(heading).toBeVisible();
  const dashboardLink = page.getByRole('link', { name: /Dashboard/ });
  await expect(dashboardLink).toBeVisible();
});

test('can navigate to dashboard', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.getByRole('link', { name: /Dashboard/ }).click();
  await expect(page).toHaveURL(/.*dashboard/);
  await expect(page.getByText('Municipal Assets Dashboard')).toBeVisible();
});
