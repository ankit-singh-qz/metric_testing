# GitHub Engineering Metrics Guide

This guide defines candidate measurements. Confirm the definitions used by your actual dashboard before comparing numbers; tools often calculate similarly named metrics differently.

| Metric | Suggested definition | Data needed / caveat |
|---|---|---|
| AI-authored code % | AI-attributed changed lines divided by all changed code lines in the measurement scope | Use reliable IDE/platform attribution or explicit, auditable metadata. A PR checkbox alone does not establish an exact line percentage. |
| PR throughput | Number of PRs merged during a period | Use merged timestamps and a clearly stated date window. |
| Review wait time | Median time from PR creation to the first submitted human review | Use PR creation and first review timestamps; state whether bot reviews are excluded. |
| Rework rate | PRs requiring code changes after review feedback divided by PRs reviewed | Define what counts as rework and inspect review/commit events. Do not infer it merely from commit count. |
| Lead time for changes | Choose and document either first commit to production or issue start to production | Use a consistent start/end definition and actual merge/deployment timestamps. |
| Deployment frequency | Successful production deployments per day/week | A configured deployment system and successful deployment events are required. CI runs are not deployments. |
| Attribution mapping rate | Changes or PRs linked to a valid issue/work item and contributor divided by all in-scope changes | Define the denominator and validate links/identity mapping. |

## AI-Telemetry on GitHub

For a step-by-step setup that covers all seven metrics (including Cursor AI code % and GitHub deployment events), see [ai-telemetry-github.md](./ai-telemetry-github.md).

## What this bundle supports

- [metrics-ci.yml](../.github/workflows/metrics-ci.yml) validates the metrics snapshot script and attribution metadata on pull requests and selected branch pushes.
- PR and issue templates encourage consistent issue linkage, review notes, validation, and AI disclosure.
- `scripts/github_metrics_snapshot.py` (stdlib only) can summarize GitHub-sourced metrics locally.
- `ai-attribution.json` documents declared AI-assisted files for this bundle.
- [deploy-metrics.yml](../.github/workflows/deploy-metrics.yml) records successful `production` deployments after CI on `main` (for deployment frequency and lead time). Replace the environment URL with your real host when you have one.
- [deploy-python-example.yml.example](../.github/workflows/deploy-python-example.yml.example) shows optional hosting-provider steps.

These assets improve traceability and give a metrics collector workflow activity to observe. They do not create historical review events or deployments, and they do not produce credible metric values by themselves.

## Suggested usage

1. Link each feature or bug PR to an issue.
2. Make a focused change and open a PR with validation notes and an AI-assistance disclosure where applicable.
3. Request an actual human review; respond to feedback with normal code changes.
4. Merge through your usual review policy.
5. If you need deployment frequency or end-to-end lead time, configure and record real production deployments.
6. Report the measurement window, denominator, source system, and metric definition alongside every number.
