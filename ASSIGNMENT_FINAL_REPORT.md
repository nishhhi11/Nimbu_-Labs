# Comprehensive Assignment Evidence & Working Report
**Course:** AI Tools and Prompt Engineering  
**Project:** Building and Auditing an AI-Agent Toolchain (Nimbus Campus Helpdesk Agent)  
**Student Name:** Nishi Chopda  
**Date:** November 7, 2026  
**Environment:** Google Antigravity / macOS (Darwin arm64)

---

## Part A – Claim Audit (15 Marks)

| No. | CTO Claim (Summary) | Verdict | Correction / Reasoning | Official Source URL | Access Date |
|:---|:---|:---|:---|:---|:---|
| **1** | MCP uses JSON-RPC 2.0 and has Tools, Resources, and Prompts. | **True** | The official Model Context Protocol (MCP) specification defines JSON-RPC 2.0 as the base protocol with three core primitives: Tools (actions), Resources (readable data), and Prompts (reusable templates). | `https://modelcontextprotocol.io/docs/concepts/architecture` | 2026-11-07 |
| **2** | MCP revision 2025-02-30 introduced a mandatory Persistent Memory Primitive. | **False** | February 30 is an invalid calendar date. Furthermore, MCP protocol specifications (e.g. 2024-11-05) have no mandatory "Persistent Memory Primitive"; state/memory is externalized to client applications. | `https://spec.modelcontextprotocol.io/specification/` | 2026-11-07 |
| **3** | Skills use a folder with `SKILL.md`, YAML metadata, and progressive loading. | **True** | Agent skills follow the standardized specification of a folder containing a root `SKILL.md` with YAML frontmatter (`name`, `description`), progressively disclosing `references/` and `scripts/`. | `https://docs.anthropic.com/` / Antigravity Skill Spec | 2026-11-07 |
| **4** | Every Skill requires `skill.config.yaml` and a Python runtime declaration. | **False** | Skills do not require `skill.config.yaml` or a mandatory runtime declaration. Metadata is encapsulated in the YAML frontmatter of `SKILL.md`, and skills can include any executable script, markdown documentation, or static data. | Agent Skills Specification Reference | 2026-11-07 |
| **5** | Linked Git worktrees have separate working directories and share repository objects. | **True** | As documented in the official `git-worktree(1)` manual, each linked worktree has its own private working tree and index (`.git/worktrees/<name>/`), but shares the main object database, refs, and commit graph. | `https://git-scm.com/docs/git-worktree` | 2026-11-07 |
| **6** | `git worktree sync --all` pulls and rebases all worktrees. | **False** | `git worktree sync` is not a valid Git command. Git provides `add`, `list`, `lock`, `move`, `prune`, `remove`, and `unlock`. Pulling and rebasing must be performed inside each individual branch. | `https://git-scm.com/docs/git-worktree` | 2026-11-07 |
| **7** | Plugins can bundle commands, subagents, Skills, hooks, and MCP configurations. | **True** | Antigravity and modern agent plugin architectures allow packaging skills, slash commands (`commands/`), hooks (`hooks.json`), rules, and MCP configurations (`mcp_config.json`) into a single installable unit. | Antigravity Plugin Guide / Customization Engine | 2026-11-07 |
| **8** | RFC 9999 requires Ed25519 signatures for every stdio MCP server. | **False** | RFC 9999 is a fictional / non-existent RFC number in the IETF registry. The standard MCP stdio transport operates over local standard input/output pipes without protocol-mandated cryptographic signatures. | `https://www.rfc-editor.org/` | 2026-11-07 |
| **9** | Git permits the same branch in two worktrees by default. | **False** | Git strictly prohibits checking out the same branch in multiple worktrees simultaneously to avoid conflicting reflog and branch pointer states (`fatal: '<branch>' is already checked out`). | `https://git-scm.com/docs/git-worktree` | 2026-11-07 |
| **10** | A 2024 study established skill collapse at 12 Skills and a 40% accuracy drop. | **Unverified** | No peer-reviewed academic paper or benchmark exists establishing a deterministic "skill collapse at 12 skills with 40% drop". Prompt routing degradation depends heavily on context window and description discriminability. | Academic literature / arXiv search | 2026-11-07 |

---

## Part B – Agent Skill (`timetable-helper`) (20 Marks)

### B1. Folder Structure
```text
campus-helpdesk/skills/timetable-helper/
├── SKILL.md
├── references/
│   ├── lookup-guide.md
│   └── mock_timetable.csv
└── scripts/
    └── timetable_lookup.py
```

### B2. Progressive Disclosure Details
- **`SKILL.md`**: Core prompt with clear purpose, operational rules, anti-hallucination constraints, and reference routing.
- **`references/mock_timetable.csv`**: Fictional dataset covering batches `CS-A` and `CS-B`, Monday to Friday, subjects, rooms, and faculty.
- **`references/lookup-guide.md`**: Column dictionary, validation constraints, edge-case protocols (weekends, free slots).
- **`scripts/timetable_lookup.py`**: CLI lookup engine with case-insensitive filtering, sorting, and structured reporting.

### B3. Test Plan Execution Matrix (6 Prompts)
| Test | Type | Prompt | Expected Behaviour | Actual Result | Triggered? |
|:---|:---|:---|:---|:---|:---|
| **1** | Positive | *"Show me the complete Monday timetable for batch CS-A, including subject names, timings, rooms and faculty."* | Skill triggers; reads CSV; lists classes chronologically. | 5 classes returned (09:00 to 16:00) with full room and faculty details. | **Yes** |
| **2** | Positive | *"For batch CS-A, tell me all the days and timings when Operating Systems is scheduled. Include the room and faculty name."* | Skill triggers; finds all OS slots across the week. | 4 lecture slots (Mon, Wed, Thu, Fri in Room 105) + 1 Lab identified. | **Yes** |
| **3** | Positive + Adversarial | *"Can you confirm my Quantum Computing class for batch CS-A on Friday at 3:00 PM in Room 402 with Dr. Hawking?"* | Skill triggers; detects missing class; refuses invention. | Strictly refused invention: stated no matching record exists in mock data. | **Yes** |
| **4** | Negative | *"What is the capital of France and what is its population?"* | Skill does not trigger; answered with general knowledge. | Answered about Paris directly without accessing timetable tools/files. | **No** |
| **5** | Negative | *"Write a 200-word formal excuse letter to a professor for medical leave."* | Skill does not trigger; drafts leave letter. | Drafted student letter; avoided false-positive skill execution. | **No** |
| **6** | Ambiguous | *"What classes do I have tomorrow?"* | Skill recognizes schedule intent; detects missing batch and day; asks clarification. | Prompted user for batch (`CS-A`/`CS-B`) and day of the week rather than guessing. | **Yes** |

### B4. Description Optimisation
- **Original (Too Broad):** *"Campus assistant for all student questions, classes, schedules, and college information."* → Caused false-positive triggers on general questions and fees.
- **Alternative 1 (Too Narrow):** *"Only use when a user asks for 'CS-A' or 'CS-B' Monday to Friday schedule strictly from mock_timetable.csv."* → Failed to trigger on natural conversational phrasing.
- **Selected (Balanced):** *"Answers student questions about class schedules, lecture timings, subjects, rooms, and daily timetables using the supplied mock timetable data. Use when a student asks about their timetable, today's classes, the next lecture, or a particular subject's schedule."* → Accurate trigger boundary without false activations.

---

## Part C – Packaged Plugin (`campus-helpdesk`) (20 Marks)

### C1. Package Architecture
```text
campus-helpdesk/plugin/campus-helpdesk/
├── plugin.json               # Plugin manifest
├── mcp_config.json           # MCP Server registration
├── hooks.json                # PreToolUse security hook mapping
├── commands/
│   └── timetable.md          # Custom /timetable slash command
├── hooks/
│   └── security_hook.py      # Security hook enforcement script
└── skills/
    └── timetable-helper/     # Bundled timetable skill
```

### C2. Threat Model & Mitigations
1. **Prompt Injection through Skill Data:** Untrusted timetable records or user queries containing instruction overrides are treated strictly as read-only data strings; system prompt rules prevent override.
2. **Malicious Hooks:** Security hooks are subject to least-privilege execution, validated path parameters, and explicit whitelist checks.
3. **MCP Tool Poisoning:** Strict JSON schema typing, deterministic Python parameter parsing, and explicit error handlers prevent arbitrary code execution.

---

## Part D – Local MCP Server (20 Marks)

### D1. Capabilities Implemented
- **Tool 1 (`get_timetable`):** Inputs `batch`, `day`. Returns matching timetable rows chronologically.
- **Tool 2 (`get_fee_status`):** Inputs `student_id`. Returns fictional student fee balance; refuses to fabricate nonexistent IDs.
- **Resource (`campus://hostel/rules`):** Serves `hostel-rules.md` (gate timings, curfews, visitor policies).

### D2. Investigation of `@nimbus/mcp-skill-bridge` (v2.3)
- **NPM Registry Lookup:** `npm view @nimbus/mcp-skill-bridge` returned `404 Not Found`.
- **PyPI Registry Lookup:** `curl -s https://pypi.org/pypi/nimbus-mcp-skill-bridge/json` returned `Not Found`.
- **Verdict:** **REJECT (Unverified / Hallucinated Package)**. The package does not exist in public registries. Implemented standard MCP stdio server directly using Python.

### D3. Protocol Negotiation & Test Verification
- `initialize`: Negotiated protocol version `2024-11-05`, tools capability, and resources capability.
- `tools/list`: Returned registered tools and complete JSON schemas.
- `tools/call`: Successfully retrieved timetable arrays and student fee balance.
- `resources/read`: Successfully retrieved complete Markdown text for `campus://hostel/rules`.

### D4. Safe Failure Handling
- **Invalid Day (`Funday`):** Returned `"Validation Error: Invalid day 'Funday'. Valid days are Monday through Friday."` with `"isError": true`.
- **Unknown Batch (`CS-Z`):** Returned `"No timetable records found for batch 'CS-Z' on Monday."` without errors.
- **Unknown Student (`9999UNKNOWN`):** Returned `"Student record not found for ID '9999UNKNOWN'. Fictional fee information cannot be fabricated."` with `"isError": true`.

---

## Part E – Parallel Development with Git Worktrees (15 Marks)

### E1. Worktree Creation
```bash
git worktree add -b feature/skill-tests ../wt-skill-tests main
git worktree add -b feature/mcp-server ../wt-mcp-server main
git worktree add -b bugfix/hook-path ../wt-hook-path main
git worktree list
```
**Active Worktree Output:**
```text
/Users/nishi/AI_Assignment  0115f69 [main]
/Users/nishi/wt-hook-path   0115f69 [bugfix/hook-path]
/Users/nishi/wt-mcp-server  0115f69 [feature/mcp-server]
/Users/nishi/wt-skill-tests 0115f69 [feature/skill-tests]
```

### E2. Genuine Merge Conflict Creation & Resolution
- Edited `README.md` on `feature/skill-tests` (`# Feature branch updates for testing`).
- Edited `README.md` on `bugfix/hook-path` (`# Bugfix branch updates for hook validation`).
- Executed `git merge bugfix/hook-path` inside `wt-skill-tests`, triggering `CONFLICT (add/add)`.
- Verified raw conflict markers:
  ```text
  <<<<<<< HEAD
  # Feature branch updates for testing
  =======
  # Bugfix branch updates for hook validation
  >>>>>>> bugfix/hook-path
  ```
- Manually resolved `README.md` and committed merge `0802486`.

### E3. Git Worktree Technical Concepts
1. **Prevention of Same Branch Checkout:** Git prohibits checking out the same branch across multiple worktrees to maintain reflog integrity and avoid race conditions where two indexes mutate the same HEAD pointer.
2. **Shared vs. Private State:**
   - *Shared:* Object database (`.git/objects/`), branch and tag refs (`.git/refs/`), commit history graph, and configuration.
   - *Private:* Working directory files, staging index (`.git/worktrees/<name>/index`), HEAD reference (`.git/worktrees/<name>/HEAD`), and checkout-specific operational state (e.g. `MERGE_HEAD`, cherry-pick state).
3. **Safe Cleanup:**
   - `git worktree remove <path>`: Deletes the working directory and cleans administrative references.
   - `git worktree prune`: Cleans stale metadata records from `.git/worktrees/` if a worktree directory was manually deleted.

### E4. CTO Claim Audit – Claude Code `/worktree-merge`
- **Verdict:** **False**
- **Reasoning:** Claude Code does not possess a native `/worktree-merge` command that automatically resolves arbitrary merge conflicts without developer oversight. Git merge conflicts inherently require contextual human/agent reasoning.
- **Reference:** Official Claude Code CLI Documentation (`https://docs.anthropic.com/`).

