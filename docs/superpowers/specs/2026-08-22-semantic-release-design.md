# Semantic Release Workflow — Design

## Purpose

Automate repo versioning: every push to `main` that contains releasable
commits (`feat`, `fix`, etc., per Conventional Commits) triggers a new
semantic version, a git tag, and a GitHub Release with auto-generated
release notes. No manual version bumping.

## Scope

One version number for the entire repo (not per-skill). The repo already
uses Conventional Commit messages (`feat:`, `fix:` prefixes visible in
`git log`), so no change to commit conventions is required.

Out of scope: attaching built `.skill` files as release assets, maintaining
a `CHANGELOG.md` file, per-skill versioning. These can be added later as a
follow-up if needed.

## Tooling

[`semantic-release`](https://semantic-release.gitbook.io/) (the JS/Node
tool). It's a CI-time-only dependency — the repo's actual content (Python
skill scripts) is unaffected by it running in Node. Chosen over
`python-semantic-release` for its more mature GitHub Actions integration
and plugin ecosystem.

Three plugins, in order:

1. `@semantic-release/commit-analyzer` — inspects commits since the last
   release to determine the version bump (`fix` → patch, `feat` → minor,
   `BREAKING CHANGE:` footer → major).
2. `@semantic-release/release-notes-generator` — builds release notes from
   the same commits.
3. `@semantic-release/github` — creates the git tag and GitHub Release
   using the generated notes. This is the only publish target — no npm
   registry publish, no committed changelog file.

## Files added

### `package.json` (new)

Minimal, `"private": true`, no publishable package. Lists `semantic-release`
and the three plugins above as `devDependencies`, pinned to their current
major versions. Exists solely so `npm ci` can install the release tooling
in CI.

### `.releaserc.json` (new)

```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/github"
  ]
}
```

### `.github/workflows/release.yml` (new)

- **Trigger:** `push` to `main`.
- **Permissions:** `contents: write` (create tags/releases), `issues: write`
  and `pull-requests: write` (lets the github plugin comment on issues/PRs
  referenced by released commits — harmless if the repo doesn't use this).
- **Steps:**
  1. `actions/checkout@v4` with `fetch-depth: 0` (semantic-release needs
     full commit history to analyze all commits since the last tag).
  2. `actions/setup-node@v4` with Node LTS.
  3. `npm ci`.
  4. `npx semantic-release`, using the default `GITHUB_TOKEN` — no
     additional secrets required.
- **Concurrency:** a concurrency group keyed on the workflow name so
  overlapping runs on rapid successive pushes to `main` don't race each
  other creating conflicting releases.

## Versioning behavior

No git tags exist in the repo yet. The first workflow run on `main` after
this change merges will cut `v1.0.0` (semantic-release's default initial
version). Subsequent pushes to `main` containing releasable commits bump
the version automatically; pushes with only non-releasable commits (e.g.
`chore:`, `docs:`) produce no release.

## Testing / verification

- `npm ci` succeeds locally (validates `package.json`/lockfile).
- Push a `fix:` or `feat:` commit to `main` (or a manually triggered test)
  and confirm the workflow creates the expected tag (`v1.0.0` on first run)
  and GitHub Release with populated notes.
- Confirm a `chore:`-only push does **not** create a release.
