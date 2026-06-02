# claude-financial-skills

Source repo for Claude Code financial skills. Each skill lives under `skills/` and is packaged into a `.skill` file (zip archive) for distribution.

## Structure

```
skills/<name>/
  SKILL.md          ← skill instructions and frontmatter
  references/       ← skill-specific reference docs
  scripts/          ← Python scripts the skill executes

shared/             ← reference docs copied into every skill at build time
dist/               ← built .skill files (gitignored)
```

## Build

```bash
# build all skills
make

# build one skill
make pack SKILL=portfolio-stress-test

# list available skills
make list

# clean dist/
make clean
```

## Skills

| Skill | Description |
|-------|-------------|
| `epoch-converter` | Convert Unix epoch timestamps (seconds or ms) to dates, US Eastern time, market session status, and trading-day context |
| `portfolio-stress-test` | Historical + hypothetical crash scenarios, Monte Carlo retirement simulation |
| `equity-analysis` | Fundamental equity research with institutional-grade formatting |
| `investment-scorecard` | Structured scoring framework for investment decisions |
| `market-regime` | Identify current market regime and adjust positioning |

## Claude Desktop (MCP)

Some skills also ship an MCP server so the same functionality is available in Claude Desktop conversations. Register the server in `~/Library/Application Support/Claude/claude_desktop_config.json` and restart Desktop.

| Skill | MCP server | Transport |
|-------|-----------|-----------|
| `epoch-converter` | `scripts/epoch_mcp_server.py` | `uvx --from fastmcp-slim[server] fastmcp run <path>` |

## Adding a skill

1. Create `skills/<your-skill>/SKILL.md` with the required frontmatter (`name`, `description`).
2. Add `references/` or `scripts/` subdirectories as needed.
3. Run `make pack SKILL=<your-skill>` to verify it builds.
4. Add a row to the Skills table above.

Shared reference docs in `shared/` are automatically copied into every skill's `references/` directory at build time — useful for portfolio schema, benchmark tables, etc. that multiple skills need.
