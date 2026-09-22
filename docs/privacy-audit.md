# Repository privacy review

Date: 2026-09-22

Personal owner addresses and identifying recording examples have been replaced
with neutral values. Workflow statuses and progress are unchanged; the generated
index also reflects previously completed work that its earlier version omitted.
Validation: 76 targeted recording, profile, naming and settings tests passed;
Logics lint passed; workflow audit has no blocking issues and 51 warnings.

The review inspected all 307 commits reachable from locally available refs,
plus reflog history, filenames, text objects and Git identities. Current and
historical screenshots were inspected using OCR, which is not a guarantee that
every visible identifier was recognized. Common private-key and access-token
signatures were not found; this is not an exhaustive secret-detection result.

Historical versions contain private reference databases, identifying filenames,
personal/professional email addresses and unredacted screenshots. A separate
filtered mirror is prepared for review: it removes historical local-reference
files and superseded screenshots, anonymizes matching text and commit identities,
and preserves the current application code and redacted screenshots. Original
history remains sensitive until the filtered history is adopted and published.
Rewriting changes commit IDs and may invalidate historical CI/build references.

Additional material requiring a confidentiality decision:

- Two tracked hardware-acceptance ASC recordings contain actual CAN identifiers,
  payloads and timestamps. Removing names does not anonymize those measurements.
- Current screenshots retain measured curves and some decoded motor signal names
  and values, despite masking database names, identifiers and payloads.
- GitHub account and CI links identify the repository owner.
- Ignored local reference databases/screenshots, generated builds, virtual
  environments and caches are not distributable sanitized source artifacts.
  Ignoring a file does not remove its previously committed versions.

This review covers locally available Git history. Remote-only refs, pull-request
refs, release assets, CI artifacts, caches, forks and other clones were not
enumerated or purged. Do not distribute a directory archive including ignored
files or the original Git database as an anonymized deliverable.
