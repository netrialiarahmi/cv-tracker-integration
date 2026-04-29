/**
 * Excel Parser - Parses CSV and Excel files exported from Microsoft Planner
 */

const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');
const ExcelJS = require('exceljs');
const config = require('./config');

/**
 * Detect if file is Excel format based on file signature
 * @param {string} filePath - Path to file
 * @returns {boolean} True if file is Excel format
 */
function isExcelFile(filePath) {
  // Read only first 4 bytes for efficiency
  const fd = fs.openSync(filePath, 'r');
  const buffer = Buffer.alloc(4);
  fs.readSync(fd, buffer, 0, 4, 0);
  fs.closeSync(fd);
  
  // Check for ZIP file signature (PK) which indicates xlsx format
  if (buffer.length >= 2 && buffer[0] === 0x50 && buffer[1] === 0x4B) {
    return true;
  }
  // Also check file extension
  const ext = path.extname(filePath).toLowerCase();
  return ext === '.xlsx' || ext === '.xls';
}

/**
 * Parse Excel file (.xlsx) from Planner export
 * @param {string} filePath - Path to Excel file
 * @returns {Promise<Array>} Array of parsed rows
 */
async function parseExcelFile(filePath) {
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);
  
  if (workbook.worksheets.length === 0) {
    throw new Error('No worksheet found in Excel file');
  }

  console.log(`  ℹ Workbook has ${workbook.worksheets.length} worksheet(s): ${workbook.worksheets.map(ws => `"${ws.name}"`).join(', ')}`);
  
  const knownColumns = Object.values(require('./config').columns).map(c => c.toLowerCase().trim());
  // Also include aliases as known column names for sheet/header detection
  const aliases = (require('./config').columnAliases || {});
  const allKnownNames = new Set(knownColumns);
  for (const aliasList of Object.values(aliases)) {
    for (const alias of aliasList) {
      allKnownNames.add(alias.toLowerCase().trim());
    }
  }
  
  // Search all worksheets for the one containing task data
  let bestWorksheet = null;
  let bestSheetMatch = { sheetIndex: 0, rowIndex: 0, matchCount: 0, allRows: [], headers: [] };

  // Helper: scan a worksheet, return best header-row match for it
  const scanWorksheet = (si) => {
    const ws = workbook.worksheets[si];
    const allRows = [];
    ws.eachRow((row, rowNumber) => {
      const values = row.values.slice(1).map(v => v !== null && v !== undefined ? String(v).trim() : '');
      allRows.push({ rowNumber, values });
    });
    let best = { sheetIndex: si, rowIndex: 0, matchCount: 0, allRows, headers: allRows.length > 0 ? allRows[0].values : [] };
    for (let i = 0; i < allRows.length; i++) {
      const matchCount = allRows[i].values.filter(v =>
        allKnownNames.has(v.toLowerCase().trim())
      ).length;
      if (matchCount > best.matchCount) {
        best = { sheetIndex: si, rowIndex: i, matchCount, allRows, headers: allRows[i].values };
      }
    }
    return best;
  };

  // 1) Prefer the configured sheet name (e.g. "Consolidate Data") when present
  const preferredName = (require('./config').preferredSheetName || '').toLowerCase().trim();
  let preferredIndex = -1;
  if (preferredName) {
    preferredIndex = workbook.worksheets.findIndex(ws =>
      String(ws.name || '').toLowerCase().trim() === preferredName
    );
  }
  if (preferredIndex >= 0) {
    const preferredMatch = scanWorksheet(preferredIndex);
    if (preferredMatch.matchCount >= 2) {
      console.log(`  ℹ Using preferred worksheet "${workbook.worksheets[preferredIndex].name}" (matched ${preferredMatch.matchCount} known columns)`);
      bestSheetMatch = preferredMatch;
    } else {
      console.log(`  ⚠️  Preferred worksheet "${workbook.worksheets[preferredIndex].name}" found but has too few known columns (${preferredMatch.matchCount}); falling back to auto-detect`);
    }
  } else if (preferredName) {
    console.log(`  ⚠️  Preferred worksheet "${preferredName}" not found in workbook; falling back to auto-detect`);
  }

  // 2) Otherwise, auto-detect across all worksheets
  if (bestSheetMatch.matchCount < 2) {
    for (let si = 0; si < workbook.worksheets.length; si++) {
      const cand = scanWorksheet(si);
      if (cand.matchCount > bestSheetMatch.matchCount) {
        bestSheetMatch = cand;
      }
    }
  }
  
  if (bestSheetMatch.matchCount >= 2) {
    console.log(`  ℹ Using worksheet "${workbook.worksheets[bestSheetMatch.sheetIndex].name}" (matched ${bestSheetMatch.matchCount} known columns)`);
  } else {
    // Fallback: use the worksheet with the most rows (skip metadata sheets)
    let maxRows = 0;
    let fallbackIndex = 0;
    for (let si = 0; si < workbook.worksheets.length; si++) {
      const rowCount = workbook.worksheets[si].rowCount;
      if (rowCount > maxRows) {
        maxRows = rowCount;
        fallbackIndex = si;
      }
    }
    console.log(`  ⚠️  No worksheet matched known columns. Falling back to worksheet "${workbook.worksheets[fallbackIndex].name}" (most rows: ${maxRows})`);
    const ws = workbook.worksheets[fallbackIndex];
    const allRows = [];
    ws.eachRow((row, rowNumber) => {
      const values = row.values.slice(1).map(v => v !== null && v !== undefined ? String(v).trim() : '');
      allRows.push({ rowNumber, values });
    });
    bestSheetMatch = { sheetIndex: fallbackIndex, rowIndex: 0, matchCount: 0, allRows, headers: allRows.length > 0 ? allRows[0].values : [] };
  }
  
  const { allRows, rowIndex: headerIndex, headers } = bestSheetMatch;
  const headerRowNumber = allRows[headerIndex] ? allRows[headerIndex].rowNumber : 1;
  console.log(`  ℹ Using row ${headerRowNumber} as header row`);
  console.log(`  ℹ Found ${headers.length} columns: ${JSON.stringify(headers)}`);
  
  // Collect data rows (everything after the header row)
  const records = [];
  for (let i = headerIndex + 1; i < allRows.length; i++) {
    const record = {};
    allRows[i].values.forEach((value, index) => {
      if (headers[index]) {
        record[headers[index]] = value;
      }
    });
    const hasNonEmptyValue = Object.values(record).some(val => val !== '');
    if (hasNonEmptyValue) {
      records.push(record);
    }
  }
  
  return records;
}

/**
 * Parse CSV file from Planner export
 * @param {string} filePath - Path to CSV file
 * @returns {Array} Array of parsed rows
 */
function parseCSVFile(filePath) {
  // Read file content
  const fileContent = fs.readFileSync(filePath, 'utf-8');
  
  // Parse CSV with semicolon delimiter
  const records = parse(fileContent, {
    columns: true,
    skip_empty_lines: true,
    delimiter: config.csvDelimiter,
    relax_column_count: true,
    trim: true,
    bom: true // Handle BOM if present
  });
  
  return records;
}

/**
 * Parse CSV or Excel file from Planner export
 * @param {string} filePath - Path to CSV or Excel file
 * @returns {Promise<Array>} Array of parsed rows
 */
async function parseExcelCSV(filePath) {
  try {
    console.log(`📄 Reading file: ${filePath}`);
    
    let records;
    
    if (isExcelFile(filePath)) {
      console.log('  ℹ Detected Excel format (.xlsx)');
      records = await parseExcelFile(filePath);
    } else {
      console.log('  ℹ Detected CSV format');
      records = parseCSVFile(filePath);
    }
    
    console.log(`✅ Parsed ${records.length} records from file`);
    return records;
    
  } catch (error) {
    console.error('❌ Error parsing file:', error.message);
    throw error;
  }
}

/**
 * Validate required columns exist in parsed data
 * @param {Array} records - Parsed CSV records
 * @returns {boolean} True if valid
 */
function validateColumns(records) {
  if (!records || records.length === 0) {
    console.warn('⚠️  No records found in CSV');
    return false;
  }
  
  const requiredColumns = [
    config.columns.taskName,
    config.columns.bucketName
  ];
  
  const firstRecord = records[0];
  const actualColumns = Object.keys(firstRecord);
  console.log(`  ℹ Columns in data: ${JSON.stringify(actualColumns)}`);
  
  // Try exact match first
  let missingColumns = requiredColumns.filter(col => !(col in firstRecord));
  
  // If exact match fails, try case-insensitive matching and remap
  if (missingColumns.length > 0) {
    console.log('  ℹ Exact column match failed, trying case-insensitive match...');
    const columnMap = buildColumnMap(actualColumns, requiredColumns);
    
    if (columnMap) {
      // Remap all records to use expected column names
      for (let i = 0; i < records.length; i++) {
        for (const [expected, actual] of Object.entries(columnMap)) {
          if (actual !== expected && actual in records[i]) {
            records[i][expected] = records[i][actual];
          }
        }
      }
      // Also remap all config columns
      for (const [key, expected] of Object.entries(config.columns)) {
        const match = actualColumns.find(col => col.toLowerCase().trim() === expected.toLowerCase().trim());
        if (match && match !== expected) {
          for (let i = 0; i < records.length; i++) {
            if (match in records[i] && !(expected in records[i])) {
              records[i][expected] = records[i][match];
            }
          }
        }
      }
      missingColumns = requiredColumns.filter(col => !(col in records[0]));
    }
  }
  
  if (missingColumns.length > 0) {
    console.error('❌ Missing required columns:', missingColumns);
    return false;
  }
  
  console.log('✅ All required columns present');
  return true;
}

/**
 * Build a mapping from expected column names to actual column names
 * Uses case-insensitive matching first, then alias matching
 * @param {string[]} actualColumns - Column names found in the data
 * @param {string[]} requiredColumns - Expected column names
 * @returns {Object|null} Mapping of expected -> actual, or null if not all found
 */
function buildColumnMap(actualColumns, requiredColumns) {
  const aliases = config.columnAliases || {};
  const map = {};
  for (const expected of requiredColumns) {
    // 1. Try case-insensitive exact match
    let match = actualColumns.find(col => col.toLowerCase().trim() === expected.toLowerCase().trim());
    
    // 2. Try alias matching
    if (!match && aliases[expected]) {
      for (const alias of aliases[expected]) {
        match = actualColumns.find(col => col.toLowerCase().trim() === alias.toLowerCase().trim());
        if (match) break;
      }
    }
    
    // 3. Try partial/contains match as last resort
    if (!match) {
      const expectedWords = expected.toLowerCase().split(/\s+/);
      match = actualColumns.find(col => {
        const colLower = col.toLowerCase().trim();
        return expectedWords.every(w => colLower.includes(w));
      });
    }
    
    if (match) {
      map[expected] = match;
      console.log(`  ✓ Mapped "${match}" -> "${expected}"`);
    } else {
      console.warn(`  ⚠️  No match found for required column "${expected}"`);
    }
  }
  return Object.keys(map).length > 0 ? map : null;
}

/**
 * Get column value safely
 * @param {Object} row - CSV row
 * @param {string} columnName - Column name
 * @returns {string} Column value or empty string
 */
function getColumnValue(row, columnName) {
  return row[columnName] || '';
}

module.exports = {
  parseExcelCSV,
  validateColumns,
  getColumnValue
};
