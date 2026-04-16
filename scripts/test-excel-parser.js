/**
 * Test script for Excel parser
 * Creates a sample Excel file and tests parsing
 */

const fs = require('fs');
const path = require('path');
const ExcelJS = require('exceljs');
const { parseExcelCSV, validateColumns } = require('./excel-parser');

async function createTestExcelFile() {
  const workbook = new ExcelJS.Workbook();
  
  // Sheet 1: Metadata (like actual Planner export)
  const metaSheet = workbook.addWorksheet('Info');
  metaSheet.columns = [
    { header: 'Plan ID', key: 'planId', width: 30 },
    { header: 'Plan name', key: 'planName', width: 30 },
    { header: 'Date of export', key: 'dateExport', width: 20 }
  ];
  metaSheet.addRow({
    planId: 'abc123',
    planName: 'Hiring Tracker',
    dateExport: '2026-04-15'
  });
  
  // Sheet 2: Actual task data
  const worksheet = workbook.addWorksheet('Tasks');
  
  // Add headers
  worksheet.columns = [
    { header: 'Task ID', key: 'taskId', width: 15 },
    { header: 'Task Name', key: 'taskName', width: 30 },
    { header: 'Bucket Name', key: 'bucketName', width: 30 },
    { header: 'Progress', key: 'progress', width: 15 },
    { header: 'Priority', key: 'priority', width: 15 },
    { header: 'Assigned To', key: 'assignedTo', width: 20 },
    { header: 'Created By', key: 'createdBy', width: 20 },
    { header: 'Created Date', key: 'createdDate', width: 20 },
    { header: 'Start date', key: 'startDate', width: 20 },
    { header: 'Due date', key: 'dueDate', width: 20 },
    { header: 'Labels', key: 'labels', width: 20 },
    { header: 'Description', key: 'description', width: 40 },
    { header: 'Completed Date', key: 'completedDate', width: 20 }
  ];
  
  // Add sample data
  worksheet.addRow({
    taskId: 'TASK-001',
    taskName: 'Frontend Developer',
    bucketName: 'Backlog (Employee Req Form)',
    progress: 'Not started',
    priority: 'Medium',
    assignedTo: 'Adelia Galuh H',
    createdBy: 'Adelia Galuh H',
    createdDate: '2024-01-15',
    startDate: '2024-01-15',
    dueDate: '2024-02-15',
    labels: 'Technology;Additional',
    description: 'Looking for a frontend developer with React experience',
    completedDate: ''
  });
  
  worksheet.addRow({
    taskId: 'TASK-002',
    taskName: 'Backend Developer',
    bucketName: 'HR & User Interview + Skill Test',
    progress: 'In progress',
    priority: 'High',
    assignedTo: 'Rizky Pangestu',
    createdBy: 'Adelia Galuh H',
    createdDate: '2024-01-10',
    startDate: '2024-01-10',
    dueDate: '2024-02-10',
    labels: 'Technology;Replacement',
    description: 'Backend developer to replace John Doe',
    completedDate: ''
  });
  
  // Save the file
  const filePath = path.join(__dirname, '..', 'downloads', 'test-export.xlsx');
  await workbook.xlsx.writeFile(filePath);
  console.log(`✅ Created test Excel file: ${filePath}`);
  return filePath;
}

async function testExcelParser() {
  console.log('🧪 Testing Excel Parser...\n');
  
  try {
    // Create test file
    const testFilePath = await createTestExcelFile();
    console.log('');
    
    // Parse the file
    console.log('📄 Parsing Excel file...');
    const records = await parseExcelCSV(testFilePath);
    console.log('');
    
    // Validate columns
    console.log('✅ Validating columns...');
    if (!validateColumns(records)) {
      throw new Error('Column validation failed');
    }
    console.log('');
    
    // Display parsed data
    console.log('📊 Parsed records:');
    records.forEach((record, index) => {
      console.log(`\nRecord ${index + 1}:`);
      console.log(`  Task Name: ${record['Task Name']}`);
      console.log(`  Bucket Name: ${record['Bucket Name']}`);
      console.log(`  Progress: ${record['Progress']}`);
      console.log(`  Assigned To: ${record['Assigned To']}`);
    });
    console.log('');
    
    // Test CSV parsing as well
    console.log('📄 Testing CSV parsing...');
    const csvFilePath = path.join(__dirname, '..', 'downloads', 'test-export.csv');
    const csvContent = 'Task ID;Task Name;Bucket Name;Progress\nTASK-003;DevOps Engineer;Offering;In progress';
    fs.writeFileSync(csvFilePath, csvContent);
    console.log(`  Created test CSV: ${csvFilePath}`);
    
    const csvRecords = await parseExcelCSV(csvFilePath);
    console.log(`  Parsed ${csvRecords.length} CSV records`);
    console.log('');
    
    console.log('✅ All tests passed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run test
if (require.main === module) {
  testExcelParser();
}

module.exports = { testExcelParser, createTestExcelFile };
