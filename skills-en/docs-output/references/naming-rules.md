# Document Naming and Organization Rules

## Directory Structure

```
docs/
├── auth/                       # Authentication module
│   ├── login.md
│   └── register.md
├── user/                       # User module
│   ├── profile.md
│   └── settings.md
├── order/                      # Order module
│   ├── create-order.md
│   ├── order-list.md
│   └── order-detail.md
├── dashboard/                  # Dashboard module
│   └── overview.md
└── progress/                   # Progress records
    ├── 2025-01-15/
    │   ├── zhangsan_a3f2c1.md
    │   └── lisi_b7e4d9.md
    ├── 2025-01-16/
    │   └── zhangsan_c8a1f0.md
    └── archive/                # Archive (auto-migrate after >30 days)
        └── 2024-12/
            └── 2024-12-10/
                └── zhangsan_d1e2f3.md
```

## Naming Conventions

| Level | Rule | Example |
|-------|------|---------|
| Top-level directory | Business module name, kebab-case | `auth`, `user`, `order-management` |
| Second-level files | Page/feature name, kebab-case, `.md` extension | `login.md`, `create-order.md` |
| Progress date directory | `YYYY-MM-DD` format | `2025-01-15` |
| Progress files | `{username}_{6-char hex hash}` | `zhangsan_a3f2c1.md` |
| Archive monthly directory | `YYYY-MM` format | `2024-12` |

## Detailed Rules

1. **Module directories**: Names should be concise, 2-4 words, using kebab-case (e.g., `user-management`, not `userManagement`)
2. **Feature files**: Names correspond to specific pages or feature points, using kebab-case
3. **Localized names allowed**: If the project consistently uses a non-English language, module and file names may use that language (e.g., `auth/login.md`)
4. **No numeric prefixes**: Modular structure does not need `01-`, `02-` numbering

## Multi-Person Collaboration Guidelines

- Clarify module ownership before development — each person owns a different module directory
- One feature point = one `.md` file — avoid multiple people editing the same file
- Work on independent Git branches, merge into main via PR
