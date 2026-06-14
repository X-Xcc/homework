# 法律学习 AI 工作台 — 核心对象字段设计 v1

> 版本：v1  
> 日期：2026-06-09  
> 作用：定义产品层核心对象的数据字段结构，供 PRD、原型、前后端建模共同使用

---

## 1. 文档目标

本文件用于回答四个问题：

1. 产品里的核心对象到底有哪些字段？
2. 哪些字段是展示字段，哪些字段是关系字段，哪些字段是状态字段？
3. 对象之间如何互相引用？
4. 后续如果进入数据库建模，哪些字段可以直接落表，哪些字段仍属于产品层概念？

本版覆盖 5 类核心对象：

1. `Material`
2. `Case`
3. `Knowledge`
4. `Analysis`
5. `Collection`

说明：

- `Workspace` 更偏聚合视图与页面层容器，v1 暂不作为独立持久化主对象设计
- 后续如果要支持团队空间、课程空间、项目空间，再单独抽出 `Workspace` 实体

---

## 2. 字段设计总原则

### 2.1 先服务产品对象，再服务数据库表

本文件首先是产品对象设计，不是 SQL 建表文件。

所以优先关注：

- 用户能看到什么
- 页面要展示什么
- 对象怎么连接
- 工作流如何流转

而不是先纠结数据库范式。

### 2.2 每类对象至少分 6 组字段

每类对象统一从以下 6 组字段思考：

1. **基础标识字段**
2. **展示内容字段**
3. **关系连接字段**
4. **状态流程字段**
5. **统计派生字段**
6. **系统审计字段**

### 2.3 先保证可展示、可追溯、可跳转

v1 字段设计优先保证三件事：

- 页面能展示
- 来源能追溯
- 对象能跳转

### 2.4 不把 AI 输出直接当最终真相

凡是 AI 生成内容，尽量单独标出：

- 是否 AI 生成
- 是否人工编辑
- 当前版本是什么

这样后续才方便区分“生成建议”和“用户沉淀结果”。

---

## 3. 通用字段约定

以下字段建议作为 5 类核心对象的通用约定。

### 3.1 通用基础字段

- `id`：对象唯一标识
- `object_type`：对象类型
- `title`：对象标题
- `summary`：对象摘要

### 3.2 通用归属字段

- `owner_id`：所属用户
- `source_type`：来源类型
- `source_id`：来源对象 ID（如从某材料提取）

### 3.3 通用状态字段

- `status`：当前状态
- `visibility`：可见性
- `is_archived`：是否归档
- `is_deleted`：逻辑删除标记

### 3.4 通用时间字段

- `created_at`
- `updated_at`
- `last_viewed_at`

### 3.5 通用 AI 字段

- `ai_generated`：是否由 AI 初始生成
- `ai_confidence`：AI 置信度（如适用）
- `human_verified`：是否已人工确认

---

## 4. `Material` 字段设计

## 4.1 对象定义

`Material` 表示一份原始输入材料，是分析的起点对象。

适用范围：

- 判决书
- 合同
- 法条文本
- 课堂讲义
- 学术论文
- 用户笔记
- 外部导入文本

---

## 4.2 字段分组

### A. 基础标识字段

- `id`
- `object_type` = `material`
- `owner_id`
- `title`
- `material_type`
- `source_type`

### B. 内容展示字段

- `summary`
- `original_text`
- `excerpt_text`
- `language`
- `keywords`
- `topic_tags`

### C. 文件与来源字段

- `file_name`
- `file_format`
- `file_size`
- `import_method`（上传 / 粘贴 / 导入 / 系统生成）
- `source_url`（如适用）
- `source_reference`

### D. 关系连接字段

- `case_ids`
- `knowledge_ids`
- `analysis_ids`
- `collection_ids`
- `citation_count`

### E. 结构化解析字段

- `outline`
- `detected_entities`
- `detected_legal_articles`
- `detected_issue_candidates`
- `detected_concept_candidates`

### F. 状态流程字段

- `status`（未处理 / 已阅读 / 已标注 / 已分析 / 已沉淀）
- `processing_status`（待解析 / 解析中 / 已完成 / 失败）
- `annotation_count`
- `question_count`
- `highlight_count`

### G. 审计字段

- `created_at`
- `updated_at`
- `last_viewed_at`
- `archived_at`

---

## 4.3 `Material` 最小 MVP 字段

建议 MVP 至少包括：

- `id`
- `owner_id`
- `title`
- `material_type`
- `summary`
- `original_text`
- `case_ids`
- `knowledge_ids`
- `analysis_ids`
- `status`
- `processing_status`
- `created_at`
- `updated_at`

---

## 5. `Case` 字段设计

## 5.1 对象定义

`Case` 表示一个有明确目标的任务容器。

不一定是司法案件，也可能是：

- 作业题
- 课程主题
- 研究问题
- 合规分析专题

---

## 5.2 字段分组

### A. 基础标识字段

- `id`
- `object_type` = `case`
- `owner_id`
- `title`
- `case_type`

### B. 展示内容字段

- `summary`
- `description`
- `subject_area`
- `topic_tags`
- `learning_goal`

### C. 任务结构字段

- `main_question`
- `issue_tree`
- `target_output_type`
- `argument_direction`

### D. 关系连接字段

- `material_ids`
- `knowledge_ids`
- `analysis_ids`
- `collection_ids`
- `related_case_ids`

### E. 流程状态字段

- `status`（进行中 / 已完成 / 待复习 / 已归档）
- `stage`（收集材料 / 拆争点 / 做分析 / 沉淀成果）
- `completion_ratio`
- `last_active_module`

### F. 统计派生字段

- `material_count`
- `analysis_count`
- `knowledge_count`
- `collection_count`
- `issue_count`

### G. 协作与 AI 字段

- `ai_generated_outline`
- `ai_suggested_issues`
- `human_verified`
- `last_ai_summary`

### H. 审计字段

- `created_at`
- `updated_at`
- `last_viewed_at`
- `completed_at`
- `archived_at`

---

## 5.3 `Case` 最小 MVP 字段

- `id`
- `owner_id`
- `title`
- `case_type`
- `summary`
- `main_question`
- `material_ids`
- `analysis_ids`
- `knowledge_ids`
- `status`
- `stage`
- `created_at`
- `updated_at`

---

## 6. `Knowledge` 字段设计

## 6.1 对象定义

`Knowledge` 表示可复用、可连接、可沉淀的知识节点。

可能是：

- 法条节点
- 概念节点
- 争点节点
- 要件节点
- 案例规则节点

---

## 6.2 字段分组

### A. 基础标识字段

- `id`
- `object_type` = `knowledge`
- `owner_id`
- `title`
- `knowledge_type`

### B. 展示内容字段

- `summary`
- `definition`
- `core_rule`
- `applicable_conditions`
- `exceptions`
- `topic_tags`

### C. 关系连接字段

- `material_ids`
- `case_ids`
- `analysis_ids`
- `collection_ids`
- `related_knowledge_ids`

### D. 来源追溯字段

- `source_material_excerpt_ids`
- `source_reference`
- `source_confidence`
- `derived_from_ai`

### E. 复习与学习字段

- `review_status`
- `review_count`
- `last_reviewed_at`
- `next_review_at`
- `difficulty_level`
- `mastery_level`

### F. 结构化连接字段

- `legal_article_refs`
- `issue_refs`
- `concept_refs`
- `case_rule_refs`

### G. 状态字段

- `status`（草稿 / 已确认 / 待复习 / 已归档）
- `human_verified`
- `editable`

### H. 审计字段

- `created_at`
- `updated_at`
- `last_viewed_at`

---

## 6.3 `Knowledge` 最小 MVP 字段

- `id`
- `owner_id`
- `title`
- `knowledge_type`
- `summary`
- `definition`
- `material_ids`
- `case_ids`
- `related_knowledge_ids`
- `review_status`
- `status`
- `created_at`
- `updated_at`

---

## 7. `Analysis` 字段设计

## 7.1 对象定义

`Analysis` 表示围绕某个问题形成中的分析产物。

它不是最终成果，而是中间的思考工作件。

常见类型：

- 事实梳理
- 争点树
- 要件匹配
- 法律关系分析
- 论证骨架
- 案例对比稿

---

## 7.2 字段分组

### A. 基础标识字段

- `id`
- `object_type` = `analysis`
- `owner_id`
- `title`
- `analysis_type`

### B. 展示内容字段

- `summary`
- `content`
- `structured_content`
- `current_conclusion`
- `open_questions`

### C. 作用域字段

- `case_id`
- `material_ids`
- `knowledge_ids`
- `focused_issue_id`

### D. 版本与编辑字段

- `version`
- `parent_analysis_id`
- `edit_count`
- `last_editor_type`（human / ai）
- `revision_notes`

### E. AI 协作字段

- `ai_generated`
- `ai_prompt_context`
- `ai_confidence`
- `human_verified`
- `suggested_next_steps`

### F. 状态字段

- `status`（草稿 / 分析中 / 已完成 / 已转成果）
- `completeness_score`
- `promoted_to_collection`

### G. 统计字段

- `citation_count`
- `referenced_material_count`
- `referenced_knowledge_count`

### H. 审计字段

- `created_at`
- `updated_at`
- `last_viewed_at`
- `completed_at`

---

## 7.3 `Analysis` 最小 MVP 字段

- `id`
- `owner_id`
- `title`
- `analysis_type`
- `case_id`
- `material_ids`
- `knowledge_ids`
- `content`
- `structured_content`
- `status`
- `ai_generated`
- `human_verified`
- `created_at`
- `updated_at`

---

## 8. `Collection` 字段设计

## 8.1 对象定义

`Collection` 表示用户决定保存、复用、输出的沉淀成果。

常见类型：

- 知识卡
- 案例卡
- 争点卡
- 答题模板
- 复习包
- 导出成果

---

## 8.2 字段分组

### A. 基础标识字段

- `id`
- `object_type` = `collection`
- `owner_id`
- `title`
- `collection_type`

### B. 展示内容字段

- `summary`
- `content`
- `display_format`
- `topic_tags`
- `use_case`

### C. 来源字段

- `source_material_ids`
- `source_case_ids`
- `source_analysis_ids`
- `source_knowledge_ids`
- `source_trace`

### D. 组织字段

- `folder_id`
- `bundle_id`
- `sort_order`
- `is_pinned`

### E. 学习与复用字段

- `review_status`
- `reuse_count`
- `export_count`
- `included_in_review_pack_ids`

### F. 导出字段

- `exportable_formats`
- `last_exported_at`
- `last_export_format`

### G. 状态字段

- `status`（草稿 / 已保存 / 已导出 / 已归档）
- `human_verified`
- `editable`

### H. 审计字段

- `created_at`
- `updated_at`
- `last_viewed_at`

---

## 8.3 `Collection` 最小 MVP 字段

- `id`
- `owner_id`
- `title`
- `collection_type`
- `summary`
- `content`
- `source_case_ids`
- `source_analysis_ids`
- `source_knowledge_ids`
- `status`
- `created_at`
- `updated_at`

---

## 9. 五类对象关系映射

以下是 v1 推荐的核心关系。

```text
Material
 ├─ belongs to many → Case
 ├─ derives many → Knowledge
 ├─ supports many → Analysis
 └─ contributes to many → Collection

Case
 ├─ contains many → Material
 ├─ contains many → Analysis
 ├─ references many → Knowledge
 └─ outputs many → Collection

Knowledge
 ├─ derives from many → Material
 ├─ referenced by many → Case
 ├─ used in many → Analysis
 └─ saved in many → Collection

Analysis
 ├─ scoped to one → Case
 ├─ references many → Material
 ├─ references many → Knowledge
 └─ promotes to many → Collection

Collection
 ├─ traces back to many → Material
 ├─ traces back to many → Case
 ├─ traces back to many → Analysis
 └─ traces back to many → Knowledge
```

---

## 10. 页面与字段的映射关系

### 10.1 工作台首页主要依赖

- `Case.title`
- `Case.stage`
- `Case.updated_at`
- `Material.title`
- `Analysis.title`
- `Collection.title`
- `Knowledge.title`

### 10.2 材料详情页主要依赖

- `Material.title`
- `Material.original_text`
- `Material.summary`
- `Material.case_ids`
- `Material.knowledge_ids`
- `Material.analysis_ids`
- `Material.processing_status`

### 10.3 案件分析工作区主要依赖

- `Case.title`
- `Case.issue_tree`
- `Case.material_ids`
- `Analysis.structured_content`
- `Analysis.knowledge_ids`
- `Collection.source_analysis_ids`

### 10.4 知识库主要依赖

- `Knowledge.title`
- `Knowledge.knowledge_type`
- `Knowledge.definition`
- `Knowledge.related_knowledge_ids`
- `Knowledge.review_status`

### 10.5 成果页主要依赖

- `Collection.title`
- `Collection.collection_type`
- `Collection.summary`
- `Collection.source_trace`
- `Collection.exportable_formats`

---

## 11. v1 设计结论

### 11.1 对象定位结论

- `Material` 是输入对象
- `Case` 是任务对象
- `Knowledge` 是长期认知对象
- `Analysis` 是过程对象
- `Collection` 是沉淀对象

### 11.2 建模结论

- `Workspace` 暂不独立建模
- `Analysis` 与 `Collection` 必须分开，不能混成一个对象
- `Knowledge` 必须有独立对象地位，不能只作为标签
- 所有对象都要保留来源追溯能力

### 11.3 MVP 结论

如果只做第一版，最优先保证：

- 基础标识字段
- 页面展示字段
- 关系连接字段
- 状态字段
- 时间字段

统计字段、复习字段、复杂 AI 字段可以后补。

---

## 12. 下一步建议

建议按以下顺序继续：

1. **页面组件清单 v1**：把工作台、材料页、案件页拆成组件级
2. 已输出 `PRD v1`（见 `PRD_V1.md`）
3. **数据库草模 v1**：把当前对象字段下沉为表结构草案
4. **API 草案 v1**：定义对象读写与关联接口

如果你希望继续保持产品定义顺序，我建议下一步做：

> **页面组件清单 v1**

因为现在对象、页面、IA 都已经齐了，PRD 也已成稿，接下来最适合进入执行拆分层。