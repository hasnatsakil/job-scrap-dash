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

const FIELD_LABELS = [
  'Department', 'Technology', 'Location', 'Compensation', 'Salary',
  'Work Type', 'Employment Type', 'Seniority', 'Experience',
  'Education', 'Industry', 'Function', 'Category', 'Posted Date',
];

const HEADING_PHRASES = [
  'What You\'ll Do', 'What We Offer', 'What You\'ll Bring',
  'Key Responsibilities', 'Key Qualifications', 'Key Requirements',
  'Responsibilities', 'Requirements', 'Qualifications',
  'Nice to Have', 'About the Role', 'About Us', 'About the Company',
  'Company Overview', 'Benefits', 'Perks', 'Compensation',
  'Our Mission', 'Our Vision', 'Our Values', 'Our Culture',
  'Why Join Us', 'The Role', 'Overview', 'Summary',
  'Job Description', 'Job Summary', 'Position Summary',
  'Skills', 'Experience', 'Education',
  'Benefits and Perks', 'Benefits, Culture and Perks',
  'Skills, Knowledge and Expertise',
];

function matchFields(text: string): FieldBlock[] {
  const fields: FieldBlock[] = [];
  let remaining = text;

  const pattern = new RegExp(
    `^\\s*(${FIELD_LABELS.join('|')})\\s*:\\s*(.+?)(?=\\s+(?:${FIELD_LABELS.join('|')})\\s*:\\s*|\\s+Description\\s*:\\s*|$)`,
    'i'
  );

  let match;
  let safety = 0;
  while ((match = remaining.match(pattern)) && safety < 10) {
    fields.push({ type: 'field', label: match[1].trim(), value: match[2].trim() });
    remaining = remaining.slice(match[0].length).trim();
    safety++;
  }

  return fields;
}

function findHeadings(text: string): number[] {
  const positions: number[] = [];

  for (const phrase of HEADING_PHRASES) {
    const escaped = phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(?<=^|[.!?,;\\s])${escaped}(?=[.!?,;\\s]|$)`, 'gi');
    let match;
    while ((match = regex.exec(text)) !== null) {
      positions.push(match.index);
    }
  }

  positions.sort((a, b) => a - b);
  return [...new Set(positions)];
}

export function parseDescription(text: string): DescBlock[] {
  const blocks: DescBlock[] = [];
  const clean = text.trim();
  if (!clean) return blocks;

  const fields = matchFields(clean);
  let body = clean;

  if (fields.length >= 2) {
    fields.forEach(f => blocks.push(f));
    let rem = clean;
    for (const f of fields) {
      const esc = f.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const idx = rem.search(new RegExp(f.label + '\\s*:\\s*' + esc, 'i'));
      if (idx !== -1) rem = rem.slice(idx + f.label.length + f.value.length + 2).trimStart();
    }
    body = rem;
  }

  if (!body) {
    return blocks.length > 0 ? blocks : [{ type: 'body', text: clean }];
  }

  const headingPositions = findHeadings(body);

  if (headingPositions.length === 0) {
    blocks.push({ type: 'body', text: body });
    return blocks;
  }

  let pos = 0;
  for (const hp of headingPositions) {
    if (hp > pos) {
      const preceding = body.slice(pos, hp).trim();
      if (preceding) blocks.push({ type: 'body', text: preceding });
    }
    const phrase = body.slice(hp).match(
      new RegExp(`^[^.?!\\s][^.]*?(?=[.?!\\s]|$)`)
    );
    const headingText = phrase ? phrase[0].trim() : body.slice(hp, hp + 60).trim();
    blocks.push({ type: 'heading', text: headingText });
    pos = hp + headingText.length;
  }

  if (pos < body.length) {
    const trailing = body.slice(pos).trim();
    if (trailing) blocks.push({ type: 'body', text: trailing });
  }

  return blocks;
}
