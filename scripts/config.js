/**
 * Configuration for Microsoft Planner to Hiring Tracker data transformation
 */

const config = {
  // Timezone for timestamps
  timezone: 'Asia/Jakarta',

  // CSV delimiter (Planner exports use semicolon)
  csvDelimiter: ';',

  // Column names in Planner export
  columns: {
    taskId: 'Task ID',
    taskName: 'Task Name',
    bucketName: 'Bucket Name',
    progress: 'Progress',
    priority: 'Priority',
    assignedTo: 'Assigned To',
    createdBy: 'Created By',
    createdDate: 'Created Date',
    startDate: 'Start date',
    dueDate: 'Due date',
    labels: 'Labels',
    description: 'Description',
    completedDate: 'Completed Date'
  },

  // Alternative column names (Planner export format changes over time)
  columnAliases: {
    'Task Name': ['Task name', 'Task', 'Name'],
    'Bucket Name': ['Bucket name', 'Bucket', 'Board column', 'Column'],
    'Task ID': ['Task Id', 'TaskID', 'ID'],
    'Assigned To': ['Assigned to', 'Assigned To ', 'AssignedTo'],
    'Created By': ['Created by', 'CreatedBy'],
    'Created Date': ['Created date', 'CreatedDate'],
    'Start date': ['Start Date', 'StartDate'],
    'Due date': ['Due Date', 'DueDate'],
    'Completed Date': ['Completed date', 'CompletedDate'],
    'Labels': ['Label', 'Tags'],
    'Description': ['Notes', 'Details'],
    'Progress': ['Status'],
    'Priority': ['Urgency']
  },

  // Bucket name to stage mapping
  bucketStages: {
    'Backlog (Employee Req Form)': {
      initialScreening: false,
      interview: false,
      skillTest: false,
      finalInterview: false,
      offering: false,
      contractSign: false,
      onBoarding: false
    },
    'Approval Circular & Review (Paralel Screening CV)': {
      initialScreening: true,
      interview: false,
      skillTest: false,
      finalInterview: false,
      offering: false,
      contractSign: false,
      onBoarding: false
    },
    'HR & User Interview + Skill Test': {
      initialScreening: true,
      interview: true,
      skillTest: false,
      finalInterview: false,
      offering: false,
      contractSign: false,
      onBoarding: false
    },
    'Offering': {
      initialScreening: true,
      interview: true,
      skillTest: true,
      finalInterview: true,
      offering: true,
      contractSign: false,
      onBoarding: false
    },
    'Order for Contract Sign & ID dkk': {
      initialScreening: true,
      interview: true,
      skillTest: true,
      finalInterview: true,
      offering: true,
      contractSign: true,
      onBoarding: false
    },
    'Sudah Sign Contract Lanjut Onboarding': {
      initialScreening: true,
      interview: true,
      skillTest: true,
      finalInterview: true,
      offering: true,
      contractSign: true,
      onBoarding: true
    }
  },

  // Special bucket handling
  specialBuckets: {
    hold: 'HOLD',
    canceled: 'CANCELED',
    inProgress: 'In Progress (Untuk Task selain Recruitment Reguler)'
  },

  // Progress status
  completedStatus: 'Completed',

  // Division mapping from Labels
  divisionMapping: {
    'Technology': 'Technology Engineering Division',
    'Redaksi Teks': 'Kompas.com News - Text Department',
    'Redaksi Video': 'Kompas.com News - Video & Social Media Department',
    'Integrated Marketing': 'Lative Ads Department', // Default, may need context
    'Marcomm Kompascom': 'Marketing Communication Kompas.com',
    'VCBL': 'VCBL & Pasangiklan',
    'Kompascom Sales': 'Sales',
    'Product & Data': 'Product & Data Division',
    'Technology Engineering': 'Technology Engineering Division',
    'Kompas.com News': 'Kompas.com News - Text Department'
  },

  // Labels to ignore (contract types, hire types)
  ignoreLabels: ['Konpro', 'KKWT', 'Freelance', 'Additional', 'Replacement'],

  // Hire type labels
  hireTypeLabels: {
    additional: 'Additional',
    replacement: 'Replacement'
  },

  // Status detection keywords (checked against Labels + Task Name, case-insensitive)
  // Order matters: first match wins.
  statusKeywords: [
    { keyword: 'intern', value: 'Intern' },
    { keyword: 'freelance', value: 'Freelance' }
  ],
  // Default status when no keyword matches
  defaultStatus: 'Contract',

  // Preferred sheet name to read (case-insensitive). Falls back to current
  // detection logic (most-known-columns, then most-rows) when not present.
  preferredSheetName: 'Consolidate Data',

  // Short bucket-name aliases used in the "Consolidate Data" tab.
  // Each maps a short/alt label to one of the canonical keys in `bucketStages`.
  bucketAliases: {
    'backlog': 'Backlog (Employee Req Form)',
    'employee req form': 'Backlog (Employee Req Form)',
    'initial': 'Approval Circular & Review (Paralel Screening CV)',
    'initial screening': 'Approval Circular & Review (Paralel Screening CV)',
    'initial hr': 'Approval Circular & Review (Paralel Screening CV)',
    'approval circular': 'Approval Circular & Review (Paralel Screening CV)',
    'paralel screening': 'Approval Circular & Review (Paralel Screening CV)',
    'hr & user interview': 'HR & User Interview + Skill Test',
    'hr user interview': 'HR & User Interview + Skill Test',
    'user interview': 'HR & User Interview + Skill Test',
    'skill test': 'HR & User Interview + Skill Test',
    'final interview': 'HR & User Interview + Skill Test',
    'final': 'HR & User Interview + Skill Test',
    'offering': 'Offering',
    'job offer': 'Offering',
    'order for contract sign': 'Order for Contract Sign & ID dkk',
    'contract sign': 'Order for Contract Sign & ID dkk',
    'contract': 'Order for Contract Sign & ID dkk',
    'sudah sign contract': 'Sudah Sign Contract Lanjut Onboarding',
    'onboarding': 'Sudah Sign Contract Lanjut Onboarding',
    'on boarding': 'Sudah Sign Contract Lanjut Onboarding',
    'on board': 'Sudah Sign Contract Lanjut Onboarding'
  },

  // PIC name mapping
  picMapping: {
    'Adelia Galuh H': 'adelia',
    'Rizky Pangestu': 'rizky',
    'Novinda Riski': 'vania',
    'Member': 'adelia', // default
    'default': 'adelia'
  },

  // Replacement keywords (matched with word boundaries). Sorted by length
  // at use time so 'replacement' wins over 'replace'. 'menggantikan' covers
  // the Indonesian verb form; 'ganti' is shorter form of 'pengganti'.
  replacementKeywords: [
    'replacement',
    'menggantikan',
    'pengganti',
    'replace',
    'ganti',
    'repl',
  ],

  // Stop-words: when a captured "Replacement For" name matches one of these
  // (case-insensitive, exact match), reject the capture entirely. Prevents
  // accidental matches like "Replace slot Oik" capturing "slot" instead of
  // "Oik" before the multi-word logic kicks in.
  replacementStopWords: [
    'slot', 'ex', 'the', 'dan', 'dari', 'untuk', 'freelance', 'konpro',
    'kandidat', 'yang', 'yg', 'yng', 'akan', 'sudah', 'belum', 'maternity',
    'resign', 'mundur', 'pindah', 'rotasi', 'posisi', 'sementara', 'magang',
    'kampus', 'sales', 'ke', 'saja', 'bulan', 'akhir', 'nya', 'prev',
    'previous', 'ment', 'a', 'an', 'atas', 'nama', 'na', 'tbc', 'update',
  ],

  // Truncate a captured name at the first occurrence of any of these
  // junk-suffix tokens (case-insensitive, word-boundary). Picks up
  // narrative continuations like "Idris yg di rolling" → "Idris".
  replacementJunkSuffixes: [
    'yang', 'yg', 'yng', 'maternity', 'resign', 'mundur', 'pindah',
    'dipromosi', 'dipromote', 'rotasi', 'karena', 'untuk', 'update',
    'belum', 'dari', 'ke', 'akan', 'sudah', 'sedang', 'tetap',
    'atau', 'or', 'tapi', 'but', 'dengan', 'with',
  ],

  // Maximum length for the merged Notes field (raised from 500 to avoid
  // mid-name truncation in long update logs).
  notesMaxLength: 1000,

  // Fields to preserve from existing data
  preserveFields: [
    'Job Description',
    'Attachments'
  ],

  // Date format for Last Updated
  dateFormat: 'YYYY-MM-DD HH:mm:ss',

  // Default values
  defaults: {
    division: 'Product & Data Division',
    pic: 'adelia',
    notes: '',
    jobDescription: '',
    attachments: [],
    freeze: false,
    hireType: 'Additional',
    replacementFor: '',
    createdDate: '',
    status: 'Contract'
  }
};

module.exports = config;
