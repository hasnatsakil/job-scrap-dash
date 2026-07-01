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

function isHeadingParagraph(text: string): boolean {
  const trimmed = text.trim();
  if (!trimmed) return false;
  if (trimmed.length > 80) return false;
  if (/[.!?;]$/.test(trimmed)) return false;
  if (/:\s*$/.test(trimmed)) return false;
  if (!/^[A-Z]/.test(trimmed)) return false;
  const words = trimmed.split(/\s+/);
  if (words.length < 2) return false;
  if (words.length > 12) return false;
  const alphaWords = words.filter(w => /^[a-zA-Z(),&/]+$/.test(w));
  if (alphaWords.length / words.length < 0.5) return false;
  if (/^(\d|[A-Z]\.)/.test(trimmed)) return false;
  if (/^[\d$£€]/.test(trimmed)) return false;
  return true;
}

function extractFields(text: string): FieldBlock[] {
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
  const fieldRe = /^([A-Za-z][\w\s,&/-]*?):\s*(.+)$/;
  const result: FieldBlock[] = [];

  for (const line of lines) {
    const m = line.match(fieldRe);
    if (m && m[1].length <= 25) {
      result.push({ type: 'field', label: m[1], value: m[2] });
    }
  }

  return result;
}

export function parseDescription(text: string): DescBlock[] {
  const blocks: DescBlock[] = [];
  const paragraphs = text.split(/\n\s*\n/).filter(p => p.trim());

  for (const para of paragraphs) {
    if (isHeadingParagraph(para)) {
      blocks.push({ type: 'heading', text: para.trim() });
    } else {
      const fields = extractFields(para);
      if (fields.length >= 2) {
        blocks.push(...fields);
      } else {
        blocks.push({ type: 'body', text: para.trim() });
      }
    }
  }

  if (blocks.length === 0 && text.trim()) {
    blocks.push({ type: 'body', text: text.trim() });
  }

  return blocks;
}
