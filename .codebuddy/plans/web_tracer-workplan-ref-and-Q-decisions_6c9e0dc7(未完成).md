---
name: web_tracer-workplan-ref-and-Q-decisions
overview: 只修改 web_tracer/web_application_tracing_workplan.md：① 取消 ref/ 目录、基线改为直接引用仓库根的 ../code_tracer/；② 把 Q1–Q4 四项定案（Spring AOP+策略抽象 / 用户现有业务系统 / 本机 Linux / JDK 17+Maven）写入 §0、§1.1、§2、§4、§5.3、§7、§8、§11、§12，并新增"真实业务系统接入信息待补清单"作为 Phase 0 的输入前提。
todos:
  - id: baseline-paths
    content: 改写 §0/§1.1/§2/§4/§5.1/§6/T61 中的 11 处 ref/ 引用为 ../code_tracer，删除目录树中的 ref/ 行
    status: pending
  - id: q1-aop
    content: 写入 Q1 定案：spring_aop 为默认策略、保留 REGISTRY 抽象、登记三条已知局限与 span 命名约定，调整 §8.2 依赖必选标记
    status: pending
    dependencies:
      - baseline-paths
  - id: q2-target-app
    content: 写入 Q2 定案：target_app/ 改为外部真实业务系统接入登记，改写 T12 任务与 §8.3，提升 T17/T33 优先级说明
    status: pending
    dependencies:
      - baseline-paths
  - id: q3-q4-env
    content: 写入 Q3/Q4 定案：目标环境改本机 Linux，JDK 17 + Maven 明确为基准构建组合
    status: pending
    dependencies:
      - baseline-paths
  - id: section11-verify
    content: 改写 §11 为已定案分组并新增真实业务系统接入信息待补清单，同步 §12 门禁措辞
    status: pending
    dependencies:
      - q1-aop
      - q2-target-app
      - q3-q4-env
  - id: grep-audit
    content: grep 复查残留引用与跨源一致性，追加修订记录行
    status: pending
    dependencies:
      - section11-verify
---

## 用户需求
用户已把 `web_application_tracing_workplan.md` 迁到仓库根的 `web_tracer/`，现在要求把该文件按两项定案改到位：

1. **基线引用方式变更**：`web_tracer/ref/` 不再作为 `code_tracer` 的物理副本，改为**直接引用仓库根的 `../code_tracer/`**，不建 `ref/` 目录。
2. **Phase 0 四个阻塞问题定案写入**（用户已拍板）：
   - Q1 Java 方法级 span 路径 = **Spring AOP `@Around` 切面，同时保留 `method_instrumentation.py` 的 ABC + REGISTRY 策略抽象**（便于后续切换到 `@WithSpan` / Byte Buddy）。
   - Q2 靶场 = **用户现有的业务系统**（不是我方新建 demo）。
   - Q3 运行环境 = **本机 Linux（当前环境）**。
   - Q4 Java 版本与构建 = **JDK 17 + Maven**。

## 产品概述
本轮**只改文档，不写代码、不建目录、不装环境**。目标是让 `web_tracer/web_application_tracing_workplan.md` 与上述定案完全一致，消除所有失效的 `ref/` 引用，并把"用真实业务系统做靶场"这一决策带来的新增前置条件登记清楚。

## 核心特性（本轮交付内容）
- **基线路径全量改写**：文档中所有 `ref/...` 引用改为 `../code_tracer/...`（相对 `web_tracer/` 根），并声明基线为**只读引用、禁止修改**，`[复用]` 文件采取"复制单个文件到 `web_tracer/` 后演进"的方式，不复制整个 `code_tracer/` 目录树（`engine/` 下约 41740 个前端依赖文件，整份复制不可行）。
- **Q1–Q4 定案落笔**：§0 目标环境、§1.1 复用表、§2 架构图、§4 目录树、§5.3 接口代码注释、§7 任务表（T12/T13/T14/T15/T20）、§8 依赖清单、§11 待拍板表、§12 门禁，全部同步为定案结论。
- **Spring AOP 已知局限登记**：① 仅覆盖 Spring 容器管理的 bean；② 同类内部自调用 `this.xxx()` 不被拦截；③ final 类/方法无法被 CGLIB 代理。同时记录 span 命名必须 `FQCN#method`、attribute 必须带 `layer`（controller/service/repository）、切面只在既有 trace 下建子 span（父链路由 traceparent 保证）。
- **新增「真实业务系统接入信息待补清单」**：把 Q2 改为真实系统后，T12/T13 的前置输入显式列出（代码/仓库位置、启动命令与端口、登录鉴权方式、入口页面 URL 与点击步骤、前后端是否同源/CORS/网关、Spring Boot 与 Java 版本、数据库类型、是否允许加 `-javaagent` 与新增一个切面文件、敏感数据脱敏要求）。用户未提供这些信息前，Phase 0 仍标记为阻塞。
- **风险提示入册**：真实系统常见跨域/网关/鉴权会拦截 `traceparent`，导致关联降级 `confidence ≤ 0.8`，故 T17（CORS 预检探测）与 T33（后端放行 traceparent）优先级上升。

## 技术栈
- 本轮为**纯 Markdown 文档编辑**，无代码、无依赖安装、无构建。
- 目标文件：`/home/franklin/dsai/Engineering-and-Design/web_tracer/web_application_tracing_workplan.md`（806 行，WP-WEB-TRACER-001，状态 DRAFT）。
- 编辑方式：严格使用 `replace_in_file` 做定点替换，**禁止整文件重写**（AGENTS.md §5.17 e，整块回写是历史上丢失 issue 的根因）。

## 实现思路
按"语义分区 + 批量定点替换"执行，全文分五组修改，改完统一 grep 校验无残留 `ref/` 引用、无自相矛盾表述。所有替换锚点均已核实原文。

### 1. 基线路径改写（11 处，已核实行号）
| 行 | 原文要害 | 改为 |
|---|---|---|
| L10 | 目标环境 = Windows 主机 + WSL + Docker | **本机 Linux 为主**，WSL/Docker 降为后续环境 |
| L12 | 基线 = `web_tracer/ref/`（只读副本） | 基线 = 仓库根 `../code_tracer/`，**只读引用、禁止修改、不建 `ref/`** |
| L29 | `ref/ui/static_dashboard.html` | `../code_tracer/ui/static_dashboard.html`（64.4 KB）+ `../code_tracer/ui/code-tracer.css`，**逐文件复制**到 `web_tracer/ui/` 后演进 |
| L38 / L39 | `ref/engine/core/trace_engine.py`、`ref/ui/tracer_pro.html` | 改为 `../code_tracer/engine/core/trace_engine.py`、`../code_tracer/ui/tracer_pro.html`（已核实存在） |
| L321 | "从 `ref/` 复制后演进" | "从 `../code_tracer/` **逐文件**复制后演进；禁止整目录复制" |
| L326 | 目录树中的 `├── ref/` 一行 | **删除**该行 |
| L371 / L372 | `[复用 ref/ui]` | `[复用 ../code_tracer/ui]` |
| L405 | 移植 `ref/.../server.py::_resolve_base` | 移植 `../code_tracer/engine/backend/server.py::_resolve_base`（26.77 KB，已核实） |
| L541 | 已从 `ref/engine/backend/server.py`（:8000）继承 | 改为 `../code_tracer/engine/backend/server.py` |
| L644 | T61 产出 `ref/workplan/` 归档 | 改为 `web_tracer/workplan/` 归档 |

### 2. Q1 定案（Spring AOP + 保留抽象）
- L84 架构图：`+ 方法级策略(4选1, Q1 决定)` → `+ 方法级策略(默认 spring_aop, 可切换)`。
- L349、L466–L472：去掉"Q1 分叉点"措辞，改为"**Q1 已定案：默认 `spring_aop`；REGISTRY 保留四策略以支持后续切换**"，并在 `JavaMethodInstrumentation` 注释下补三条已知局限与 span 命名/attribute 约定。
- L597 T14、L603 T20：验收标准中"Q1 定案"改为"确认 `select_strategy('auto')` 在真实系统上返回 `spring_aop`，且 `nested_ok=True`"。
- §8.2（L680–L682）：`spring-boot-starter-aop` 标 **必选**；`opentelemetry-instrumentation-annotations` 与 `net.bytebuddy` 降为 **可选（备用策略）**。

### 3. Q2 定案（真实业务系统）
- L385 目录树：`target_app/` 条目由"P0 靶场 Spring Boot + H2 demo"改为 `docs/target_app_access.md` —— **外部真实业务系统接入登记（源码不入库）**。
- L595 T12：由"搭建 demo"改为"**接入用户现有业务系统 + 登记接入信息**"，验收标准由"`/api/document` 返回 200"改为"接入清单 9 项全部登记完成，且系统可在本机 Linux 启动并访问"。
- L690 §8.3：`靶场 Web 前端 | 内置 demo 或用户提供` → `用户提供（真实业务系统，见接入清单）`。
- 联动说明：真实系统多为跨域/带鉴权，T17（CORS 预检探测）、T33（后端放行 traceparent）在 Phase 0/3 的重要性上升，需在 §7 提示行补一句。

### 4. Q3 / Q4 定案
- L10 目标环境改本机 Linux；§8.2 的 JDK 行明确 `17`（JFR 需 21+ 仍属 P8）、Maven 明确为**主构建工具**（Gradle 降为可选）。
- §11 表格中 Q3、Q4 由"待拍板"改为"已定案"。

### 5. §11 表格改写 + 新增接入清单
- §11（L741–L756）：Q1–Q4 移入"**已定案（2026-09-30）**"分组并写明结论；Q5–Q11 保持"待拍板"。
- 新增小节 **§11.1 真实业务系统接入信息待补清单（阻塞 T12/T13）**，9 项逐条列出（代码/仓库位置、启动命令与端口、登录鉴权方式、入口 URL 与点击步骤、前后端是否同源/CORS/网关、Spring Boot 与 Java 版本、数据库类型、是否允许加 `-javaagent` 及新增切面文件、敏感数据脱敏要求）。
- §12 Phase 0 门禁首条由"Q1 有答"改为"Q1 已定案为 spring_aop 且策略验证通过"，其余两条（六类节点齐现、关联率 ≥80%）注明"**在真实业务系统上验证**"。

## 目录结构（本轮仅修改 1 个文件）
```
web_tracer/
└── web_application_tracing_workplan.md   # [MODIFY] 基线路径改写 + Q1–Q4 定案 + 接入清单新增
```
不新增/删除其他文件；不创建 `archive/ config/ data/ log/ docs/ workplan/` 骨架；不创建 `knowledge.json`（用户限定本轮只改 workplan，相关 AGENTS.md 合规提示保留在文档内）。

## 执行注意
- 全部替换用 `replace_in_file`，锚点取**完整原始行/段落**，避免误伤同名字段（如 `layer`、`ref`）。
- 改完后必须 grep 复查：① `ref/` 全文 0 命中（除明确指向"基线为 ../code_tracer"的说明性文字外）；② `webtracer` / `web_tracing/` 0 命中；③ Q1–Q4 在 §11 只出现一次且结论一致（AGENTS.md §5.13 跨源一致性审计）。
- 文档 §0 状态保持 `DRAFT — 待用户批准`，仅在修订记录处追加一行日期与改动摘要（AGENTS.md §5.7 修订元数据）。
