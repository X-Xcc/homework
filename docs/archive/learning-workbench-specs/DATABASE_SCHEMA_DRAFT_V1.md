# 法律学习 AI 工作台 — 数据库草模 v1

> 版本：v1  
> 日期：2026-06-09  
> 作用：把产品对象字段下沉为数据库层草案，供后端建模、API 设计与开发评审使用

---

## 1. 文档目标

本文件用于回答以下问题：

1. 5 类核心对象如何落成数据库主表？
2. 哪些多对多关系需要单独关系表？
3. 哪些字段适合直接存表，哪些先保持 JSON 结构？
4. MVP 第一版建议先建哪些表？

本版仍然只覆盖单用户 / 单空间 MVP，不处理团队协作模型。

---

## 2. 建模原则

### 2.1 先保证闭环，再追求范式完美

本版优先保证以下链路可落地：

```text
Material → Case → Analysis → Knowledge / Collection
```

### 2.2 主对象单独建主表

以下对象全部独立建主表：

- `materials`
- `cases`
- `knowledge_nodes`
- `analyses`
- `collections`

### 2.3 多对多关系尽量走关系表

凡是以下场景，优先用关系表：

- 一个对象可关联多个同类/异类对象
- 后续关系可能需要顺序、权重、角色、来源说明
- 页面上需要追踪“为什么关联”

### 2.4 第一版允许部分结构化字段走 JSON

以下内容 v1 可先用 JSON / JSONB：

- `issue_tree`
- `outline`
- `structured_content`
- `detected_entities`
- `suggested_next_steps`
- `source_trace`

### 2.5 派生统计字段可冗余

为了提升首页、列表页、详情页的读取效率，允许在主表上保留统计冗余字段，例如：

- `material_count`
- `analysis_count`
- `knowledge_count`
- `collection_count`

---

## 3. 表总览

建议第一版至少包含以下 10 张表。

### 3.1 主表

1. `materials`
2. `cases`
3. `knowledge_nodes`
4. `analyses`
5. `collections`

### 3.2 关系表

6. `case_materials`
7. `material_knowledge_links`
8. `analysis_materials`
9. `analysis_knowledge_links`
10. `collection_sources`

---

## 4. 主表设计

## 4.1 `materials`

### 表用途

保存用户导入或创建的原始材料。

### 建议字段

- `id` `uuid` 主键
- `owner_id` `uuid` 非空
- `title` `varchar(255)` 非空
- `material_type` `varchar(50)` 非空
- `summary` `text` 可空
- `original_text` `longtext/text` 非空
- `excerpt_text` `text` 可空
- `language` `varchar(20)` 可空
- `keywords` `json/jsonb` 可空
- `topic_tags` `json/jsonb` 可空
- `file_name` `varchar(255)` 可空
- `file_format` `varchar(50)` 可空
- `file_size` `bigint` 可空
- `import_method` `varchar(50)` 可空
- `source_url` `text` 可空
- `source_reference` `text` 可空
- `outline` `json/jsonb` 可空
- `detected_entities` `json/jsonb` 可空
- `detected_legal_articles` `json/jsonb` 可空
- `detected_issue_candidates` `json/jsonb` 可空
- `detected_concept_candidates` `json/jsonb` 可空
- `status` `varchar(30)` 非空
- `processing_status` `varchar(30)` 非空
- `annotation_count` `int` 默认 `0`
- `question_count` `int` 默认 `0`
- `highlight_count` `int` 默认 `0`
- `ai_generated` `boolean` 默认 `false`
- `ai_confidence` `decimal(5,2)` 可空
- `human_verified` `boolean` 默认 `false`
- `last_viewed_at` `datetime/timestamp` 可空
- `created_at` `datetime/timestamp` 非空
- `updated_at` `datetime/timestamp` 非空
- `archived_at` `datetime/timestamp` 可空
- `deleted_at` `datetime/timestamp` 可空

### 建议索引

- `(owner_id, updated_at desc)`
- `(owner_id, material_type)`
- `(owner_id, status)`

---

## 4.2 `cases`

### 表用途

保存用户围绕特定问题建立的案件 / 任务容器。

### 建议字段

- `id` `uuid` 主键
- `owner_id` `uuid` 非空
- `title` `varchar(255)` 非空
- `case_type` `varchar(50)` 非空
- `summary` `text` 可空
- `description` `text` 可空
- `subject_area` `varchar(100)` 可空
- `topic_tags` `json/jsonb` 可空
- `learning_goal` `text` 可空
- `main_question` `text` 可空
- `issue_tree` `json/jsonb` 可空
- `target_output_type` `varchar(50)` 可空
- `argument_direction` `text` 可空
- `status` `varchar(30)` 非空
- `stage` `varchar(30)` 非空
- `completion_ratio` `decimal(5,2)` 默认 `0`
- `last_active_module` `varchar(50)` 可空
- `material_count` `int` 默认 `0`
- `analysis_count` `int` 默认 `0`
- `knowledge_count` `int` 默认 `0`
- `collection_count` `int` 默认 `0`
- `issue_count` `int` 默认 `0`
- `ai_generated_outline` `json/jsonb` 可空
- `ai_suggested_issues` `json/jsonb` 可空
- `human_verified` `boolean` 默认 `false`
- `last_ai_summary` `text` 可空
- `last_viewed_at` `datetime/timestamp` 可空
- `created_at` `datetime/timestamp` 非空
- `updated_at` `datetime/timestamp` 非空
- `completed_at` `datetime/timestamp` 可空
- `archived_at` `datetime/timestamp` 可空
- `deleted_at` `datetime/timestamp` 可空

### 建议索引

- `(owner_id, updated_at desc)`
- `(owner_id, stage)`
- `(owner_id, status)`

---

## 4.3 `knowledge_nodes`

### 表用途

保存长期可复用的知识节点。

### 建议字段

- `id` `uuid` 主键
- `owner_id` `uuid` 非空
- `title` `varchar(255)` 非空
- `knowledge_type` `varchar(50)` 非空
- `summary` `text` 可空
- `definition` `text` 可空
- `core_rule` `text` 可空
- `applicable_conditions` `text` 可空
- `exceptions` `text` 可空
- `topic_tags` `json/jsonb` 可空
- `source_reference` `text` 可空
- `source_confidence` `decimal(5,2)` 可空
- `derived_from_ai` `boolean` 默认 `false`
- `review_status` `varchar(30)` 非空
- `review_count` `int` 默认 `0`
- `last_reviewed_at` `datetime/timestamp` 可空
- `next_review_at` `datetime/timestamp` 可空
- `difficulty_level` `varchar(20)` 可空
- `mastery_level` `varchar(20)` 可空
- `legal_article_refs` `json/jsonb` 可空
- `issue_refs` `json/jsonb` 可空
- `concept_refs` `json/jsonb` 可空
- `case_rule_refs` `json/jsonb` 可空
- `status` `varchar(30)` 非空
- `human_verified` `boolean` 默认 `false`
- `editable` `boolean` 默认 `true`
- `last_viewed_at` `datetime/timestamp` 可空
- `created_at` `datetime/timestamp` 非空
- `updated_at` `datetime/timestamp` 非空
- `deleted_at` `datetime/timestamp` 可空

### 建议索引

- `(owner_id, updated_at desc)`
- `(owner_id, knowledge_type)`
- `(owner_id, review_status)`
- `(owner_id, status)`

---

## 4.4 `analyses`

### 表用途

保存案件分析过程中的工作件。

### 建议字段

- `id` `uuid` 主键
- `owner_id` `uuid` 非空
- `case_id` `uuid` 非空
- `title` `varchar(255)` 非空
- `analysis_type` `varchar(50)` 非空
- `focused_issue_id` `varchar(64)` 可空
- `summary` `text` 可空
- `content` `longtext/text` 可空
- `structured_content` `json/jsonb` 可空
- `current_conclusion` `text` 可空
- `open_questions` `json/jsonb` 可空
- `version` `int` 默认 `1`
- `parent_analysis_id` `uuid` 可空
- `edit_count` `int` 默认 `0`
- `last_editor_type` `varchar(20)` 可空
- `revision_notes` `text` 可空
- `ai_generated` `boolean` 默认 `false`
- `ai_prompt_context` `json/jsonb` 可空
- `ai_confidence` `decimal(5,2)` 可空
- `human_verified` `boolean` 默认 `false`
- `suggested_next_steps` `json/jsonb` 可空
- `status` `varchar(30)` 非空
- `completeness_score` `decimal(5,2)` 默认 `0`
- `promoted_to_collection` `boolean` 默认 `false`
- `citation_count` `int` 默认 `0`
- `referenced_material_count` `int` 默认 `0`
- `referenced_knowledge_count` `int` 默认 `0`
- `last_viewed_at` `datetime/timestamp` 可空
- `created_at` `datetime/timestamp` 非空
- `updated_at` `datetime/timestamp` 非空
- `completed_at` `datetime/timestamp` 可空
- `deleted_at` `datetime/timestamp` 可空

### 建议索引

- `(owner_id, case_id, updated_at desc)`
- `(owner_id, analysis_type)`
- `(owner_id, status)`
- `(case_id, status)`

---

## 4.5 `collections`

### 表用途

保存用户确认沉淀的成果对象。

### 建议字段

- `id` `uuid` 主键
- `owner_id` `uuid` 非空
- `title` `varchar(255)` 非空
- `collection_type` `varchar(50)` 非空
- `summary` `text` 可空
- `content` `longtext/text` 可空
- `display_format` `varchar(50)` 可空
- `topic_tags` `json/jsonb` 可空
- `use_case` `text` 可空
- `source_trace` `json/jsonb` 可空
- `folder_id` `uuid` 可空
- `bundle_id` `uuid` 可空
- `sort_order` `int` 默认 `0`
- `is_pinned` `boolean` 默认 `false`
- `review_status` `varchar(30)` 可空
- `reuse_count` `int` 默认 `0`
- `export_count` `int` 默认 `0`
- `included_in_review_pack_ids` `json/jsonb` 可空
- `exportable_formats` `json/jsonb` 可空
- `last_exported_at` `datetime/timestamp` 可空
- `last_export_format` `varchar(20)` 可空
- `status` `varchar(30)` 非空
- `human_verified` `boolean` 默认 `false`
- `editable` `boolean` 默认 `true`
- `last_viewed_at` `datetime/timestamp` 可空
- `created_at` `datetime/timestamp` 非空
- `updated_at` `datetime/timestamp` 非空
- `deleted_at` `datetime/timestamp` 可空

### 建议索引

- `(owner_id, updated_at desc)`
- `(owner_id, collection_type)`
- `(owner_id, status)`
- `(owner_id, is_pinned)`

---

## 5. 关系表设计

## 5.1 `case_materials`

### 表用途

表示案件与材料的多对多关联。

### 建议字段

- `id` `uuid` 主键
- `case_id` `uuid` 非空
- `material_id` `uuid` 非空
- `relation_role` `varchar(30)` 可空
- `sort_order` `int` 默认 `0`
- `created_at` `datetime/timestamp` 非空

### 唯一约束

- `(case_id, material_id)`

### 索引

- `(case_id, sort_order)`
- `(material_id)`

---

## 5.2 `material_knowledge_links`

### 表用途

表示材料与知识节点之间的关联。

### 建议字段

- `id` `uuid` 主键
- `material_id` `uuid` 非空
- `knowledge_id` `uuid` 非空
- `link_type` `varchar(30)` 可空
- `source_excerpt` `text` 可空
- `confidence_score` `decimal(5,2)` 可空
- `created_by` `varchar(20)` 可空
- `created_at` `datetime/timestamp` 非空

### 唯一约束

- `(material_id, knowledge_id)`

---

## 5.3 `analysis_materials`

### 表用途

表示分析工作件所引用的材料。

### 建议字段

- `id` `uuid` 主键
- `analysis_id` `uuid` 非空
- `material_id` `uuid` 非空
- `usage_type` `varchar(30)` 可空
- `evidence_note` `text` 可空
- `created_at` `datetime/timestamp` 非空

### 唯一约束

- `(analysis_id, material_id)`

---

## 5.4 `analysis_knowledge_links`

### 表用途

表示分析工作件引用了哪些知识节点。

### 建议字段

- `id` `uuid` 主键
- `analysis_id` `uuid` 非空
- `knowledge_id` `uuid` 非空
- `usage_type` `varchar(30)` 可空
- `created_at` `datetime/timestamp` 非空

### 唯一约束

- `(analysis_id, knowledge_id)`

---

## 5.5 `collection_sources`

### 表用途

统一记录成果对象的来源对象。

### 设计原因

因为 `Collection` 可能来自：

- `Material`
- `Case`
- `Analysis`
- `Knowledge`

如果每种来源都建一张关系表，第一版会太碎。

### 建议字段

- `id` `uuid` 主键
- `collection_id` `uuid` 非空
- `source_type` `varchar(30)` 非空
- `source_id` `uuid` 非空
- `source_role` `varchar(30)` 可空
- `sort_order` `int` 默认 `0`
- `created_at` `datetime/timestamp` 非空

### 建议索引

- `(collection_id, source_type)`
- `(source_type, source_id)`

---

## 6. 关系映射建议

## 6.1 直接外键关系

建议直接外键：

- `analyses.case_id -> cases.id`
- `analyses.parent_analysis_id -> analyses.id`

## 6.2 通过关系表实现的多对多关系

- `cases ↔ materials` 通过 `case_materials`
- `materials ↔ knowledge_nodes` 通过 `material_knowledge_links`
- `analyses ↔ materials` 通过 `analysis_materials`
- `analyses ↔ knowledge_nodes` 通过 `analysis_knowledge_links`
- `collections ↔ all sources` 通过 `collection_sources`

## 6.3 第一版暂不显式建表的关系

以下关系第一版可以先不单独建关系表：

- `case ↔ knowledge`
- `case ↔ collection`
- `material ↔ collection`

原因是这些关系可通过 `analysis` 和 `collection_sources` 反推，先避免表过多。

---

## 7. 字段类型建议

### 7.1 状态类字段

建议先用 `varchar` + 应用层枚举约束。

理由：

- MVP 变动快
- 避免数据库枚举过早锁死

### 7.2 标签与引用列表

建议优先用 `json/jsonb`：

- `topic_tags`
- `keywords`
- `legal_article_refs`
- `issue_refs`
- `concept_refs`

### 7.3 长文本字段

以下字段建议使用 `text` 或等价长文本类型：

- `original_text`
- `content`
- `summary`
- `description`
- `definition`

---

## 8. MVP 最小建表建议

如果只做最小第一版，建议先建 8 张表。

### 8.1 必做主表

- `materials`
- `cases`
- `analyses`
- `knowledge_nodes`
- `collections`

### 8.2 必做关系表

- `case_materials`
- `analysis_materials`
- `collection_sources`

### 8.3 第二阶段补充关系表

- `material_knowledge_links`
- `analysis_knowledge_links`

如果首版节奏更紧，也可以先把知识节点与分析引用关系先存成 JSON，再在第二版正则化。

---

## 9. 查询场景校验

## 9.1 首页“继续案件”

需要查询：

- 最近更新的 `cases`
- 对应的 `material_count`
- 对应的 `analysis_count`

因此 `cases` 表保留统计冗余是合理的。

## 9.2 材料详情页

需要查询：

- 单条 `materials`
- 所属案件 `case_materials`
- 关联分析 `analysis_materials`
- 关联知识 `material_knowledge_links`

### 结论

材料页是典型的“单对象 + 多关系”页面，关系表方案适合。

## 9.3 案件分析页

需要查询：

- 当前 `cases`
- 当前案件下的 `analyses`
- 当前分析引用的 `materials`
- 当前分析引用的 `knowledge_nodes`

### 结论

`analyses` 必须以 `case_id` 为主归属外键。

---

## 10. 风险与后续优化点

### 10.1 第一版风险

- `collection_sources` 是通用来源表，灵活但需要应用层做好校验
- `issue_tree` 用 JSON 虽然快，但后续复杂查询不方便
- `topic_tags` 先用 JSON，后续如果检索需求强，可能需要拆标签体系

### 10.2 V2 可能新增表

- `annotations`
- `material_excerpts`
- `issues`
- `review_packs`
- `folders`
- `knowledge_links`

---

## 11. 本阶段结论

### 11.1 结构结论

- 5 个核心对象都可以独立落表
- 多对多关系已收敛为少量关系表
- 第一版数据库复杂度可控

### 11.2 MVP 结论

- 先做 5 主表 + 3 关系表即可支撑闭环
- 其余关系可在第二阶段继续正则化

### 11.3 执行结论

这个数据库草模已经足够支撑：

- 后端实体建模
- ORM schema 起草
- API 草案设计
- 前端数据依赖对照

---

## 12. 下一步建议

建议按以下顺序继续：

1. 已输出 `API 草案 v1`（见 `API_DRAFT_V1.md`）
2. 已输出 `前端页面树 v1`（见 `FRONTEND_PAGE_TREE_V1.md`）
3. **交互原型 v1**：把关键路径做成可演示原型
4. **SQL / ORM 初稿 v1**：把草模转成具体建表代码

如果继续顺推，我建议下一步做：

> **交互原型 v1**

因为现在对象、页面、组件、数据结构、接口、工程结构都已成型，最自然的下一步就是进入关键路径原型。