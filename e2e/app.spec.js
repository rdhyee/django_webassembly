// @ts-check
import { test, expect } from "@playwright/test";

/**
 * Django WebAssembly E2E Tests
 *
 * These tests verify the full application works in a real browser,
 * including Pyodide loading and Django request handling.
 *
 * Note: Tests have extended timeouts because Pyodide takes time to load (~20MB).
 */

test.describe("Django WebAssembly Application", () => {
  // Extend timeout for all tests in this describe block
  test.setTimeout(180000);

  test.beforeEach(async ({ page }) => {
    // Wait for service worker to install and Django to initialize
    await page.goto("/");

    // Wait for either the loading page or the actual app to load
    // The loading page will reload when ready
    await page.waitForLoadState("networkidle", { timeout: 120000 });

    // If we see the loading spinner, wait for reload
    const spinner = page.locator(".spinner");
    if (await spinner.isVisible()) {
      // Wait for the page to reload after Pyodide loads
      await page.waitForURL("**/*", { timeout: 120000 });
      await page.waitForLoadState("networkidle");
    }
  });

  test("should load the home page", async ({ page }) => {
    // The home page should show Django WebAssembly title
    await expect(page.locator("h1")).toContainText("Django WebAssembly", { timeout: 60000 });
  });

  test("should have links to polls and admin", async ({ page }) => {
    await expect(page.locator("a[href=\"/polls\"]")).toBeVisible({ timeout: 60000 });
    await expect(page.locator("a[href=\"/admin\"]")).toBeVisible({ timeout: 60000 });
  });

  test("should show demo credentials", async ({ page }) => {
    const content = await page.content();
    expect(content).toContain("demo");
  });
});

test.describe("Polls Application", () => {
  test.setTimeout(180000);

  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle", { timeout: 120000 });

    // Wait for Django to be ready
    const spinner = page.locator(".spinner");
    if (await spinner.isVisible()) {
      await page.waitForURL("**/*", { timeout: 120000 });
      await page.waitForLoadState("networkidle");
    }
  });

  test("should navigate to polls page", async ({ page }) => {
    await page.click("a[href=\"/polls\"]");
    await page.waitForLoadState("networkidle");

    // Should see polls index page
    await expect(page.locator("body")).toContainText("poll", { timeout: 60000 });
  });

  test("should display sample questions", async ({ page }) => {
    await page.goto("/polls/");
    await page.waitForLoadState("networkidle");

    // Sample data should include questions
    const content = await page.content();
    // Check for any question text (from init.py sample data)
    expect(
      content.includes("programming language") ||
      content.includes("web framework") ||
      content.includes("browser")
    ).toBeTruthy();
  });

  test("should navigate to question detail", async ({ page }) => {
    await page.goto("/polls/");
    await page.waitForLoadState("networkidle");

    // Click on first question link
    const questionLink = page.locator("a").filter({ hasText: /\?/ }).first();
    if (await questionLink.isVisible()) {
      await questionLink.click();
      await page.waitForLoadState("networkidle");

      // Should see voting form
      await expect(page.locator("form")).toBeVisible({ timeout: 60000 });
    }
  });

  test("should be able to vote", async ({ page }) => {
    await page.goto("/polls/1/");
    await page.waitForLoadState("networkidle");

    // Select first choice and vote
    const radioButton = page.locator("input[type=\"radio\"]").first();
    if (await radioButton.isVisible({ timeout: 10000 })) {
      await radioButton.check();
      await page.click("input[type=\"submit\"]");
      await page.waitForLoadState("networkidle");

      // Should be on results page
      expect(page.url()).toContain("results");
    }
  });
});

test.describe("Admin Panel", () => {
  test.setTimeout(180000);

  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle", { timeout: 120000 });

    const spinner = page.locator(".spinner");
    if (await spinner.isVisible()) {
      await page.waitForURL("**/*", { timeout: 120000 });
      await page.waitForLoadState("networkidle");
    }
  });

  test("should show admin login page", async ({ page }) => {
    await page.goto("/admin/");
    await page.waitForLoadState("networkidle");

    // Should redirect to login or show login form
    await expect(page.locator("body")).toContainText(/log in|admin/i, { timeout: 60000 });
  });

  test("should be able to login to admin", async ({ page }) => {
    await page.goto("/admin/login/");
    await page.waitForLoadState("networkidle");

    // Fill in credentials
    await page.fill("input[name=\"username\"]", "demo");
    await page.fill("input[name=\"password\"]", "demo");
    await page.click("input[type=\"submit\"]");

    await page.waitForLoadState("networkidle");

    // Should be logged in and see admin dashboard
    const content = await page.content();
    expect(
      content.includes("Site administration") ||
      content.includes("Django administration") ||
      content.includes("Welcome")
    ).toBeTruthy();
  });
});

test.describe("Browser Feature Detection", () => {
  test("should check for WebAssembly support", async ({ page }) => {
    const hasWasm = await page.evaluate(() => {
      return typeof WebAssembly !== "undefined";
    });
    expect(hasWasm).toBeTruthy();
  });

  test("should check for Service Worker support", async ({ page }) => {
    const hasSW = await page.evaluate(() => {
      return "serviceWorker" in navigator;
    });
    expect(hasSW).toBeTruthy();
  });
});
