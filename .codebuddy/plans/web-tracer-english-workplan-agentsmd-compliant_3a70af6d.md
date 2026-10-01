---
name: web-tracer-english-workplan-agentsmd-compliant
overview: 按 AGENTS.md §15 的强制结构，新建一份英文、面向新手用户的 Web Application Tracer 主 workplan（`web_tracer/workplan/`），完整继承原中文草案的技术内容（61 任务 / WT 契约 / R1-R12 / Q1-Q11 / 门禁）并写入 Q1-Q4 定案；旧中文草案归档保留；补 index 与日志条目。
todos:
  - id: inventory-draft
    content: 完整读取中文草案，登记 T01-T61、WT 契约、R1-R12、Q1-Q11、门禁清单
    status: completed
  - id: create-main-workplan
    content: 按 AGENTS.md §15 新建英文主 workplan，含术语词典、mermaid 图、合规章节与 Q1-Q4 定案
    status: completed
    dependencies:
      - inventory-draft
  - id: create-index-readme
    content: 新建 workplan/README.md 索引，对齐 code_tracer 索引风格
    status: completed
    dependencies:
      - create-main-workplan
  - id: archive-old-draft
    content: 按 §5.3 归档旧中文草案到 workplan/archive/ 并移除根目录副本
    status: completed
    dependencies:
      - create-main-workplan
  - id: create-logs
    content: 新建 log/update_log.md 与 log/issue_log.md，录入 U001 与 I001-I003
    status: completed
    dependencies:
      - create-main-workplan
  - id: consistency-audit
    content: grep 复查命名、ref/ 残留与跨源一致性，校验日志结构
    status: completed
    dependencies:
      - create-index-readme
      - archive-old-draft
      - create-logs
---


## 产品概述
在 `web_tracer/` 项目下，按仓库根 `AGENTS.md` 的强制规则，新建一份**英文版主 workplan**（供最终用户与开发者共同使用），把现有中文草案的全部技术资产迁移过来，并写入已拍板的技术决策。

## 核心特性
- **结构合规**：严格按 AGENTS.md §15「Workplan Rules」组织——Title/Description（含 Document ID、Revision Control、Version History、Status）、Object、Scope Summary（每项含 ID / details / category / status / related phase）、Index of Content、Dependencies、Evaluation and Alignment with Existing Architecture、Implementation Phases（每阶段含 Timeline / Milestones / Deliverables / 更新或新建清单 / Risks &amp; Mitigation / Potential Future Issues / Success Criteria / References）。
- **英文 + 新手友好**：全文英文；每个专业术语首次出现时附一句白话解释与类比（span、trace_id、AOP、OTLP、CORS 预检、correlation 等），使非专业用户能读懂。
- **资产完整继承**：保留中文草案的 T01–T61 任务表、WT-01..WT-52 契约、R1–R12 风险、§12 阶段门禁，不丢失任何技术结论。
- **四项定案写入**：Q1 = Spring AOP `@Around` 切面（保留 ABC + REGISTRY 四策略抽象）；Q2 = 用户现有业务系统（附 9 项接入信息待补清单，阻塞 Phase 0）；Q3 = 本机 Linux；Q4 = JDK 17 + Maven。
- **基线改为只读引用**：取消 `ref/` 目录，基线指向仓库根 `../code_tracer/`（禁止修改），`[复用]` 文件逐文件复制后演进，不复制整个目录树。
- **配套文档与日志**：新建 workplan 索引 `README.md`、归档旧中文草案、新建 `log/update_log.md` 与 `log/issue_log.md`（按 §5.17 固定结构），并做跨源一致性复查。



## 技术栈
- 本轮为**纯 Markdown 文档工程**：无代码、无依赖安装、无构建、不装 JDK/Maven/Playwright。
- 编辑方式：新建文件用写入；对既有文件（issue_log 等）一律用定点替换，**禁止整文件回写**（AGENTS.md §5.17 e）。
- 基准参考：`code_tracer/workplan/README.md`（索引风格范例）、`eks/knowledge.json`（仓库内唯一知识库实例）。

## 实现思路
先把中文草案（802 行）当作**唯一技术资产来源**完整读取并登记清单，再按 AGENTS.md §15 的段落在英文版中重建，最后补齐合规配套（索引、归档、日志）并做一致性 grep。核心取舍：

1. **新建而非原地改写**：旧草案是中文、且结构缺失 §15 的 Object / Scope Summary / Evaluation and Alignment / 每阶段 Risks-Mitigation-Success Criteria 等强制段，定点替换无法补齐结构，故新建英文主 workplan；旧文件按 §5.3 先归档再移除根目录副本，保留修订历史。
2. **内容语言与受众**：英文正文 + 术语白话注释，满足"user and developer 都能读懂"；技术编号（T/WT/R/Q）保持原样，避免与历史评审记录脱钩。
3. **合规差异必须显式登记**（旧草案与 AGENTS.md 冲突处）：
   - §18 UI：旧方案"复制 code-tracer.css 后演进"与"两个 UI 共用 `common/universal_ui_design.css/js` 基础层、项目 CSS 只做 override"冲突 → 英文版改为 common 基础层 + 项目 override 双层结构，并写明 ThemeManager（5 主题 + localStorage）。
   - §5.10：`web_tracer/knowledge.json` 缺失即不合规 → 本轮不创建，但作为 Phase 0 首个任务 + 登记 issue。
   - §2.4：`config/schemas/knowledge_base_schema.json` 实际不存在（grep 0 命中）→ 登记为 issue，不臆造 schema 内容。
   - §1 命名：canonical name = "Web Application Tracer"，abbrev = `web_tracer`，全文统一，禁止 `webtracer` / `web_tracing`。
4. **真实业务系统接入的前置输入**显式列为阻塞项，避免开发者在信息缺失时开工。

## 执行注意（防回归）
- 复用文件的路径必须核实后落笔，不得臆造：`code_tracer/ui/static_dashboard.html`(64.4KB)、`code_tracer/ui/code-tracer.css`(30.02KB)、`code_tracer/ui/tracer_pro.html`(20.83KB，反面教材)、`code_tracer/engine/core/trace_engine.py`(9.63KB，不复用)、`code_tracer/engine/backend/server.py`(26.77KB，`_resolve_base` 来源)、`code_tracer/engine/launch.py`(2.93KB)。
- `code_tracer/engine/` 下约 41740 个前端依赖文件 → 整份复制不可行，这是"不建 ref/"的技术依据，需写入正文。
- 阶段范围冻结（§15）与 feature completion 定义（stub/占位不得标 ✅）必须单列一节。
- 收尾必须 grep：全文 0 处 `ref/`（除说明性文字）、0 处 `webtracer` / `web_tracing/`、Q1–Q4 结论在各节一致（§5.13 跨源一致性）。

## 架构设计（新 workplan 的章节骨架）
```
1  Title and Description          + Document ID / Revision / Status / Version History
2  Object                         目标与成功判据（一句话 + 白话版）
3  Scope Summary                  ID / details / category / status / related phase
4  Index of Content               全文档锚点链接
5  Glossary for Beginners         术语白话词典（span / trace_id / AOP / OTLP / CORS...）
6  Dependencies                   与 code_tracer、Q 决策、环境的前置依赖
7  Evaluation and Alignment       与现有架构复用/废弃/新增评估（基线引用 ../code_tracer）
8  Architecture and Data Flow     含 mermaid 图 + 三个契约 schema 说明
8.1 Directory Structure           完整目录树（test/ 非 tests/，含必备 10 目录）
9  Repository Compliance          逐条映射 AGENTS.md（命名/文件夹/测试真源/knowledge.json/日志/UI/错误码/Bootstrap/输出生命周期/问题生命周期）
10 Implementation Phases P0–P8 + Closeout
   每段固定八要素：Timeline / Milestones / Deliverables / Updated-or-Created /
                  Risks & Mitigation / Potential Future Issues / Success Criteria / References
11 Task Table                     T01–T61（沿用原编号，标注 Phase / 依赖 / 产出 / 验收）
12 Decisions                      Q1–Q4 已定案 + Q5–Q11 待拍板 + 真实系统接入清单 9 项
13 Risks                          R1–R12
14 Phase Gates                    各阶段门禁（P0 关联率 ≥80% 等）
15 Testing Strategy               §21 覆盖要求
16 Logs and Reporting             日志与阶段报告落位
17 Revision History               修订表
```

## 目录结构
```
web_tracer/
├── workplan/
│   ├── web_application_tracing_workplan.md   # [NEW] 英文主 workplan（按 §15 全量结构）
│   ├── README.md                             # [NEW] 索引：Master Workplan 表 + Phase Reports 占位 + Archive 段
│   └── archive/
│       └── web_application_tracing_workplan.zh-CN.r0.md   # [MOVE] 旧中文草案，§5.3 先归档
├── log/
│   ├── update_log.md                         # [NEW] U001 本轮变更
│   └── issue_log.md                          # [NEW] §5.17 固定结构 + I001–I003
└── web_application_tracing_workplan.md       # [REMOVE] 迁移归档后从根目录移除
```
本轮不创建 `archive/ config/ data/ output/ test/ ui/ engine/ docs/ knowledge.json`——均作为新 workplan 内 Phase 0 的合规任务列出，按 §5.1 待批准后再执行。

