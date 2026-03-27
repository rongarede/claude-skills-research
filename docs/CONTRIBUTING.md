# Contributing

## Skill Structure

Each skill lives in its own directory under `skills/`:

```
skills/
└── my-skill/
    ├── SKILL.md          # Required: skill definition (triggers, workflow)
    ├── scripts/          # Optional: executable scripts
    │   └── main.sh
    └── references/       # Optional: reference materials
```

## SKILL.md Format

```yaml
---
name: my-skill
description: |
  One-line description of what this skill does.
  Trigger words: /my-skill, my skill trigger, related keywords
---

## Workflow

1. Step one
2. Step two
```

## Guidelines

- One skill per directory
- SKILL.md is required — it defines the skill's triggers and behavior
- Scripts must have a shebang line and be executable (`chmod +x`)
- Scripts should use `set -e` for fail-fast behavior
- No hardcoded user-specific paths — use environment variables or `~`
- Test your skill before submitting a PR

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b add-my-skill`)
3. Add or modify skills
4. Test installation: `bash install.sh`
5. Submit a pull request
