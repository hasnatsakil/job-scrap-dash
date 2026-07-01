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

const FIELD_NAMES = ['department', 'location', 'compensation', 'salary', 'comp', 'compensation range'];

function isHeadingLine(line: string): boolean {
  if (!line || line.length > 60) return false;
  if (/[.!?;]$/.test(line)) return false;
  if (!/^[A-Z]/.test(line)) return false;
  const words = line.split(/\s+/);
  const alpha = words.filter(w => /^[a-zA-Z]+$/.test(w)).length;
  if (alpha / words.length < 0.4) return false;
  if (/^\w[\w\s]*:/i.test(line)) return false;
  return true;
}

export function parseDescription(text: string): DescBlock[] {
  const blocks: DescBlock[] = [];
  const lines = text.split('\n').map(l => l.trim());

  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const fieldRe = new RegExp(
      '^(' + FIELD_NAMES.map(n => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')\\s*:\\s*(.+)$', 'i'
    );
    const m = line.match(fieldRe);
    if (m) {
      blocks.push({ type: 'field', label: m[1], value: m[2].trim() });
      i++;
    } else {
      break;
    }
  }

  const classifications: { type: 'heading' | 'body'; text: string }[] = [];
  for (; i < lines.length; i++) {
    const line = lines[i];
    if (!line) continue;
    classifications.push({
      type: isHeadingLine(line) ? 'heading' : 'body',
      text: line,
    });
  }

  for (let j = 0; j < classifications.length; j++) {
    const c = classifications[j];
    if (c.type === 'heading') {
      blocks.push({ type: 'heading', text: c.text });
    } else {
      let merged = c.text;
      while (j + 1 < classifications.length && classifications[j + 1].type === 'body') {
        j++;
        merged += '\n' + classifications[j].text;
      }
      blocks.push({ type: 'body', text: merged });
    }
  }

  return blocks;
}
