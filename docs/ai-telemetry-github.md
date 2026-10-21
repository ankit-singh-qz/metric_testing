# AI-Telemetry and GitHub — All 7 Metrics

This repository is set up so you can observe all seven engineering metrics from [github-metrics-guide.md](./github-metrics-guide.md) when GitHub is connected to your AI / delivery telemetry stack (for example Cursor AI Code Tracking plus GitHub PR and deployment events, or an OTLP collector ingesting `cursor.cloud_agent.*` logs for GitHub-hosted repos).

| # | Metric | Primary data source | What this repo provides |
|---|--------|---------------------|-------------------------|
| 1 | AI-authored code % | Cursor [AI Code Tracking API](https://cursor.com/docs/account/teams/ai-code-tracking-api) (`/analytics/ai-code/commits`) or IDE-attributed commits | Commit your changes from Cursor in this repo; `docs/ai-attribution.json` for declared bundle scope (not a line-level %) |
| 2 | PR throughput | GitHub Pull Requests (merged) | Feature branches, PR template, CI on PRs |
| 3 | Review wait time | GitHub Pull Request Reviews (first human review timestamp) | PR template asks for human review; use `Closes #issue` workflow |
| 4 | Rework rate | GitHub reviews + commits after first review | Request changes on PRs and push fix commits (normal review loop) |
| 5 | Lead time for changes | Issue timestamps → merge or → production deployment | Issue templates + `Closes #n` in PRs; deploy workflow on `main` |
| 6 | Deployment frequency | GitHub Deployments / Environments (`production`) | [deploy-metrics.yml](../.github/workflows/deploy-metrics.yml) records successful production deployments after CI |
| 7 | Attribution mapping rate | GitHub linked issues on PRs | PR template **Linked issue** section; issue templates for traceability |

## One-time setup

1. **GitHub** — Enable Issues. Optionally add a `production` environment under **Settings → Environments** (no secrets required for the demo deploy recorder).
2. **Cursor (AI-authored code %)** — Open this repo as the **workspace root** (single-root; multi-root is not supported for AI commit metrics). Use **Source Control** in Cursor (or the terminal panel in the same window) to commit and push so `/analytics/ai-code/commits` can attribute Tab vs Composer vs non-AI lines. Enterprise teams use the AI Code Tracking API; see Cursor docs for API keys and date windows.
3. **OpenTelemetry (optional)** — For Cloud Agent activity on GitHub, enable OpenTelemetry Export and the `cloud_agents` family. Events such as `cursor.cloud_agent.pull_request` and `cursor.cloud_agent.commit` include `vcs.repository.url` for GitHub repos only.

## Generate signal (recommended sequence)

1. Open an issue from **Feature request** or **Bug report**.
2. In Cursor, implement on a branch; commit from Cursor (not only an external GUI) for metric 1.
3. Open a PR using the template: fill **Linked issue** (`Closes #123`), AI disclosure, and validation checkboxes.
4. Request review from a teammate; they submit a review (approve or request changes).
5. If changes were requested, push at least one follow-up commit (metric 4).
6. Merge after approval (metrics 2, 3, 5, 7).
7. After merge to `main`, **Metrics CI** runs, then **Deploy Metrics Bundle** records a `production` deployment (metrics 5 and 6).

## GitHub webhooks

If you configured a repo webhook, a **push** fires after you push from Cursor; **pull_request** and **pull_request_review** fire when you open or update a PR and when someone submits a review on GitHub. Check **Settings → Webhooks → Recent Deliveries** if events are missing. Webhooks do not replace Cursor for metric 1 (AI line attribution).

## Verify metrics locally

From the repository root, authenticate one of these ways:

- [GitHub CLI](https://cli.github.com/): `gh auth login`
- Or set a fine-grained PAT: `$env:GITHUB_TOKEN = "github_pat_..."` (repo read access to pulls, issues, deployments)

```powershell
python scripts/github_metrics_snapshot.py --days 30
```

The script prints JSON for metrics **2–7** from the GitHub API. **AI-authored code %** must be queried from Cursor (or your telemetry backend), not from GitHub alone.

Example (Enterprise API key as username, empty password):

```powershell
$pair = "${env:CURSOR_API_KEY}:"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$basic = [Convert]::ToBase64String($bytes)
gh api "https://api.cursor.com/analytics/ai-code/commits?startDate=30d&endDate=now" `
  -H "Authorization: Basic $basic"
```

Aggregate `tabLinesAdded + composerLinesAdded` over `totalLinesAdded` for your repo and window to approximate AI-authored code %.

## Definitions reminder

Always report the measurement window, denominator, and tool-specific definitions with any number. See [github-metrics-guide.md](./github-metrics-guide.md) for suggested definitions and caveats.
