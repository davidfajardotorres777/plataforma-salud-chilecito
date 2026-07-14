Deployment and publishing guide

This document explains how to publish the platform artifacts and the demo.

1) GitHub Actions / GHCR (Docker registry)
- The repo includes a workflow .github/workflows/docker-ghcr.yml that builds and pushes a Docker image to GHCR (ghcr.io/${{ github.repository_owner }}/plataforma-salud-chilecito:SHA).
- Requirements: add a Dockerfile at the repository root. The workflow uses GITHUB_TOKEN to authenticate with GHCR.

2) GitHub Pages (static demo)
- The static demo lives under src/webapp/static and is published to the gh-pages branch by .github/workflows/deploy_pages.yml.
- To enable a custom domain, configure Pages under repository settings > Pages and set the CNAME accordingly.

3) Heroku
- The repo contains a workflow .github/workflows/deploy_heroku.yml that uses the HEROKU_* secrets.
- Required secrets (in repository Settings > Secrets): HEROKU_API_KEY, HEROKU_APP_NAME, HEROKU_EMAIL

4) Vercel / Other hosts
- You can point Vercel to this repository for automatic deployments of the frontend. Add a vercel.json if you need custom builds.

5) Branch protection and required checks
- Recommended: protect main branch and require the CI check named "CI" to pass before merging.
- This repository has an automated step that will try to enable branch protection; if you need stricter policies, configure them in Settings > Branches.

6) Local testing
- Create a virtualenv: python -m venv .venv
- Install deps: . .venv/bin/activate && pip install -r requirements.txt
- Start MongoDB & Redis via docker compose: docker compose up -d
- Run tests: pytest -q

If you want, I can create the Dockerfile, configure a specific Heroku Procfile, or add a vercel.json for you. Add the required secrets afterwards so the workflows can deploy automatically.
