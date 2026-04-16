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

  // PIC name mapping
  picMapping: {
    'Adelia Galuh H': 'adelia',
    'Rizky Pangestu': 'rizky',
    'Novinda Riski': 'vania',
    'Member': 'adelia', // default
    'default': 'adelia'
  },

  // Replacement keywords
  replacementKeywords: ['replace', 'pengganti', 'replacement'],

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
    createdDate: ''
  }
};

module.exports = config;
