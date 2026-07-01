interface FieldBlock {
  type: 'field';
  label: string;
  value: string;
}

interface HeadingBlock {
  type: 'heading';
  text: string;
}

interface BodyBlock {
  type: 'body';
  text: string;
}

export type DescBlock = FieldBlock | HeadingBlock | BodyBlock;

const FIELD_KEYS = ['department', 'location', 'compensation', 'salary', 'comp'];

const HEADING_KEYWORDS = [
  'description', 'key responsibilities', 'responsibilities',
  'skills', 'knowledge', 'expertise', 'skills, knowledge and expertise',
  'nice to have', 'benefits', 'culture', 'perks',
  'benefits, culture and perks', 'about', 'about us', 'about the role',
  'requirements', 'qualifications', "what you'll do", 'what we\'re looking for',
  'education', 'experience', 'summary', 'the role', 'about you',
  'who you are', 'what you bring', 'key qualifications',
  'preferred qualifications', 'minimum qualifications',
];

function isHeading(line: string): boolean {
  const trimmed = line.trim();
  if (!trimmed || trimmed.length > 80) return false;
  if (/[.!?:;]$/.test(trimmed)) return false;
  const lower = trimmed.toLowerCase();
  if (HEADING_KEYWORDS.some(kw => lower === kw || lower.startsWith(kw + ' ') || lower.startsWith(kw + ':'))) return true;
  if (/^[A-Z][a-z]+(\s[A-Z][a-z]+)*$/.test(trimmed) && trimmed.split(/\s+/).length <= 6) return true;
  return false;
}

export function parseDescription(text: string): DescBlock[] {
  const paragraphs = text.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
  const blocks: DescBlock[] = [];

  for (const para of paragraphs) {
    const lines = para.split('\n').map(l => l.trim()).filter(Boolean);
    const fieldMatches = lines.map(l => l.match(/^(Department|Location|Compensation|Salary|Comp)\s*:\s*(.+)$/i));
    if (fieldMatches.every(m => m !== null) && fieldMatches.length > 0) {
      for (const m of fieldMatches) {
        blocks.push({ type: 'field', label: m![1], value: m![2].trim() });
      }
      continue;
    }

    if (lines.length === 1 && isHeading(lines[0])) {
      blocks.push({ type: 'heading', text: lines[0] });
      continue;
    }

    blocks.push({ type: 'body', text: para });
  }

  return blocks;
}
