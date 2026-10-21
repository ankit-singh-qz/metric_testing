# Installation and Use — GitHub Metrics Bundle

## 1. Copy files into your repository

Copy `.github/`, `docs/`, `scripts/`, `AI_USAGE.md`, and this file into the root of your Git repository.

If `.github/` or `docs/` already exists, **merge** the new files; do not replace existing workflows, templates, or documentation you rely on.

## 2. Verify locally (optional)

The metrics snapshot script uses only the Python standard library. From the repository root:

```powershell
python -m py_compile scripts/github_metrics_snapshot.py
```

To pull live GitHub metrics, authenticate with [GitHub CLI](https://cli.github.com/) (`gh auth login`) or set `$env:GITHUB_TOKEN` to a fine-grained PAT, then:

```powershell
python scripts/github_metrics_snapshot.py --days 30
```

## 3. Push via a branch

From the **repository root**:

```powershell
git checkout -b feature/github-metrics-bundle
git add .github docs scripts AI_USAGE.md INSTALL_AND_USE.md
git commit -m "Add GitHub metrics bundle for AI-Telemetry"
git push -u origin feature/github-metrics-bundle
```

Open a pull request on GitHub, link it to an issue, disclose AI assistance, and request a real review. Review, throughput, rework, lead-time, and attribution metrics should come from actual activity; do not fabricate events to improve the results.

## 4. Deployment and all 7 metrics

After merges to `main`, **Deploy Metrics Bundle** runs when **Metrics CI** succeeds and records a successful `production` deployment in GitHub (for deployment frequency and lead time). See [docs/ai-telemetry-github.md](docs/ai-telemetry-github.md) for the full checklist, including Cursor AI-authored code %.

Optional: `.github/workflows/deploy-python-example.yml.example` shows how to add a real hosting provider. Do not count CI alone as a deployment.
