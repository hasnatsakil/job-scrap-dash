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

const FIELD_NAMES = ['department', 'location', 'compensation', 'salary', 'comp'];

const HEADING_RAW = [
  'description', 'key responsibilities',
  'who we are', 'who you are', "what you'll do",
  'what we\'re looking for', 'about the role',
  'skills, knowledge and expertise', 'skills & knowledge',
  'nice to have', 'benefits, culture and perks',
  'the role', 'about you', 'what you bring',
  'key qualifications', 'preferred qualifications', 'minimum qualifications',
];

const HEADING_NAMES = HEADING_RAW.filter(n => n.split(/\s+/).length >= 2 || n === 'description');

function esc(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function findBoundary(text: string, start: number): number | null {
  let earliest: number | null = null;
  const slice = text.slice(start);

  for (const name of FIELD_NAMES) {
    const re = new RegExp('\\b' + esc(name) + '\\s*:', 'i');
    const m = slice.match(re);
    if (m && (earliest === null || start + m.index! < earliest)) {
      earliest = start + m.index!;
    }
  }

  for (const name of HEADING_NAMES) {
    const re = new RegExp('\\b' + esc(name) + '\\b', 'i');
    const m = slice.match(re);
    if (m && (earliest === null || start + m.index! < earliest)) {
      earliest = start + m.index!;
    }
  }

  return earliest;
}

interface HeadingHit {
  name: string;
  index: number;
  end: number;
}

function findHeadings(text: string): HeadingHit[] {
  const hits: HeadingHit[] = [];
  const seen = new Set<string>();
  for (const name of HEADING_NAMES) {
    if (seen.has(name)) continue;
    const re = new RegExp('\\b' + esc(name) + '\\b', 'i');
    const m = text.match(re);
    if (m) {
      hits.push({ name, index: m.index!, end: m.index! + name.length });
      seen.add(name);
    }
  }
  hits.sort((a, b) => a.index - b.index || b.end - a.end);

  const unique: HeadingHit[] = [];
  for (const h of hits) {
    const prev = unique[unique.length - 1];
    if (!prev || h.index >= prev.end) {
      unique.push(h);
    }
  }
  return unique;
}

function capitalizeTitle(s: string): string {
  return s.replace(/\b\w/g, c => c.toUpperCase());
}

export function parseDescription(text: string): DescBlock[] {
  const blocks: DescBlock[] = [];
  let pos = 0;
  const len = text.length;

  while (pos < len) {
    const fieldRe = new RegExp(
      '\\b(' + FIELD_NAMES.map(n => esc(n)).join('|') + ')\\s*:\\s*', 'i'
    );
    const fieldMatch = text.slice(pos).match(fieldRe);
    if (fieldMatch && fieldMatch.index === 0) {
      const label = fieldMatch[1];
      const afterField = pos + fieldMatch[0].length;
      const boundary = findBoundary(text, afterField);
      const valueEnd = boundary !== null ? boundary : len;
      const value = text.slice(afterField, valueEnd).trim();
      blocks.push({ type: 'field', label, value });
      pos = valueEnd;
      continue;
    }

    break;
  }

  const rest = text.slice(pos).trim();
  if (!rest) return blocks;

  const headings = findHeadings(rest);

  if (headings.length === 0) {
    blocks.push({ type: 'body', text: rest });
    return blocks;
  }

  if (headings[0].index > 0) {
    const before = rest.slice(0, headings[0].index).trim();
    if (before) blocks.push({ type: 'body', text: before });
  }

  for (let i = 0; i < headings.length; i++) {
    const h = headings[i];
    const nextStart = i + 1 < headings.length ? headings[i + 1].index : rest.length;
    const content = rest.slice(h.end, nextStart).trim();
    blocks.push({ type: 'heading', text: capitalizeTitle(h.name) });
    if (content) blocks.push({ type: 'body', text: content });
  }

  return blocks;
}
