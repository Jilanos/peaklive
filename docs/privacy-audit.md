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
personal/professional email addresses and unredacted screenshots. The authorized
history rewrite removes historical local-reference files, superseded screenshots
and raw hardware-acceptance recordings, and anonymizes matching text and email
identities. Current application code and README screenshots are preserved.
Original data is retained only in a private backup outside the repository.
Rewriting changes commit IDs and may invalidate historical CI/build references.

Confidentiality decisions confirmed by the maintainer:

- The two raw hardware-acceptance ASC recordings and historical private DBCs
  and screenshots are removed from the published history. Capture locations in
  historical validation notes refer to private evidence, not distributable files.
- Current README screenshots, including visible motor signals, measured curves
  and values, are explicitly approved and remain unchanged.
- The GitHub account, CI links and other additionally reported identifiers are
  approved. Targeted personal/professional addresses remain anonymized.
- Ignored local reference databases/screenshots, generated builds, virtual
  environments and caches are not distributable sanitized source artifacts.
  Ignoring a file does not remove its previously committed versions.

This review covers locally available Git history. Remote-only refs, pull-request
refs, release assets, CI artifacts, caches, forks and other clones were not
enumerated or purged. Do not distribute a directory archive including ignored
files or the original Git database as an anonymized deliverable.
