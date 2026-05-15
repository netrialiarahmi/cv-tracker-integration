/**
 * Data Transformer - Transforms Planner CSV data to Hiring Tracker JSON format
 */

const fs = require('fs');
const config = require('./config');
const { getColumnValue } = require('./excel-parser');
const { resolveDivision } = require('./division-lookup');

/**
 * Get current date/time in Jakarta timezone
 * @returns {string} Formatted datetime string
 */
function getCurrentDateTime() {
  const now = new Date();
  
  // Convert to Jakarta timezone (UTC+7)
  const jakartaTime = new Date(now.toLocaleString('en-US', { timeZone: config.timezone }));
  
  const year = jakartaTime.getFullYear();
  const month = String(jakartaTime.getMonth() + 1).padStart(2, '0');
  const day = String(jakartaTime.getDate()).padStart(2, '0');
  const hours = String(jakartaTime.getHours()).padStart(2, '0');
  const minutes = String(jakartaTime.getMinutes()).padStart(2, '0');
  const seconds = String(jakartaTime.getSeconds()).padStart(2, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

/**
 * Map bucket name and progress to stage checkboxes
 * @param {string} bucketName - Bucket name from Planner
 * @param {string} progress - Progress status
 * @param {Object} existingStages - Existing stages for HOLD/CANCELED preservation
 * @returns {Object} Stage checkboxes object
 */
function mapBucketToStages(bucketName, progress, existingStages = null) {
  // If completed, all stages are true
  if (progress === config.completedStatus) {
    return {
      initialScreening: true,
      interview: true,
      skillTest: true,
      finalInterview: true,
      offering: true,
      contractSign: true,
      onBoarding: true
    };
  }
  
  // For HOLD, CANCELED, or In Progress - preserve existing stages
  if (existingStages && (
    bucketName.includes(config.specialBuckets.hold) ||
    bucketName.includes(config.specialBuckets.canceled) ||
    bucketName === config.specialBuckets.inProgress
  )) {
    return existingStages;
  }
  
  // Map bucket to stages
  const stages = config.bucketStages[bucketName];
  if (stages) {
    return { ...stages };
  }

  // Try alias / partial matching for short bucket labels (e.g., "Initial",
  // "Final Interview", "Onboarding") used in the Consolidate Data tab.
  const aliasMatch = resolveBucketAlias(bucketName);
  if (aliasMatch && config.bucketStages[aliasMatch]) {
    return { ...config.bucketStages[aliasMatch] };
  }

  // Default to initial screening false if bucket not recognized
  console.warn(`⚠️  Unknown bucket name: "${bucketName}", using default stages`);
  return {
    initialScreening: false,
    interview: false,
    skillTest: false,
    finalInterview: false,
    offering: false,
    contractSign: false,
    onBoarding: false
  };
}

/**
 * Resolve a short / alternative bucket label to a canonical bucket key.
 * Tries exact alias match first, then substring match against known bucket names.
 * @param {string} bucketName
 * @returns {string|null} Canonical bucket key or null
 */
function resolveBucketAlias(bucketName) {
  if (!bucketName) return null;
  const key = bucketName.toLowerCase().trim();
  const aliases = config.bucketAliases || {};
  if (aliases[key]) return aliases[key];

  // Substring match against alias keys (e.g. "Initial Screening - HR" → "initial screening")
  for (const aliasKey of Object.keys(aliases)) {
    if (key.includes(aliasKey)) return aliases[aliasKey];
  }

  // Substring match against canonical bucket names
  for (const canonical of Object.keys(config.bucketStages)) {
    if (canonical.toLowerCase().includes(key) || key.includes(canonical.toLowerCase())) {
      return canonical;
    }
  }
  return null;
}

/**
 * Detect employment status from labels + task name.
 * @param {string} labelsStr - Semicolon-separated labels
 * @param {string} taskName - Task name (job title)
 * @returns {string} Status (Intern / Freelance / Contract)
 */
function extractStatus(labelsStr, taskName) {
  const haystack = `${labelsStr || ''} ${taskName || ''}`.toLowerCase();
  for (const { keyword, value } of (config.statusKeywords || [])) {
    if (haystack.includes(keyword.toLowerCase())) {
      return value;
    }
  }
  return config.defaultStatus || config.defaults.status || 'Contract';
}

/**
 * Extract division from labels
 * @param {string} labelsStr - Semicolon-separated labels
 * @param {Object} existing - Existing data entry
 * @returns {string} Division name
 */
function extractDivision(labelsStr, existing = null) {
  if (!labelsStr) {
    return existing?.Division || config.defaults.division;
  }
  
  const labels = labelsStr.split(';').map(l => l.trim()).filter(l => l);
  
  // Check each label against division mapping
  for (const label of labels) {
    // Skip ignore labels
    if (config.ignoreLabels.includes(label)) {
      continue;
    }
    
    // Check exact match
    if (config.divisionMapping[label]) {
      return config.divisionMapping[label];
    }
    
    // Check partial match
    for (const [key, value] of Object.entries(config.divisionMapping)) {
      if (label.includes(key) || key.includes(label)) {
        return value;
      }
    }
  }
  
  // Return existing division if available
  return existing?.Division || config.defaults.division;
}

/**
 * Extract PIC from Assigned To field
 * @param {string} assignedTo - Assigned To value
 * @returns {string} PIC name (lowercase first name)
 */
function extractPIC(assignedTo) {
  if (!assignedTo) {
    return config.defaults.pic;
  }
  
  // Handle multiple assignees (semicolon separated) - take first
  const assignees = assignedTo.split(';').map(a => a.trim()).filter(a => a);
  const firstAssignee = assignees[0] || '';
  
  // Check mapping
  if (config.picMapping[firstAssignee]) {
    return config.picMapping[firstAssignee];
  }
  
  // Check partial match
  for (const [key, value] of Object.entries(config.picMapping)) {
    if (firstAssignee.includes(key) || key.includes(firstAssignee)) {
      return value;
    }
  }
  
  // Default
  return config.picMapping.default;
}

/**
 * Extract hire type from labels
 * @param {string} labelsStr - Semicolon-separated labels
 * @returns {string} Hire type
 */
function extractHireType(labelsStr) {
  if (!labelsStr) {
    return config.defaults.hireType;
  }
  
  const labels = labelsStr.split(';').map(l => l.trim()).filter(l => l);
  
  if (labels.includes(config.hireTypeLabels.replacement)) {
    return 'Replacement';
  }
  
  if (labels.includes(config.hireTypeLabels.additional)) {
    return 'Additional';
  }
  
  return config.defaults.hireType;
}

/**
 * Sanitize a captured candidate name:
 *  - trim whitespace and trailing punctuation
 *  - truncate at the first junk-suffix token (e.g. "Idris yg di rolling" → "Idris")
 *  - reject single stop-words ("slot", "yg", etc.)
 *  - reject results shorter than 2 chars
 * @returns {string} cleaned name or '' when invalid
 */
function sanitizeReplacementName(raw) {
  if (!raw) return '';
  let s = String(raw).trim();
  // Strip trailing punctuation and bracket residues
  s = s.replace(/[\s,.;:|/\\)(\-]+$/g, '').trim();
  if (!s) return '';

  // Truncate at first junk-suffix token (word-boundary)
  const junk = config.replacementJunkSuffixes || [];
  if (junk.length) {
    const escaped = junk.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
    const re = new RegExp(`\\s+(?:${escaped})\\b.*$`, 'i');
    s = s.replace(re, '').trim();
    s = s.replace(/[\s,.;:|/\\)(\-]+$/g, '').trim();
  }

  if (s.length < 2) return '';

  // Reject if the entire result is a stop-word
  const stop = (config.replacementStopWords || []).map((w) => w.toLowerCase());
  if (stop.includes(s.toLowerCase())) return '';

  return s;
}

/**
 * Try to extract a replacement name (or multiple, joined with " & ") from a
 * single text segment. Returns '' when nothing meaningful is found.
 *
 * Strategy:
 *  1. Locate first replacement keyword (word-boundary, longest first).
 *  2. Look at the text immediately after the keyword (up to ~80 chars).
 *  3. Capture name(s) made of capitalised words / lowercase first-words,
 *     allowing "&", "and", "dan" or comma separators for multi-name.
 *  4. Stop on punctuation/parenthesis/pipe/semicolon or junk-suffix tokens.
 */
function extractReplacementFromSegment(segment) {
  if (!segment) return '';

  const keywords = [...(config.replacementKeywords || [])].sort(
    (a, b) => b.length - a.length
  );

  for (const keyword of keywords) {
    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // Allow optional trailing "." (e.g. "Repl.") and optional ":" after.
    const re = new RegExp(`\\b${escaped}\\b\\.?\\s*:?`, 'i');
    const m = re.exec(segment);
    if (!m) continue;

    let after = segment.substring(m.index + m[0].length).trim();
    if (!after) continue;

    // Drop a leading "slot " / "ex " / "posisi " filler word that comes
    // between the keyword and the actual name. Examples:
    //   "Replace slot Oik" → "Oik"
    //   "Repl ex RubyH"   → "RubyH"
    //   "menggantikan posisi Yuna. Yuna ..." → "Yuna. Yuna ..."
    after = after.replace(/^(slot|ex|posisi)\s+/i, '');

    // Special case: numbered list "1. NameA ... 2. NameB ..." (used in
    // "Replacement: 1. Kiki yang pindah ... 2. Haryanti yang promosi ...").
    // Capture each numbered item, sanitize, join with " & ".
    if (/^\d+\.\s/.test(after)) {
      const items = after
        .split(/\s*\d+\.\s+/)
        .map((p) => p.trim())
        .filter(Boolean);
      const names = [];
      const seen = new Set();
      for (const item of items) {
        // Take just the leading word-run before any non-name char
        const head = item.match(/^([A-Za-z][A-Za-z\s.'\-]{0,80})/);
        if (!head) continue;
        const cleaned = sanitizeReplacementName(head[1]);
        if (!cleaned) continue;
        const k = cleaned.toLowerCase();
        if (seen.has(k)) continue;
        seen.add(k);
        names.push(cleaned);
      }
      if (names.length) return names.join(' & ');
      // fall through to generic logic if numbered parse failed
    }

    // Greedy capture of the leading name-run. Allowed chars: letters,
    // spaces, ' & - (NOT comma, NOT period — period spills past sentence
    // boundaries, comma usually starts a descriptive clause). Trailing
    // period on the captured name (e.g. "Sr.") is preserved by allowing
    // it as a final char only.
    const window = after.substring(0, 80);
    const nameMatch = window.match(/^[:\s]*([A-Za-z][A-Za-z\s'&\-]{0,80}\.?)/);
    if (!nameMatch || !nameMatch[1]) continue;

    // Split into individual names (handle "A & B", "A and B", "A dan B").
    const rawParts = nameMatch[1]
      .split(/\s*(?:&|\band\b|\bdan\b)\s*/i)
      .map((p) => sanitizeReplacementName(p))
      .filter(Boolean);

    if (rawParts.length === 0) continue;

    // De-duplicate while preserving order
    const seen = new Set();
    const uniq = [];
    for (const p of rawParts) {
      const k = p.toLowerCase();
      if (seen.has(k)) continue;
      seen.add(k);
      uniq.push(p);
    }

    return uniq.join(' & ');
  }

  return '';
}

/**
 * Extract replacement-name(s) from any free text (Description / Task Name).
 * Scans segments separated by " | " in order; first non-empty match wins.
 * Returns string (possibly multi-name "A & B") or config default.
 *
 * @param {string} description - source text
 * @returns {string} replacement name(s) or default
 */
function extractReplacementFor(description) {
  if (!description) {
    return config.defaults.replacementFor;
  }

  // Scan segments first (Notes are usually pipe-joined update history).
  // Each segment is independently checked; first one with a hit wins so
  // dated update logs further right don't poison the result.
  const segments = String(description).split('|').map((s) => s.trim()).filter(Boolean);
  if (segments.length === 0) segments.push(String(description));

  for (const seg of segments) {
    // Inside one segment, also drop everything from " Update" or a date
    // prefix onward — these are timeline entries that often contain
    // candidate names that are NOT replacement targets.
    const trimmedSeg = seg.replace(
      /\s+(?:update\s*\d*\s*[:/]|update\b|\d{1,2}[\/-]\d{1,2}[\/-]?\d{0,4}\s*:).*$/i,
      ''
    );
    const found = extractReplacementFromSegment(trimmedSeg || seg);
    if (found) return found;
  }

  return config.defaults.replacementFor;
}

/**
 * Check whether text contains a replacement keyword (word-boundary match).
 * Useful when the position is clearly a replacement but no specific name
 * is mentioned (e.g. "Reporter Tren | Replacement").
 */
function hasReplacementKeyword(text) {
  if (!text) return false;
  const keywords = [...config.replacementKeywords].sort((a, b) => b.length - a.length);
  for (const keyword of keywords) {
    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re = new RegExp(`\\b${escaped}\\b\\.?`, 'i');
    if (re.test(text)) return true;
  }
  return false;
}

/**
 * Detect when the Job Position title explicitly marks itself as Additional,
 * e.g. "6. Content Writer Regional (Additional Provinsi)". Such positions
 * are headcount expansions and must NOT be promoted to Replacement even if
 * the Notes happen to contain a stray "replace" keyword.
 */
function hasAdditionalMarker(taskName) {
  if (!taskName) return false;
  return /\(\s*additional\b[^)]*\)/i.test(taskName);
}

/**
 * Merge notes from existing and new description
 * @param {string} existingNotes - Existing notes
 * @param {string} newDescription - New description from Planner
 * @returns {string} Merged notes
 */
function mergeNotes(existingNotes, newDescription) {
  // Clean up description: strip CR/LF and Excel's literal "_x000d_"
  // newline-escape (which appears verbatim in some xlsx exports).
  const cleanDesc = newDescription
    ? newDescription.replace(/_x000d_/gi, ' ').replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim()
    : '';

  // If no new description, keep existing (deduplicated)
  if (!cleanDesc) {
    return dedupeNotes(existingNotes || config.defaults.notes);
  }

  // If no existing notes, use new description
  if (!existingNotes) {
    return cleanDesc;
  }

  // If they're the same, just return one
  if (existingNotes === cleanDesc) {
    return existingNotes;
  }

  // Append, deduplicate segments split by ' | ', then cap length
  const combined = dedupeNotes(`${existingNotes} | ${cleanDesc}`);
  const cap = config.notesMaxLength || 1000;
  return combined.length > cap ? combined.substring(0, cap - 3) + '...' : combined;
}

/**
 * Deduplicate ' | '-separated note segments while preserving order.
 */
function dedupeNotes(notes) {
  if (!notes) return '';
  const seen = new Set();
  const out = [];
  for (const seg of String(notes).split('|')) {
    const s = seg.trim();
    if (!s) continue;
    const key = s.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(s);
  }
  return out.join(' | ');
}

/**
 * Check if position should be frozen
 * @param {string} bucketName - Bucket name
 * @returns {boolean} True if frozen
 */
function isFrozen(bucketName) {
  return bucketName.includes(config.specialBuckets.hold) ||
         bucketName.includes(config.specialBuckets.canceled);
}

/**
 * Find existing entry by job position
 * @param {Array} existingData - Existing hiring data
 * @param {string} jobPosition - Job position to find
 * @returns {Object|null} Existing entry or null
 */
function findExisting(existingData, jobPosition) {
  if (!existingData || !Array.isArray(existingData)) {
    return null;
  }
  
  return existingData.find(item => 
    item['Job Position'] && 
    item['Job Position'].trim() === jobPosition.trim()
  ) || null;
}

/**
 * Transform single CSV row to hiring tracker format
 * @param {Object} row - CSV row
 * @param {Object} existing - Existing data entry
 * @returns {Object} Transformed entry
 */
function transformRow(row, existing = null) {
  const taskName = getColumnValue(row, config.columns.taskName);
  const bucketName = getColumnValue(row, config.columns.bucketName);
  const progress = getColumnValue(row, config.columns.progress);
  const assignedTo = getColumnValue(row, config.columns.assignedTo);
  const labels = getColumnValue(row, config.columns.labels);
  const description = getColumnValue(row, config.columns.description);
  const createdDate = getColumnValue(row, config.columns.createdDate);
  
  // Get existing stages for preservation
  const existingStages = existing ? {
    initialScreening: existing['Initial screening'],
    interview: existing['HR & User Interview (Stage 1)'],
    skillTest: existing['Skill Test'],
    finalInterview: existing['Final Interview'],
    offering: existing['Offering'],
    contractSign: existing['Contract Sign'],
    onBoarding: existing['On Boarding']
  } : null;
  
  // Map stages
  const stages = mapBucketToStages(bucketName, progress, existingStages);
  
  // Extract metadata
  const division = extractDivision(labels, existing);
  const pic = extractPIC(assignedTo);

  // --- Hire Type precedence (highest priority first) ---
  // 1. Planner label "Replacement" → lock as Replacement (authoritative)
  // 2. Title says "(Additional ...)" → lock as Additional (explicit headcount
  //    expansion; overrides any stray "replace" keyword in notes)
  // 3. Planner label "Additional" → Additional
  // 4. Replacement name found in Notes/Title → Replacement
  // 5. Replacement keyword anywhere → Replacement (no name)
  // 6. Default → Additional
  const labelHireType = extractHireType(labels);
  const titleAdditional = hasAdditionalMarker(taskName);
  let replacementFor = extractReplacementFor(description);
  if (!replacementFor) {
    replacementFor = extractReplacementFor(taskName);
  }

  let hireType;
  if (labelHireType === 'Replacement') {
    hireType = 'Replacement';
  } else if (titleAdditional) {
    hireType = 'Additional';
    // Drop any speculative replacement-for; this is an Additional slot.
    replacementFor = '';
  } else if (labelHireType === 'Additional') {
    hireType = 'Additional';
  } else if (replacementFor) {
    hireType = 'Replacement';
  } else if (hasReplacementKeyword(taskName) || hasReplacementKeyword(description)) {
    hireType = 'Replacement';
  } else {
    hireType = config.defaults.hireType;
  }

  const freeze = isFrozen(bucketName);
  const notes = mergeNotes(existing?.Notes, description);
  const status = extractStatus(labels, taskName);
  const completedDate = getColumnValue(row, config.columns.completedDate);

  // Auto-correct Division using the Employee-Report-derived lookup.
  // Falls back to the Planner-derived division when the lookup has no entry.
  const resolved = resolveDivision(taskName, division);
  const finalDivision = resolved.division || division;
  if (
    resolved.source !== 'planner' &&
    resolved.division &&
    division &&
    resolved.division.trim().toLowerCase() !== division.trim().toLowerCase()
  ) {
    console.log(`  ⇄ Division corrected for "${taskName}": "${division}" → "${resolved.division}" (${resolved.source})`);
  }
  
  // Build transformed entry
  return {
    Division: finalDivision,
    Directorate: resolved.directorate || existing?.Directorate || '',
    Department: resolved.department || existing?.Department || '',
    Section: resolved.section || existing?.Section || '',
    'Job Position': taskName,
    'Initial screening': stages.initialScreening,
    'HR & User Interview (Stage 1)': stages.interview,
    'Skill Test': stages.skillTest,
    'Final Interview': stages.finalInterview,
    'Offering': stages.offering,
    'Contract Sign': stages.contractSign,
    'On Boarding': stages.onBoarding,
    PIC: pic,
    Notes: notes,
    'Last Updated': getCurrentDateTime(),
    'Has Skill Test': stages.skillTest,
    'Hire Type': hireType,
    'Replacement For': replacementFor,
    'Job Description': existing?.['Job Description'] || config.defaults.jobDescription,
    Attachments: Array.isArray(existing?.Attachments) ? existing.Attachments : config.defaults.attachments,
    Freeze: freeze,
    'Created Date': createdDate || existing?.['Created Date'] || config.defaults.createdDate,
    'Completed Date': completedDate || existing?.['Completed Date'] || '',
    Status: status || existing?.Status || config.defaults.status
  };
}

/**
 * Transform entire CSV data to hiring tracker format
 * @param {Array} csvData - Parsed CSV data
 * @param {Array} existingData - Existing hiring data
 * @returns {Array} Transformed data
 */
function transformData(csvData, existingData = []) {
  console.log(`🔄 Transforming ${csvData.length} records...`);
  
  const transformed = [];
  const updatedPositions = new Set();
  
  // Transform each CSV row
  for (const row of csvData) {
    const taskName = getColumnValue(row, config.columns.taskName);
    
    if (!taskName) {
      console.warn('⚠️  Skipping row with empty task name');
      continue;
    }
    
    const existing = findExisting(existingData, taskName);
    const transformedRow = transformRow(row, existing);
    transformed.push(transformedRow);
    updatedPositions.add(taskName);
    
    if (existing) {
      console.log(`  ↻ Updated: ${taskName}`);
    } else {
      console.log(`  + Added: ${taskName}`);
    }
  }
  
  // Add existing entries that weren't in CSV (preserve them)
  for (const existing of existingData) {
    const jobPosition = existing['Job Position'];
    if (!updatedPositions.has(jobPosition)) {
      transformed.push(existing);
      console.log(`  ✓ Preserved: ${jobPosition}`);
    }
  }
  
  console.log(`✅ Transformation complete: ${transformed.length} total entries`);
  return transformed;
}

/**
 * Load existing hiring data
 * @param {string} filePath - Path to existing JSON file
 * @returns {Array} Existing data or empty array
 */
function loadExistingData(filePath) {
  try {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf-8');
      const data = JSON.parse(content);
      console.log(`📂 Loaded ${data.length} existing entries`);
      return data;
    }
  } catch (error) {
    console.warn('⚠️  Could not load existing data:', error.message);
  }
  return [];
}

/**
 * Save transformed data to JSON file
 * @param {Array} data - Data to save
 * @param {string} filePath - Output file path
 */
function saveData(data, filePath) {
  try {
    const jsonContent = JSON.stringify(data, null, 4);
    fs.writeFileSync(filePath, jsonContent, 'utf-8');
    console.log(`💾 Saved ${data.length} entries to ${filePath}`);
  } catch (error) {
    console.error('❌ Error saving data:', error.message);
    throw error;
  }
}

module.exports = {
  transformData,
  transformRow,
  loadExistingData,
  saveData,
  getCurrentDateTime,
  mapBucketToStages,
  extractDivision,
  extractPIC,
  extractHireType,
  extractReplacementFor,
  extractStatus,
  resolveBucketAlias,
  mergeNotes,
  dedupeNotes,
  hasReplacementKeyword,
  hasAdditionalMarker,
  sanitizeReplacementName,
  findExisting
};
