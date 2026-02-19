# Documentation Restructure Design

**Date:** 2026-02-19
**Scope:** README.md restructure + CLAUDE.md update
**Goal:** Document all 19 tool modules (169 tools) — currently only 5 of 19 are in README, 14 of 19 in CLAUDE.md

## Problem

The README documents 29 of 169 tools (17%). The 5 modules added in Phase 1 (sessions, event_hooks, devices, threat_insight, behaviors) are not documented anywhere user-facing. CLAUDE.md is also missing these 5 new modules.

## Approach: README Restructure (Approach B)

Reorganize the README so the tool catalog is the centerpiece, grouped by category, with compact tables.

### New README Structure

```
1. Header + badges + intro                    [KEEP AS-IS]
2. Key Features                               [UPDATE tool count]
3. Getting Started (install, config, auth)    [KEEP AS-IS]
4. Supported Tools                            [RESTRUCTURE]
   4a. Overview table: Module | Tools | Description (19 rows)
   4b. Per-module tables grouped by category:
       IDENTITY MANAGEMENT
       - Users (17 tools)
       - Groups (10 tools)
       - Schemas (8 tools)
       APPLICATION MANAGEMENT
       - Applications (16 tools)
       - Trusted Origins (8 tools)
       SECURITY & ACCESS CONTROL
       - Policies (14 tools)
       - Roles (10 tools)
       - Authorization Servers (14 tools)
       - Authenticators (8 tools)
       - Factors (6 tools)
       SECURITY MONITORING
       - System Logs (1 tool)
       - Behavior Detection Rules (8 tools)
       - ThreatInsight (2 tools)
       - Sessions (5 tools)
       INFRASTRUCTURE & INTEGRATIONS
       - Network Zones (8 tools)
       - Event Hooks (9 tools)
       - Identity Providers (8 tools)
       - Devices (5 tools)
       - Brands (12 tools)
5. Authentication                             [KEEP AS-IS]
6. Troubleshooting                            [KEEP, merge duplicate Debug section]
7. Development                                [KEEP AS-IS]
8. Security                                   [KEEP AS-IS]
9. Contributing + License + Okta footer       [KEEP AS-IS]
```

### Table Format

Each module gets a compact table — no verbose usage examples:

```markdown
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_users` | List all users | `q`, `limit`, `after`, `fetch_all` |
| `get_user` | Get user by ID | `user_id` |
```

### Changes to Existing Content

- **Remove** the verbose Usage Examples column from Users, Groups, Applications, Policies, Logs tables
- **Add** Key Parameters column instead (compact)
- **Merge** the standalone "Debug Logs" section into Troubleshooting (it's duplicated)
- **Update** Key Features bullet to say "169 tools across 19 domains"

## CLAUDE.md Changes

Add 5 new modules to the tool table in the Architecture section:

| Module | Path | Purpose |
|--------|------|---------|
| behaviors | `tools/behaviors/behaviors.py` | Behavior detection rule management |
| devices | `tools/devices/devices.py` | Device management |
| event_hooks | `tools/event_hooks/event_hooks.py` | Event hook management |
| sessions | `tools/sessions/sessions.py` | Session management |
| threat_insight | `tools/threat_insight/threat_insight.py` | ThreatInsight configuration |

No other CLAUDE.md changes needed.

## Implementation Tasks

1. Update CLAUDE.md tool table (add 5 modules)
2. Restructure README "Supported Tools" section with overview table + category groupings
3. Write compact per-module tables for all 19 modules (read each module's source to get accurate tool names, descriptions, parameters)
4. Merge duplicate Debug Logs section into Troubleshooting
5. Update Key Features bullet
6. Commit
