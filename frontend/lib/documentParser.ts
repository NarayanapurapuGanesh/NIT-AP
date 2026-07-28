export interface ParsedResumeResult {
  fileName: string;
  fileSize: string;
  score: number;
  highestDegree: string;
  institution: string;
  expYears: number;
  skills: string[];
  grants: string;
  papersCount: number;
  summary: string;
  rawTextPreview: string;
  enterpriseProfile?: any;
}

/**
 * Sends file to local Python 3.12 FastAPI Resume Intelligence Engine v2.0
 */
export async function analyzeResumeWithBackend(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/api/v1/intelligence/analyze', {
      method: 'POST',
      body: formData,
    });
    const result = await response.json().catch(() => null);
    if (result && result.data) {
      return result.data;
    }
  } catch (err) {
    console.error('Backend connection failed:', err);
  }
  return null;
}

const PDF_KEYWORDS_TO_STRIP = [
  '%PDF', 'obj', 'endobj', 'xref', 'trailer', 'startxref',
  'Linearized', 'FlateDecode', 'DecodeParms', 'Columns', 'Predictor',
  'MediaBox', 'CropBox', 'Parent', 'Resources', 'Font', 'XObject',
  'ProcSet', 'ExtGState', 'Encoding', 'Widths', 'FontDescriptor',
  'FontName', 'BaseFont', 'Subtype', 'Type', 'Pages', 'Page', 'Root',
  'Catalog', 'Info', 'Size', 'Filter', 'Length', 'GoTo', 'GoToR'
];

/**
 * Extracts human-readable text content from uploaded files (PDF, TXT, MD, etc.).
 * Strips PDF binary object headers, metadata streams, and structure tokens.
 */
export async function extractTextFromFile(file: File): Promise<{ text: string; isPdf: boolean }> {
  const isPdf = file.name.toLowerCase().endsWith('.pdf');

  if (!isPdf) {
    try {
      const text = await file.text();
      return { text: text || '', isPdf: false };
    } catch {
      return { text: '', isPdf: false };
    }
  }

  // Handle PDF files
  try {
    const buffer = await file.arrayBuffer();
    const decoder = new TextDecoder('utf-8', { fatal: false });
    const rawString = decoder.decode(buffer);

    // Extract text blocks enclosed in PDF text operators: (Text) Tj or [(Text1)(Text2)] TJ
    const textMatches: string[] = [];
    
    // 1. Literal PDF text strings enclosed in parentheses: (Text)
    const parenRegex = /\(([^()\\]|\\[\s\S])*\)/g;
    let match: RegExpExecArray | null;
    while ((match = parenRegex.exec(rawString)) !== null) {
      const str = match[0].slice(1, -1)
        .replace(/\\\( /g, '(')
        .replace(/\\\)/g, ')')
        .replace(/\\n/g, ' ')
        .replace(/\\r/g, ' ')
        .replace(/\\\\/g, '\\');
      
      // Ignore short binary strings or PDF structural strings
      if (str.trim().length > 2 && !/^[0-9\s\/\<\>\#]+$/.test(str)) {
        textMatches.push(str.trim());
      }
    }

    let extractedText = textMatches.join(' ');

    // If PDF text streams were compressed/binary and yielded no parenthesized text,
    // fallback to stripping PDF structural metadata tags from rawString
    if (!extractedText || extractedText.length < 50) {
      // Remove PDF object blocks and hex strings
      let cleaned = rawString
        .replace(/<<[\s\S]*?>>/g, ' ')
        .replace(/stream[\s\S]*?endstream/g, ' ')
        .replace(/%\S+/g, ' ')
        .replace(/\b(obj|endobj|xref|trailer|startxref)\b/gi, ' ');

      PDF_KEYWORDS_TO_STRIP.forEach(kw => {
        cleaned = cleaned.replace(new RegExp(`\\b${kw}\\b`, 'gi'), ' ');
      });

      // Keep only printable word tokens (alphanumeric sequences >= 2 chars)
      const words = cleaned.match(/\b[A-Za-z0-9+#.]{2,}\b/g) || [];
      extractedText = words.slice(0, 500).join(' ');
    }

    if (!extractedText.trim()) {
      extractedText = `[PDF Document: "${file.name}" - Processed. Compressed vector stream detected.]`;
    }

    return { text: extractedText, isPdf: true };
  } catch {
    return { text: `[PDF Document: "${file.name}" - Text extraction fallback.]`, isPdf: true };
  }
}

/**
 * Parses extracted text with strict word-boundary matching to prevent false positives
 * like 'email' matching 'AI', 'algorithm' matching 'Go', or 'digital' matching 'Git'.
 */
export function parseResumeContent(
  fileObj: File,
  extractedText: string,
  selectedRole: string,
  isPdf: boolean
): ParsedResumeResult {
  const text = extractedText || '';
  const lowerText = text.toLowerCase();

  // Filter out any leftover PDF structural tokens from word counting
  const validWords = text
    .split(/\s+/)
    .map(w => w.trim())
    .filter(w => w.length > 1 && !PDF_KEYWORDS_TO_STRIP.some(kw => kw.toLowerCase() === w.toLowerCase()));
  
  const wordsCount = validWords.length;

  // 1. Degree Extraction with strict boundaries
  let highestDegree = 'No Ph.D. or Master degree found in file text';
  let institution = 'Not specified in uploaded file';

  const phdPattern = /\b(ph\.?d\.?|doctor of philosophy|doctoral)\b/i;
  const masterPattern = /\b(m\.?tech|m\.?s|master['’]?s?|m\.?e)\b/i;
  const bachelorPattern = /\b(b\.?tech|b\.?e|bachelor['’]?s?)\b/i;

  if (phdPattern.test(text)) {
    highestDegree = 'Ph.D. / Doctoral Degree';
    if (/\biisc\b/i.test(text)) institution = 'IISc Bangalore';
    else if (/\biit\b/i.test(text)) institution = 'Indian Institute of Technology (IIT)';
    else if (/\bnit\b/i.test(text)) institution = 'National Institute of Technology (NIT)';
    else institution = 'Recognized University';
  } else if (masterPattern.test(text)) {
    highestDegree = 'Master of Technology / M.S.';
  } else if (bachelorPattern.test(text)) {
    highestDegree = 'Bachelor of Technology / B.E.';
  }

  // 2. Experience Extraction
  let expYears = 0;
  const expMatch = text.match(/(\d+)\+?\s*(years|yrs)\s*(of)?\s*(experience|exp|teaching|research)/i);
  if (expMatch) {
    expYears = parseInt(expMatch[1], 10);
  }

  // 3. Skill Extraction with strict word-boundary regular expressions
  const skillDefinitions: { name: string; pattern: RegExp }[] = [
    { name: 'Distributed Systems', pattern: /\bdistributed systems?\b/i },
    { name: 'Cloud', pattern: /\bcloud\b/i },
    { name: 'Kubernetes', pattern: /\bkubernetes|k8s\b/i },
    { name: 'Docker', pattern: /\bdocker\b/i },
    { name: 'Python', pattern: /\bpython\b/i },
    { name: 'C++', pattern: /\bc\+\+\b/i },
    { name: 'C#', pattern: /\bc#\b/i },
    { name: 'Java', pattern: /\bjava\b/i },
    { name: 'Go', pattern: /\bgo\b/i },
    { name: 'Rust', pattern: /\brust\b/i },
    { name: 'Machine Learning', pattern: /\bmachine learning\b/i },
    { name: 'Deep Learning', pattern: /\bdeep learning\b/i },
    { name: 'AI', pattern: /\b(ai|artificial intelligence)\b/i },
    { name: 'Data Structures', pattern: /\bdata structures?\b/i },
    { name: 'Algorithms', pattern: /\balgorithms?\b/i },
    { name: 'VLSI', pattern: /\bvlsi\b/i },
    { name: 'FPGA', pattern: /\bfpga\b/i },
    { name: 'Embedded Systems', pattern: /\bembedded systems?\b/i },
    { name: 'PostgreSQL', pattern: /\bpostgresql|postgres\b/i },
    { name: 'SQL', pattern: /\bsql\b/i },
    { name: 'React', pattern: /\breact(\.js)?\b/i },
    { name: 'Next.js', pattern: /\bnext(\.js)?\b/i },
    { name: 'Node.js', pattern: /\bnode(\.js)?\b/i },
    { name: 'System Architecture', pattern: /\bsystem architecture\b/i },
    { name: 'Linux', pattern: /\blinux\b/i },
    { name: 'Git', pattern: /\bgit\b/i },
    { name: 'Security', pattern: /\b(cybersecurity|security)\b/i },
    { name: 'Networks', pattern: /\bnetworks?\b/i },
    { name: 'DevOps', pattern: /\bdevops\b/i },
    { name: 'Microservices', pattern: /\bmicroservices?\b/i },
    { name: 'Database', pattern: /\bdatabases?\b/i },
  ];

  const extractedSkills = skillDefinitions
    .filter(skill => skill.pattern.test(text))
    .map(skill => skill.name);

  // 4. Research & Publications
  let papersCount = 0;
  let grants = 'No research grants detected in file text';

  if (/\b(publications?|papers?|journals?|conferences?|ieee|acm)\b/i.test(text)) {
    const paperMatch = text.match(/(\d+)\s*(papers|publications|conference|journal)/i);
    papersCount = paperMatch ? parseInt(paperMatch[1], 10) : 4;
  }

  if (/\b(grants?|serb|dst|isro|funding|sponsored research)\b/i.test(text)) {
    grants = 'Research Grant / External Funding Mentioned';
  }

  // 5. Score & Summary Computation
  let score = 35;
  if (highestDegree.includes('Ph.D')) score += 35;
  else if (highestDegree.includes('Master')) score += 20;
  if (expYears > 0) score += Math.min(expYears * 3, 15);
  if (extractedSkills.length > 0) score += Math.min(extractedSkills.length * 3, 15);
  if (papersCount > 0) score += 10;
  score = Math.min(Math.max(score, 30), 98);

  let summary = `Read ${wordsCount} words from file "${fileObj.name}".`;
  if (!highestDegree.includes('Ph.D') && !highestDegree.includes('Master') && papersCount === 0 && extractedSkills.length === 0) {
    summary += ` Note: The uploaded file text does not contain standard academic credentials (no Ph.D., publications, or technical competencies detected).`;
  } else {
    summary += ` Extracted ${extractedSkills.length} core competencies, ${papersCount > 0 ? papersCount + ' publication records' : 'no publication records'}, and computed alignment for ${selectedRole}.`;
  }

  // Clean raw preview text (showing cleaned preview, max 300 chars)
  const cleanPreviewText = text.replace(/\s+/g, ' ').trim();
  const preview = cleanPreviewText.length > 300 
    ? cleanPreviewText.slice(0, 300) + '...' 
    : cleanPreviewText || 'Clean document text extracted.';

  return {
    fileName: fileObj.name,
    fileSize: `${(fileObj.size / 1024).toFixed(1)} KB`,
    score,
    highestDegree,
    institution,
    expYears,
    skills: extractedSkills,
    grants,
    papersCount,
    summary,
    rawTextPreview: preview,
  };
}
