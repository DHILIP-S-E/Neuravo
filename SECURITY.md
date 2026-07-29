# Security Policy

## Supported Versions

Neuravo is currently pre-1.0 (`0.x` line) and under active early development.
There is no formal LTS policy yet — only the **latest released version**
receives security fixes. If you're on an older `0.x` release, please upgrade
to the latest before reporting an issue, as it may already be fixed.

| Version        | Supported          |
| -------------- | ------------------ |
| Latest release | :white_check_mark: |
| Older releases | :x:                |

This policy will be revisited once the project reaches a 1.0 release and a
stable support window can be committed to.

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security reports.** Public
issues are visible to everyone immediately, including before a fix is
available.

Instead, report vulnerabilities privately via a
[GitHub Security Advisory](https://github.com/DHILIP-S-E/Neuravo/security/advisories/new).
This creates a private discussion with the maintainer where details, a fix,
and a coordinated disclosure timeline can be worked out before anything is
made public.

Please include as much detail as you can:

- A description of the vulnerability and its potential impact
- Steps to reproduce, or a minimal proof-of-concept
- The affected version(s) and, if known, the affected module (e.g. a
  specific provider under `providers/`)

There's no dedicated security response SLA at this stage of the project, but
reports will be acknowledged and worked on as promptly as possible.

## Handling Credentials

Neuravo is an SDK that talks to AI providers (currently AWS Bedrock and
OpenAI) and, as such, handles credentials like AWS access keys and OpenAI API
keys on your behalf. A few things to keep in mind as a user of the library:

- **Never hardcode API keys, AWS credentials, or other secrets** in source
  code, notebooks, or committed config files. Use environment variables, a
  `.env` file that's excluded from version control, or your cloud provider's
  standard credential chain (e.g. IAM roles, `~/.aws/credentials`) instead.
- The SDK includes some of its own safeguards against accidental exposure,
  but these are aids, not a substitute for good credential hygiene:
  - `observability/logging.py` redacts known sensitive-data patterns (API
    keys, tokens, passwords, AWS credentials) from log output before it's
    written anywhere.
  - `security/policy.py`'s `SecurityPolicy` can block prompts matching
    configured patterns (e.g. SSN- or credit-card-like strings) and supports
    redacting sensitive text out of request/response content.
- If you believe a credential may have leaked through a bug in this SDK
  (rather than through your own usage), please report it as a vulnerability
  using the process above rather than filing a public issue.
