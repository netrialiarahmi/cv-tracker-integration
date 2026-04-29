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
  hasReplacementKeyword,
  hasAdditionalMarker,
} = require('./data-transformer');
const { resolveDivision } = require('./division-lookup');

const DATA_PATH = path.join(__dirname, '..', 'data', 'hiring-data.json');
const BACKUP_PATH = DATA_PATH + '.bak';
const ANOMALY_PATH = path.join(__dirname, '..', 'data', 'replacement_anomalies.json');

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
  let hireTypeReverted = 0;
  let replacementFilled = 0;
  let replacementCleared = 0;
  let divisionCorrected = 0;
  let statusBackfilled = 0;
  const anomalies = [];

  const updated = data.map((entry) => {
    const out = { ...entry };
    const taskName = String(out['Job Position'] || '').trim();
    const originalNotes = out['Notes'] || '';

    // 1) Clean Excel newline artifacts and dedupe notes
    const sanitizedNotes = String(originalNotes)
      .replace(/_x000d_/gi, ' ')
      .replace(/[\r\n]+/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
    const cleanedNotes = dedupeNotes(sanitizedNotes);
    if (cleanedNotes !== originalNotes) {
      out['Notes'] = cleanedNotes;
      notesFixed++;
    }

    // 2) Re-detect Replacement For from cleaned Notes; fall back to the
    //    Job Position itself for tasks named like "Account Executive
    //    Pasangiklan (replace Rio)".
    let detectedName = extractReplacementFor(cleanedNotes);
    let detectedFrom = detectedName ? 'notes' : '';
    if (!detectedName) {
      const fromTitle = extractReplacementFor(taskName);
      if (fromTitle) {
        detectedName = fromTitle;
        detectedFrom = 'title';
      }
    }

    // --- Hire Type precedence (mirrors transformRow) ---
    // Re-derive Hire Type from current signals. Title-Additional override
    // wins over any stray "replace" keyword in the notes.
    const titleAdditional = hasAdditionalMarker(taskName);
    const previousHireType = out['Hire Type'] || '';
    let newHireType;

    if (titleAdditional) {
      newHireType = 'Additional';
    } else if (detectedName) {
      newHireType = 'Replacement';
    } else if (
      hasReplacementKeyword(taskName) || hasReplacementKeyword(cleanedNotes)
    ) {
      newHireType = 'Replacement';
    } else {
      // No signals — keep whatever the Planner labels said previously.
      newHireType = previousHireType || 'Additional';
    }

    // Apply name (only when not overridden to Additional by title)
    if (newHireType === 'Additional' && titleAdditional) {
      // Title-Additional override: clear any speculative replacement-for
      if (out['Replacement For']) {
        console.log(
          `  ⊖ "${taskName}" → cleared Replacement For (title says Additional)`
        );
        out['Replacement For'] = '';
        replacementCleared++;
      }
    } else if (detectedName) {
      if ((out['Replacement For'] || '') !== detectedName) {
        out['Replacement For'] = detectedName;
        replacementFilled++;
      }
    }

    if (newHireType !== previousHireType) {
      if (newHireType === 'Replacement') {
        console.log(
          `  ↻ "${taskName}" → Hire Type=Replacement` +
          (detectedName ? `, For="${detectedName}" (${detectedFrom})` : ' (keyword only)')
        );
        hireTypeFixed++;
      } else {
        console.log(
          `  ↺ "${taskName}" → Hire Type=Additional (was ${previousHireType})`
        );
        hireTypeReverted++;
      }
      out['Hire Type'] = newHireType;
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

    // 6) Anomaly classification (HR review queue)
    const finalHireType = out['Hire Type'] || '';
    const finalRepFor = (out['Replacement For'] || '').trim();
    const notesLower = (cleanedNotes || '').toLowerCase();
    const titleLower = taskName.toLowerCase();

    if (finalHireType === 'Replacement' && !finalRepFor) {
      anomalies.push({
        category: 'missing_name',
        job_position: taskName,
        notes: cleanedNotes.substring(0, 200),
        reason: 'Labelled Replacement but no replaceable name parsed from title or notes',
      });
    } else if (
      finalHireType === 'Replacement' &&
      /\b(atau|or)\b/i.test(notesLower) &&
      hasReplacementKeyword(notesLower)
    ) {
      anomalies.push({
        category: 'ambiguous_multiple',
        job_position: taskName,
        replacement_for: finalRepFor,
        notes: cleanedNotes.substring(0, 200),
        reason: 'Notes mention multiple targets joined by "atau"/"or"; replacement target ambiguous',
      });
    } else if (
      finalHireType === 'Additional' &&
      hasReplacementKeyword(notesLower)
    ) {
      anomalies.push({
        category: 'label_text_conflict',
        job_position: taskName,
        notes: cleanedNotes.substring(0, 200),
        reason: 'Title marked Additional but notes mention "replace" keyword',
      });
    } else if (
      finalRepFor &&
      // Only flag when the EXTRACTED NAME itself looks truncated (ends in
      // "..." or the notes contain a "<keyword> <Capitalised>..." pattern
      // that suggests another replacement was cut mid-name).
      (/\.\.\.$/.test(finalRepFor) ||
        /\b(replace|repl|pengganti|menggantikan)\s+[A-Z][a-z]*\.\.\./i.test(cleanedNotes))
    ) {
      anomalies.push({
        category: 'truncated_notes',
        job_position: taskName,
        replacement_for: finalRepFor,
        notes: cleanedNotes.substring(0, 200),
        reason: 'Notes appear truncated mid-name (further replacement target may be cut off)',
      });
    }

    return out;
  });

  fs.writeFileSync(DATA_PATH, JSON.stringify(updated, null, 4), 'utf-8');
  fs.writeFileSync(ANOMALY_PATH, JSON.stringify(anomalies, null, 2), 'utf-8');

  console.log('');
  console.log('✅ Re-process complete');
  console.log(`   Notes deduped:        ${notesFixed}`);
  console.log(`   Replacement For set:  ${replacementFilled}`);
  console.log(`   Replacement For cleared (Additional override): ${replacementCleared}`);
  console.log(`   Hire Type → Replace:  ${hireTypeFixed}`);
  console.log(`   Hire Type → Additional (reverted): ${hireTypeReverted}`);
  console.log(`   Division corrected:   ${divisionCorrected}`);
  console.log(`   Status backfilled:    ${statusBackfilled}`);
  console.log(`   Total entries:        ${updated.length}`);
  console.log(`   Anomalies for HR review: ${anomalies.length}`);
  console.log(`💾 Saved: ${DATA_PATH}`);
  console.log(`📋 Anomalies: ${ANOMALY_PATH}`);
}

if (require.main === module) {
  main();
}
