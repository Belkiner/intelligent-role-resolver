# Intelligent Role Resolver

Evidence-based eligibility assessment for on-chain roles.

## Overview

Intelligent Role Resolver explores evaluating role criteria against public evidence using GenLayer Intelligent Contracts.

## Problem

Role eligibility sometimes depends on demonstrated work or criteria that are difficult to reduce to one on-chain boolean.

## Example use case

A community evaluates whether an applicant meets published criteria for a role, with the result serving as an input to a separate permissions system.

## Inputs and outputs

- **Inputs:** Applicant or candidate reference, role criteria, and evidence.
- **Expected output:** A structured eligibility assessment.

## How it works

1. A caller submits the case details and evidence references.
2. The contract obtains or receives the available evidence using its configured GenLayer flow.
3. The Intelligent Contract evaluates the evidence against the stated criteria.
4. A structured result is recorded for downstream application logic.

The exact call signatures and accepted result schema are defined by `contract.py`. Review that file before integrating a frontend.

## What makes this project distinct

This assesses eligibility for a defined role. It does not itself grant powerful permissions or replace an access-control enforcement layer.

## Repository structure

```text
.
├── contract.py
├── README.md
├── LICENSE
└── .gitignore
```

## Validation status

- Python syntax check: run locally before use.
- GenLayer lint: **not confirmed in this package build**.
- GenLayer Studio/Testnet consensus: **not confirmed**.
- Security review: **not performed**.

This is a prototype, not production-ready software. Before deployment, run the current GenLayer linter and direct/integration tests, test invalid URLs and malformed model outputs, and inspect all state transitions.

## Limitations and safety

- Public web content can be incomplete, unavailable, stale, or malicious.
- AI assessment is not a cryptographic proof that external claims are true.
- A stored URL alone does not preserve an immutable historical snapshot.
- Do not use the result as the sole control for high-value payments, legal determinations, or privileged permissions without additional safeguards.
- Do not claim a successful Testnet deployment unless you have verified it.

## Suggested next steps

1. Install the current GenLayer toolchain following the official documentation.
2. Run the GenLayer linter against `contract.py`.
3. Add direct tests for normal, edge, and malformed inputs.
4. Run integration tests in GenLayer Studio/Testnet.
5. Document the actual test results and deployed address, if any.

## License

MIT. See `LICENSE`.
