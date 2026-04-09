# 文档命名与组织规则

## 目录结构

```
docs/
├── auth/                       # 认证模块
│   ├── login.md
│   └── register.md
├── user/                       # 用户模块
│   ├── profile.md
│   └── settings.md
├── order/                      # 订单模块
│   ├── create-order.md
│   ├── order-list.md
│   └── order-detail.md
├── dashboard/                  # 仪表盘模块
│   └── overview.md
└── progress/                   # 进度记录
    ├── 2025-01-15/
    │   ├── zhangsan_a3f2c1.md
    │   └── lisi_b7e4d9.md
    ├── 2025-01-16/
    │   └── zhangsan_c8a1f0.md
    └── archive/                # 归档（>30天自动迁移）
        └── 2024-12/
            └── 2024-12-10/
                └── zhangsan_d1e2f3.md
```

## 命名规范

| 层级 | 规则 | 示例 |
|------|------|------|
| 一级目录 | 业务模块名，kebab-case | `auth`、`user`、`order-management` |
| 二级文件 | 页面/功能点名，kebab-case，`.md` 扩展名 | `login.md`、`create-order.md` |
| 进度日期目录 | `YYYY-MM-DD` 格式 | `2025-01-15` |
| 进度文件 | `{username}_{6位十六进制hash}` | `zhangsan_a3f2c1.md` |
| 归档月度目录 | `YYYY-MM` 格式 | `2024-12` |

## 详细规则

1. **模块目录**：名称简短，2-4 个词，使用 kebab-case（如 `user-management`，不用 `userManagement`）
2. **功能文件**：名称对应具体页面或功能点，使用 kebab-case
3. **中文名允许**：如果项目统一使用中文，模块和文件名可用中文（如 `认证/登录.md`）
4. **不使用序号前缀**：模块化结构不需要 `01-`、`02-` 编号

## 多人协作约定

- 开发前明确模块归属，每人负责不同模块目录
- 一个功能点 = 一个 `.md` 文件，避免多人编辑同一文件
- 在独立 Git 分支上工作，通过 PR 合入主分支
