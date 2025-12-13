## GitLab demo storyline

- Project: `https://gitlab.dockerbuch.info/dockerbuch/webpage`
- Theme: harden the Hugo CI pipeline so the Docker + LLM compose walkthrough feels production-ready.

### Issues & labels

| IID | Title | Labels | State | Notes |
| --- | ----- | ------ | ----- | ----- |
| #1 | CI Hardening: add Lighthouse performance gate | `ci`, `performance`, `priority::high` | open | Branch `feature/lighthouse-gate`, pipeline [#15](https://gitlab.dockerbuch.info/dockerbuch/webpage/-/pipelines/15) |
| #2 | Calm linkchecker noise from release notes | `ci`, `content` | open | Branch `chore/linkchecker-release-notes`, pipeline [#16](https://gitlab.dockerbuch.info/dockerbuch/webpage/-/pipelines/16) |
| #3 | Stabilize test cleanup to avoid orphaned Docker networks | `ci`, `release` | open | Backlog item for later |
| #4 | Refresh hero section for Docker + LLM story | `content`, `release` | open | Branch `content/hero-compose-llm`, pipeline [#18](https://gitlab.dockerbuch.info/dockerbuch/webpage/-/pipelines/18) |
| #5 | Document local Model Runner setup in README | `content` | closed | Addressed via branch `docs/model-runner-readme`, pipeline [#17](https://gitlab.dockerbuch.info/dockerbuch/webpage/-/pipelines/17) |

### Branch snapshots

- `feature/lighthouse-gate`: adds Lighthouse stage + Python score gate to `.gitlab-ci.yml`.
- `chore/linkchecker-release-notes`: introduces ignore list, structured release-note data, and a Hugo page backed by `data/release_notes.yaml`.
- `content/hero-compose-llm`: provides a new `_index.md` hero with CTA plus the `compose-llm-demo.svg`.
- `docs/model-runner-readme`: new README covering the Docker Model Runner-enabled workflow.
- Docker stack update: `docker compose` now includes `gitlab-proxy` so the FastAPI chatbot can hit this API via `GITLAB_PROXY_URL`.

### Sample LLM prompts

- “What CI issues are still open for the Lighthouse rollout?”
- “Summarize the latest pipeline run for `chore/linkchecker-release-notes`.”
- “List the release resources that are ignored by the link checker.”
- “What documentation work was finished recently?”

Use the GitLab proxy service to query issues, merge activity, and pipeline metadata so the assistant can answer these questions conversationally.

