# Spec: 技能系统

## 能力描述

技能（Skill）是预置的提示词模板，帮助用户用标准化方式触发特定类型的金融研究分析。

## 数据模型

```
Skill
  id: str                    # 唯一标识，kebab-case，如 company-deepdive
  name: str                  # 显示名称，如"公司深度画像"
  description: str           # 一句话描述
  category: str              # 分类：公司分析/行业分析/宏观策略/债券/基金/数据/写作
  icon: str                  # emoji 图标
  prompt_template: str       # 含 {input} 占位符的提示词模板
  sample_input: str | None   # 示例输入，用于前端展示
  output_kind: text|card|table  # 期望输出类型（当前均为 card）
```

## 预置技能列表

共 15 个预置技能，按分类：

| 分类 | 技能 ID | 名称 |
|------|---------|------|
| 公司分析 | company-deepdive | 公司深度画像 |
| 公司分析 | earnings-recap | 财报速读 |
| 行业分析 | industry-snapshot | 行业景气快照 |
| 行业分析 | industry-compare | 行业比较 |
| 宏观策略 | macro-brief | 宏观一页纸 |
| 宏观策略 | rate-outlook | 利率债策略 |
| 债券 | credit-analysis | 信用债分析 |
| 债券 | bond-market-daily | 债市日报 |
| 债券 | convertible-screen | 可转债筛选 |
| 基金 | fund-holding-xray | 基金持仓透视 |
| 基金 | portfolio-attribution | 组合归因 |
| 数据 | catalyst-tracker | 催化剂日历 |
| 数据 | event-monitor | 事件监控 |
| 写作 | research-summary | 研报摘要 |
| 写作 | thesis-debate | 多空辩论 |

## 静态配置原则

技能是代码即配置，不持久化到数据库：
- 定义在 `data/skills_seed.py`
- 服务启动时由 `_Store.__init__` 一次性加载到内存
- 变更需修改 `skills_seed.py` 并重启服务
- 运行时只读，不支持增删改

## 场景推荐

`llm._suggest_skills` 根据检测到的场景返回 2-3 个推荐技能 ID，在 `ChatResponse.suggested_skills` 中返回给前端。

## API 接口

```
GET /api/skills?q=<keyword>&category=<分类>
→ list[Skill]

GET /api/skills/{id}
→ Skill
```

## 前端集成

- `SkillsPage`：技能广场，分类浏览，点击跳转到 SearchPage 并预填技能
- `SearchPage`：接收 `initialSkill`（来自路由 state），显示技能标签，发送时附带 `skill_id`

## 集成点

- `backend/app/data/skills_seed.py` — 技能定义
- `backend/app/services/store.py` — 内存加载与查询
- `backend/app/routers/skills.py` — HTTP 接口
- `backend/app/services/llm.py` — 技能模板替换与场景推荐
- `frontend/src/pages/SkillsPage.tsx` — 技能广场
- `frontend/src/pages/SearchPage.tsx` — 技能调用入口
