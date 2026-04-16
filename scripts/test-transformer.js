/**
 * Test script for data transformation logic
 * Can be used to test transformation without running full Playwright sync
 */

const fs = require('fs');
const path = require('path');
const { parseExcelCSV, validateColumns } = require('./excel-parser');
const { transformData, loadExistingData, saveData } = require('./data-transformer');

async function testTransformation() {
  console.log('🧪 Testing data transformation...\n');
  
  // Check if test CSV or Excel exists
  const testCSVPath = path.join(__dirname, '..', 'downloads', 'test-export.csv');
  const testXLSXPath = path.join(__dirname, '..', 'downloads', 'test-export.xlsx');
  
  let testFilePath = null;
  if (fs.existsSync(testXLSXPath)) {
    testFilePath = testXLSXPath;
  } else if (fs.existsSync(testCSVPath)) {
    testFilePath = testCSVPath;
  }
  
  if (!testFilePath) {
    console.log('ℹ️  No test file found at:', testCSVPath, 'or', testXLSXPath);
    console.log('To test:');
    console.log('1. Export Excel manually from Planner');
    console.log('2. Save as downloads/test-export.xlsx or downloads/test-export.csv');
    console.log('3. Run this script again');
    return;
  }
  
  try {
    // Parse file
    console.log('📄 Parsing test file...');
    const csvData = await parseExcelCSV(testFilePath);
    
    // Validate columns
    if (!validateColumns(csvData)) {
      throw new Error('File validation failed');
    }
    console.log('');
    
    // Load existing data
    const dataFilePath = path.join(__dirname, '..', 'data', 'hiring-data.json');
    console.log('📂 Loading existing data...');
    const existingData = loadExistingData(dataFilePath);
    console.log('');
    
    // Transform data
    console.log('🔄 Transforming data...');
    const transformedData = transformData(csvData, existingData);
    console.log('');
    
    // Save to test output
    const testOutputPath = path.join(__dirname, '..', 'downloads', 'test-output.json');
    console.log('💾 Saving test output...');
    saveData(transformedData, testOutputPath);
    console.log('');
    
    console.log('✅ Test complete!');
    console.log(`📊 Results saved to: ${testOutputPath}`);
    console.log('\nCompare with existing data to verify transformation.');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run test
if (require.main === module) {
  testTransformation();
}

module.exports = { testTransformation };
