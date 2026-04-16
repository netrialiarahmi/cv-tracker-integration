/**
 * Microsoft Planner Sync Script
 * Uses Playwright to login, export Excel, and sync data
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
require('dotenv').config();

const { parseExcelCSV, validateColumns } = require('./excel-parser');
const { transformData, loadExistingData, saveData } = require('./data-transformer');

// Configuration
const MICROSOFT_EMAIL = process.env.MICROSOFT_EMAIL;
const MICROSOFT_PASSWORD = process.env.MICROSOFT_PASSWORD;
const PLANNER_URL = process.env.PLANNER_URL;
const DATA_FILE = process.env.DATA_FILE || 'data/hiring-data.json';
const DOWNLOAD_DIR = path.join(__dirname, '..', 'downloads');

// Ensure downloads directory exists
if (!fs.existsSync(DOWNLOAD_DIR)) {
  fs.mkdirSync(DOWNLOAD_DIR, { recursive: true });
}

/**
 * Validate environment variables
 */
function validateEnvironment() {
  const required = ['MICROSOFT_EMAIL', 'MICROSOFT_PASSWORD', 'PLANNER_URL'];
  const missing = required.filter(key => !process.env[key]);
  
  if (missing.length > 0) {
    console.error('❌ Missing required environment variables:', missing.join(', '));
    console.error('Please set them in .env file or environment');
    process.exit(1);
  }
  
  console.log('✅ Environment variables validated');
}

/**
 * Login to Microsoft account
 * @param {Page} page - Playwright page
 */
async function loginMicrosoft(page) {
  console.log('🔐 Logging in to Microsoft...');
  
  try {
    // Wait for email input
    await page.waitForSelector('input[type="email"]', { timeout: 30000 });
    await page.fill('input[type="email"]', MICROSOFT_EMAIL);
    console.log('  ✓ Email entered');
    
    // Click next
    await page.click('input[type="submit"]');
    
    // Wait for password input
    await page.waitForSelector('input[type="password"]', { timeout: 30000 });
    await page.fill('input[type="password"]', MICROSOFT_PASSWORD);
    console.log('  ✓ Password entered');
    
    // Click sign in
    await page.click('input[type="submit"]');
    
    // Handle "Stay signed in?" prompt
    try {
      await page.waitForSelector('input[type="submit"]', { timeout: 10000 });
      // Click "Yes" to stay signed in
      await page.click('input[type="submit"]');
      console.log('  ✓ Accepted stay signed in');
    } catch (e) {
      console.log('  ℹ No "stay signed in" prompt');
    }
    
    console.log('✅ Login successful');
    
  } catch (error) {
    console.error('❌ Login failed:', error.message);
    throw error;
  }
}

/**
 * Export Planner to Excel
 * @param {Page} page - Playwright page
 * @returns {string} Path to downloaded file
 */
async function exportPlannerToExcel(page) {
  console.log('📥 Navigating to Planner...');
  
  try {
    // Navigate to Planner
    await page.goto(PLANNER_URL, { waitUntil: 'domcontentloaded', timeout: 120000 });
    console.log('  ✓ Planner page loaded');
    
    // Wait for page to be fully loaded
    await page.waitForTimeout(8000);
    
    // Step 1: Find and click the dropdown menu button next to the plan title
    console.log('  🔍 Looking for dropdown menu button...');
    const dropdownSelectors = [
      'button[aria-label*="Plan options"]',
      'button[title*="Plan options"]',
      'button[aria-label*="More options"]',
      'h1 + button',  // Button next to h1 heading
      '[role="button"][aria-label*="plan"]',
      'button[data-testid*="plan-menu"]',
      'button[id*="plan-menu"]',
      'button[aria-label*="TALENT ACQUISITION"]'  // Fallback to specific plan name
    ];
    
    let dropdownButton = null;
    let foundSelector = null;
    for (const selector of dropdownSelectors) {
      try {
        dropdownButton = await page.waitForSelector(selector, { timeout: 5000 });
        if (dropdownButton) {
          foundSelector = selector;
          console.log(`  ✓ Found dropdown button with selector: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!dropdownButton) {
      // Take a screenshot for debugging
      const screenshotPath = path.join(DOWNLOAD_DIR, `debug-no-dropdown-${Date.now()}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.error(`  ❌ Debug screenshot saved: ${screenshotPath}`);
      throw new Error('Dropdown menu button not found. Please check the Planner URL and page structure. A debug screenshot has been saved.');
    }
    
    // Click the dropdown button to open the menu
    await dropdownButton.click();
    console.log('  ✓ Dropdown menu button clicked');
    
    // Wait for the dropdown menu to open by waiting for menu items to appear
    try {
      await page.waitForSelector('[role="menu"], [role="menuitem"], ul[role="presentation"]', { timeout: 5000 });
      console.log('  ✓ Dropdown menu opened');
    } catch (e) {
      // Fallback to time-based wait if menu selector not found
      await page.waitForTimeout(2000);
      console.log('  ✓ Waited for dropdown menu to open');
    }
    
    // Step 2: Look for "Export plan to Excel" option in the dropdown menu
    console.log('  🔍 Looking for Export plan to Excel option...');
    const exportSelectors = [
      'button:has-text("Export plan to Excel")',
      'div:has-text("Export plan to Excel")',
      '[role="menuitem"]:has-text("Export")',
      'button:has-text("Export")',
      'button[aria-label*="Export"]',
      '[data-testid*="export"]',
      'button[title*="Export"]',
      'li:has-text("Export")'
    ];
    
    let exportButton = null;
    let exportSelector = null;
    for (const selector of exportSelectors) {
      try {
        exportButton = await page.waitForSelector(selector, { timeout: 5000 });
        if (exportButton) {
          exportSelector = selector;
          console.log(`  ✓ Found export option with selector: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!exportButton) {
      // Take a screenshot for debugging
      const screenshotPath = path.join(DOWNLOAD_DIR, `debug-no-export-${Date.now()}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.error(`  ❌ Debug screenshot saved: ${screenshotPath}`);
      throw new Error('Export plan to Excel option not found in dropdown menu. Please check the page structure. A debug screenshot has been saved.');
    }
    
    // Setup download handler before clicking
    const downloadPromise = page.waitForEvent('download', { timeout: 60000 });
    
    // Click the export option
    await exportButton.click();
    console.log('  ✓ Export plan to Excel clicked');
    
    // Wait for download
    const download = await downloadPromise;
    console.log('  ✓ Download started');
    
    // Save file with .xlsx extension
    const fileName = `planner-export-${Date.now()}.xlsx`;
    const filePath = path.join(DOWNLOAD_DIR, fileName);
    await download.saveAs(filePath);
    
    console.log(`✅ File downloaded: ${filePath}`);
    return filePath;
    
  } catch (error) {
    console.error('❌ Export failed:', error.message);
    throw error;
  }
}

/**
 * Main sync function
 */
async function syncPlanner() {
  console.log('🚀 Starting Microsoft Planner sync...\n');
  
  // Validate environment
  validateEnvironment();
  
  let browser;
  let downloadedFile;
  
  try {
    // Launch browser
    console.log('🌐 Launching browser...');
    browser = await chromium.launch({
      headless: true,
      args: ['--disable-blink-features=AutomationControlled']
    });
    
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    });
    
    const page = await context.newPage();
    console.log('✅ Browser launched\n');
    
    // Login
    await page.goto('https://login.microsoftonline.com');
    await loginMicrosoft(page);
    console.log('');
    
    // Export data
    downloadedFile = await exportPlannerToExcel(page);
    console.log('');
    
    // Close browser
    await browser.close();
    console.log('✅ Browser closed\n');
    
    // Parse Excel/CSV file
    const csvData = await parseExcelCSV(downloadedFile);
    
    // Validate columns
    if (!validateColumns(csvData)) {
      throw new Error('CSV validation failed');
    }
    console.log('');
    
    // Load existing data
    const dataFilePath = path.join(__dirname, '..', DATA_FILE);
    const existingData = loadExistingData(dataFilePath);
    console.log('');
    
    // Transform data
    const transformedData = transformData(csvData, existingData);
    console.log('');
    
    // Save data
    saveData(transformedData, dataFilePath);
    console.log('');
    
    // Clean up downloaded file
    try {
      fs.unlinkSync(downloadedFile);
      console.log('🗑️  Cleaned up temporary download file\n');
    } catch (e) {
      console.warn('⚠️  Could not delete temporary file:', e.message);
    }
    
    console.log('✅ Sync completed successfully!');
    console.log(`📊 Total entries: ${transformedData.length}`);
    console.log(`📅 Last updated: ${new Date().toLocaleString('en-US', { timeZone: 'Asia/Jakarta' })}`);
    
  } catch (error) {
    console.error('\n❌ Sync failed:', error.message);
    console.error(error.stack);
    
    // Clean up browser if still open
    if (browser) {
      try {
        await browser.close();
      } catch (e) {
        // Ignore
      }
    }
    
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  syncPlanner();
}

module.exports = { syncPlanner };
