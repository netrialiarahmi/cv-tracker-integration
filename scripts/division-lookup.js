/**
 * Division lookup helper (JS twin of src/services/division.py).
 *
 * Loads `data/division_lookup.json` (built by `scripts/build_division_lookup.py`)
 * and resolves a Planner Job Position to its canonical
 * {division, directorate, department, section} hierarchy.
 */

const fs = require('fs');
const path = require('path');

const LOOKUP_PATH = path.join(__dirname, '..', 'data', 'division_lookup.json');

const PREFIXES = [
  'sr.', 'sr ', 'senior ',
  'jr.', 'jr ', 'junior ',
  'asst.', 'asst ', 'assistant ',
  'deputy ',
  'lead ', 'head of ', 'chief ',
  'general manager', 'gm ',
  'managing '
];

let _cache = null;

function loadLookup() {
  if (_cache !== null) return _cache;
  try {
    if (fs.existsSync(LOOKUP_PATH)) {
      const raw = fs.readFileSync(LOOKUP_PATH, 'utf-8');
      const payload = JSON.parse(raw);
      _cache = (payload && typeof payload === 'object' && payload.entries) || {};
      return _cache;
    }
  } catch (err) {
    console.warn(`⚠️  Failed to load division lookup: ${err.message}`);
  }
  _cache = {};
  return _cache;
}

function normalizeTitle(title) {
  if (!title) return '';
  let t = String(title).toLowerCase().trim();
  t = t.replace(/\([^)]*\)/g, ' ');
  t = t.replace(/[^\w\s]/g, ' ');
  t = t.replace(/\s+/g, ' ').trim();
  for (const p of PREFIXES) {
    if (t.startsWith(p)) {
      t = t.slice(p.length).trim();
      break;
    }
  }
  return t;
}

function tokenSetMatch(query, entries) {
  const qTokens = new Set(query.split(' ').filter(Boolean));
  if (qTokens.size === 0) return null;
  let bestKey = null;
  let bestScore = 0;
  for (const key of Object.keys(entries)) {
    const kTokens = new Set(key.split(' ').filter(Boolean));
    if (kTokens.size === 0) continue;
    let overlap = 0;
    for (const t of qTokens) if (kTokens.has(t)) overlap++;
    const subset =
      [...qTokens].every(t => kTokens.has(t)) ||
      [...kTokens].every(t => qTokens.has(t));
    if (overlap >= 2 || (overlap >= 1 && subset)) {
      const score = overlap / Math.max(qTokens.size, kTokens.size);
      if (score > bestScore) {
        bestScore = score;
        bestKey = key;
      }
    }
  }
  return bestScore >= 0.5 ? bestKey : null;
}

/**
 * Resolve the canonical division hierarchy for a job title.
 * @param {string} jobPosition
 * @param {string} currentDivision  Division derived from Planner labels (fallback)
 * @returns {{division:string, directorate:string, department:string, section:string, source:string}}
 */
function resolveDivision(jobPosition, currentDivision = '') {
  const entries = loadLookup();
  const fallback = {
    division: currentDivision || '',
    directorate: '',
    department: '',
    section: '',
    source: 'planner'
  };
  if (!entries || Object.keys(entries).length === 0 || !jobPosition) {
    return fallback;
  }
  const key = normalizeTitle(jobPosition);
  const hit = entries[key];
  if (hit) {
    return {
      division: hit.division || '',
      directorate: hit.directorate || '',
      department: hit.department || '',
      section: hit.section || '',
      source: 'lookup_exact'
    };
  }
  const fuzzy = tokenSetMatch(key, entries);
  if (fuzzy) {
    const fhit = entries[fuzzy];
    return {
      division: fhit.division || '',
      directorate: fhit.directorate || '',
      department: fhit.department || '',
      section: fhit.section || '',
      source: 'lookup_fuzzy'
    };
  }
  return fallback;
}

module.exports = {
  loadLookup,
  normalizeTitle,
  resolveDivision
};
