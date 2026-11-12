# A3 NWS weather Hermes tap — publication candidate

Standalone weather component of the student's Assignment 3 `a3-weather-web` skill.
The public-city coordinate is central Los Angeles. No credentials or private configuration.

## Current status

Prepared locally; **not yet published**. Offline tests do not fulfill the advanced
integration requirement. No fresh Hermes installation or agent execution has yet
been recorded. The existing deployed skill/gateway is unchanged.

## Repository layout

Publish this directory's contents as the root of a new public repository:
`skills/a3-nws-weather/SKILL.md` and `skills/a3-nws-weather/scripts/forecast.py`.
Keep the project submission, profile, state, credentials, and other source outside it.

## Dependencies and local check

Python 3.10+ with HTTPS and CA certificates; no third-party packages or API keys.
From this repository root:

```text
python -m unittest discover -s tests -v
python skills/a3-nws-weather/scripts/forecast.py
```

On Linux use python3 if needed. Live failure exits 1 and reports unavailable.
Offline tests use synthetic data. A live script run alone does not demonstrate
Hermes loading and executing an installed skill.

## Publication and fresh-install verification

Official tap documentation consulted November 12, 2026:
https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#publishing-a-custom-skill-tap

On a separately installed fresh Hermes environment, first record its version,
installation source/commit and `hermes skills --help` / tap subcommand help.
Do not upgrade, copy, or reuse the running gateway's home or credentials.
Confirm the fresh version's CLI before running these documented command forms:

```text
hermes skills tap add OWNER/REPOSITORY
hermes skills tap list
hermes skills search a3-nws-weather
hermes skills install OWNER/REPOSITORY/a3-nws-weather
```

OWNER/REPOSITORY is a placeholder, not a ready command. The repository must be
public and used as a tap; do not install through a direct SKILL.md URL.
Do not bypass the normal security scan with --force.

After installation, inspect the installed files and compare their SHA-256 hashes
with the public publication commit. Record that commit with `git rev-parse HEAD`
in the public repository. Do not assume tap installation itself pins a commit.
Keep the public contents unchanged during verification, and preserve the resolved
installation reference/receipt if the installed Hermes version exposes one.

Open a fresh Hermes chat with terminal and skill tools available. Invoke:

```text
/a3-nws-weather Check Los Angeles weather. Show the NWS source, update time and check time.
```

Retain the skill-load/tool execution trace and final answer. A successful live run
requires verified status, current periods and source/update/check timestamps.
An unavailable result is honest failure evidence; it is not successful execution.
Model configuration is separate from this skill and should use only authorized
test settings in the isolated environment. Never publish model tokens or auth files.

## Evidence still required

- Public URL, exact publication commit (and optional tag).
- Fresh Hermes installation/version transcript and clean-home provenance.
- Tap registration, discovery, installation and installed-file verification.
- Actual Hermes skill execution, tool output and final response.
- README/REQUIREMENTS_CHECK.md/PROCESS_LOG.md updates in the main assignment,
  stating only the steps actually completed and attributing AI-assisted extraction.

## Provenance and boundaries

The supplied student source `assignment3/services.py` contains `public_json` and
`Weather.forecast`. Those functions were extracted without changing their weather
behavior. The smoke-check shape comes from `scripts/verify_weather.py`; the new
CLI adds a nonzero failure exit status and an import-safe main function.
ChatGPT/Codex prepared the extraction, skill instructions, packaging and tests;
the student must review the code and understand the behavior before submission.

NWS API reference: https://www.weather.gov/documentation/services-web-api
Hermes platform: https://github.com/NousResearch/hermes-agent
No external implementation code was copied. No claim is made that the fresh
Hermes workflow or the student's pinned Hermes CLI has already been tested.
