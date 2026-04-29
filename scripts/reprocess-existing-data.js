/**
 * Re-process existing data/hiring-data.json IN PLACE:
 *  - Deduplicate Notes (collapse repeated "Replace X | Replace X | …" entries)
 *  - Re-detect Replacement For from Notes (handles | and ; separators)
 *  - Auto-set Hire Type = Replacement when a name is extracted from Notes
 *  - Auto-correct Division using data/division_lookup.json (Employee Report)
 *  - Backfill Status = "Contract" when missing
 *
 * Use this when you've changed transformer rules but cannot run the full
 * Planner sync (which requires Microsoft login). Safe to run repeatedly.
 *
 * Usage:
 *   node scripts/reprocess-existing-data.js
 */

const fs = require('fs');
const path = require('path');
const {
  extractReplacementFor,
  dedupeNotes,
} = require('./data-transformer');
const { resolveDivision } = require('./division-lookup');

const DATA_PATH = path.join(__dirname, '..', 'data', 'hiring-data.json');
const BACKUP_PATH = DATA_PATH + '.bak';

function readJsonAllowingNaN(filePath) {
  // Python pandas writes NaN tokens which JSON.parse rejects.
  // Coerce NaN/Infinity tokens to null before parsing.
  const raw = fs.readFileSync(filePath, 'utf-8');
  const sanitized = raw
    .replace(/\bNaN\b/g, 'null')
    .replace(/\bInfinity\b/g, 'null')
    .replace(/\b-Infinity\b/g, 'null');
  return JSON.parse(sanitized);
}

function main() {
  if (!fs.existsSync(DATA_PATH)) {
    console.error(`❌ Not found: ${DATA_PATH}`);
    process.exit(1);
  }

  const data = readJsonAllowingNaN(DATA_PATH);
  if (!Array.isArray(data)) {
    console.error('❌ hiring-data.json is not an array');
    process.exit(1);
  }

  // Backup
  fs.copyFileSync(DATA_PATH, BACKUP_PATH);
  console.log(`📦 Backup written: ${BACKUP_PATH}`);

  let notesFixed = 0;
  let hireTypeFixed = 0;
  let replacementFilled = 0;
  let divisionCorrected = 0;
  let statusBackfilled = 0;

  const updated = data.map((entry) => {
    const out = { ...entry };
    const taskName = String(out['Job Position'] || '').trim();
    const originalNotes = out['Notes'] || '';

    // 1) Dedupe notes
    const cleanedNotes = dedupeNotes(originalNotes);
    if (cleanedNotes !== originalNotes) {
      out['Notes'] = cleanedNotes;
      notesFixed++;
    }

    // 2) Re-detect Replacement For from cleaned Notes
    const detectedName = extractReplacementFor(cleanedNotes);
    if (detectedName) {
      if ((out['Replacement For'] || '') !== detectedName) {
        out['Replacement For'] = detectedName;
        replacementFilled++;
      }
      // 3) Force Hire Type = Replacement when a name was found
      if (out['Hire Type'] !== 'Replacement') {
        out['Hire Type'] = 'Replacement';
        hireTypeFixed++;
      }
    }

    // 4) Division auto-correction
    if (taskName) {
      const currentDivision = String(out['Division'] || '').trim();
      const resolved = resolveDivision(taskName, currentDivision);
      if (
        resolved.source !== 'planner' &&
        resolved.division &&
        resolved.division.trim().toLowerCase() !==
          currentDivision.toLowerCase()
      ) {
        console.log(
          `  ⇄ "${taskName}": "${currentDivision}" → "${resolved.division}" (${resolved.source})`
        );
        out['Planner Division'] = out['Planner Division'] || currentDivision;
        out['Division'] = resolved.division;
        out['Directorate'] = resolved.directorate || out['Directorate'] || '';
        out['Department'] = resolved.department || out['Department'] || '';
        out['Section'] = resolved.section || out['Section'] || '';
        divisionCorrected++;
      } else if (resolved.source !== 'planner') {
        // Same division but fill in missing hierarchy fields
        if (!out['Directorate'] && resolved.directorate) {
          out['Directorate'] = resolved.directorate;
        }
        if (!out['Department'] && resolved.department) {
          out['Department'] = resolved.department;
        }
        if (!out['Section'] && resolved.section) {
          out['Section'] = resolved.section;
        }
      }
    }

    // 5) Status backfill
    const status = (out['Status'] || '').trim();
    if (!status) {
      out['Status'] = 'Contract';
      statusBackfilled++;
    }

    return out;
  });

  fs.writeFileSync(DATA_PATH, JSON.stringify(updated, null, 4), 'utf-8');

  console.log('');
  console.log('✅ Re-process complete');
  console.log(`   Notes deduped:        ${notesFixed}`);
  console.log(`   Replacement For set:  ${replacementFilled}`);
  console.log(`   Hire Type → Replace:  ${hireTypeFixed}`);
  console.log(`   Division corrected:   ${divisionCorrected}`);
  console.log(`   Status backfilled:    ${statusBackfilled}`);
  console.log(`   Total entries:        ${updated.length}`);
  console.log(`💾 Saved: ${DATA_PATH}`);
}

if (require.main === module) {
  main();
}
