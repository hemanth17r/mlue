# Security Policy

MLUE is designed from first principles as an AI-first computational and spatial simulation substrate. Because AI models interact programmatically with MLUE in automated and semi-autonomous environments, security and containment are core design requirements.

---

## Supported Versions

| Version | Supported          | Security Maintenance |
| ------- | ------------------ | -------------------- |
| 1.6.x   | :white_check_mark: | Active (Current)     |
| 1.x     | :white_check_mark: | Security patches     |
| < 1.0   | :x:                | End of Life          |

---

## Architectural Threat Model & Sandboxing

MLUE enforces mathematical boundary constraints and system-level sandboxing by default:

1. **Strict Path Invariants**:
   All filesystem loaders (`loader.py`, `binary.py`, and `ai_interface.py`) canonicalize and resolve absolute file paths against authorized workspace trees. Path traversal tokens (`..`) attempting to escape project roots are rejected before any disk access.

2. **Zero Code Execution (`eval` / `exec` Prohibition)**:
   The MLUE core contains **zero** instances of `eval()`, `exec()`, or dynamic code compilation. All entity mutations, property changes, and condition evaluations operate through structured AST parsers and declarative dispatch tables.

3. **Memory-Isolated Sessions**:
   Dynamic in-memory AI simulation sessions are decoupled into immutable, state-checked dataclasses (`SimulationState`). One session cannot read, mutate, or leak memory into another session.

4. **Zero Third-Party Dependency Surface**:
   The core runtime (`runtime/`) relies exclusively on the Python Standard Library and an optional pure C native core (`runtime/native/`). This eliminates supply-chain vulnerabilities, malicious transitive packages, and arbitrary dependency updates.

---

## Reporting a Vulnerability

If you discover a security vulnerability or potential containment escape in MLUE, please do **NOT** open a public issue.

Instead, please report it privately:

- **Email**: `security@mlue.ai` (or directly to the core maintainer at `hemanth@example.com`)
- **Subject**: `[SECURITY] Potential vulnerability in MLUE <component>`

Please include:
1. Detailed description of the vulnerability.
2. Minimal reproducible proof-of-concept (`.mlue` scene file, script, or JSON payload).
3. Potential impact on host systems or AI agent loops.

### Response Timeline
- **Initial Acknowledgement**: Within 24 hours.
- **Triage & Impact Assessment**: Within 48 hours.
- **Remediation & Patch Release**: Within 7 business days for critical vulnerabilities.

We follow coordinated disclosure and will credit researchers in the release notes upon disclosure.
