export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const token = process.env.GITHUB_PAT;
  if (!token) {
    return res.status(500).json({ error: 'GITHUB_PAT not configured in Vercel environment variables' });
  }

  const resp = await fetch(
    'https://api.github.com/repos/hasnatsakil/job-scrap-dash/actions/workflows/scrape.yml/dispatches',
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/vnd.github.v3+json',
        'User-Agent': 'job-scrap-dash',
      },
      body: JSON.stringify({ ref: 'main' }),
    }
  );

  if (resp.ok) {
    return res.status(200).json({ status: 'triggered' });
  }

  const text = await resp.text();
  return res.status(resp.status).json({ error: `GitHub API error: ${resp.status} ${text}` });
}
