# PUBLIC REPOSITORY AUDIT

Scan for secrets, credentials, personal data and proprietary material, performed before any public
release is considered. **No secret value is reproduced in this report**; findings are described in
redacted form.

**Date:** 2026-10-12 · **Scope:** all files tracked by git · **Tracked file count:** 576

---

## 1. Result

| category | finding |
|---|---|
| API keys, tokens, bearer credentials | **none found** |
| passwords, password files | **none found** |
| private keys, SSH material, certificates | **none found** |
| cloud credentials (AWS/GCP/Azure) | **none found** |
| `.env` files, cookies, session identifiers | **none found** |
| browser profiles | **none found** |
| absolute local paths, local usernames | **none found in tracked files** |
| proprietary employer data | **none found** |
| personal financial data | **none found** |
| private career or interview material | **none found** |
| unrelated personal documents | **none found** |
| **personal email address** | **present in 54 tracked files** — see §3 |

**No credential of any kind was found.** One privacy item requires a decision before publication.

## 2. Method

Patterns searched across every tracked file, with `papers/` scanned separately:

- credential shapes: `api[_-]?key`, `apikey`, `secret[_-]?key`, `access[_-]?token`, `bearer `,
  `password`, `passwd`, `BEGIN (RSA|OPENSSH|PRIVATE)`, `aws_access`, `AKIA[0-9A-Z]{16}`,
  `xox[baprs]-`, `ghp_[A-Za-z0-9]{20,}`, `sk-[A-Za-z0-9]{20,}`;
- credential-bearing filenames: `.env`, `*.pem`, `*.key`, `id_rsa`, `*.pfx`, `*.p12`, and any path
  containing `credential`, `secret`, `token` or `cookie`;
- local paths: `C:\Users\`, `C:/Users/`, `/home/<user>/`, `AppData`;
- personal identifiers: any email address, excluding the Anthropic co-authorship line and
  `example.com`;
- employer and private-material terms: the author's employer and university names, `confidential`,
  `proprietary`, `currículo`, `curriculum vitae`, `salary`, `salário`. The names themselves are not
  reproduced here: `scripts/release_public_audit.py` holds the patterns and fails the release on any
  match outside its own source.

The project's `.gitignore` already excludes `.env`, `*.key` and `*.pem` as a precaution; the scan
confirms none exists in history-tracked content either.

## 3. The one finding: personal email in `User-Agent` headers

**Description.** A personal Gmail address appears as the contact in the HTTP `User-Agent` of
data-collection scripts, in **54 tracked files** (scripts plus two governance documents). It appears
in **zero** files under `papers/`: neither the manuscript, nor the release package, nor any figure,
table or evidence file contains it.

**This is correct engineering, not a mistake.** The SEC EDGAR fair-access policy asks automated
clients to identify themselves with a contact address, and the scripts comply.

**It is nonetheless a publication decision.** Making the repository public publishes that address,
where it will be scraped. The redacted shape of the line is:

```
H = {"User-Agent": "QIE research <personal-email-address>", "Accept-Encoding": "gzip, deflate"}
```

**Recommended action, not taken here.** Read the contact from an environment variable with a
documented fallback:

```python
CONTACT = os.environ.get("QIE_CONTACT_EMAIL", "set QIE_CONTACT_EMAIL before running")
H = {"User-Agent": f"QIE research {CONTACT}", "Accept-Encoding": "gzip, deflate"}
```

and note in the README that anyone re-running the collection scripts must set their own address,
because the policy requires a real contact rather than a placeholder. This is mechanical, affects no
result, and is left to the user: publishing a contact address may be intended.

Tracked as blocker **B4** in `RELEASE_BLOCKERS.md`.

## 4. False positives, examined and dismissed

| match | verdict |
|---|---|
| `scripts/deploy_collector.sh` — the word "password" | a comment explaining that passwordless `sudo` is needed for `systemctl`; **no credential** |
| `tests/test_config.py` — the word "api_key" | a unit test asserting that a config containing an unexpected key is **rejected**; the literal value is `"nope"` |
| `ITAU UNIBANCO HOLDING` in `H14_1_OPA_GOLD_SET.csv` and related datasets | a **publicly listed Brazilian issuer** appearing in a takeover-offer dataset built from public regulatory filings. This is public market data about a company, **not** employer information, and contains nothing internal to any institution |
| Portuguese prose matching `ricar` inside the email string | the same §3 finding, not a separate one |

**There is no internal, confidential or proprietary employer material in this repository.**

## 5. What is deliberately absent from version control

`.gitignore` excludes `data/` in full, plus `__pycache__/`, `.venv/`, caches, and three large
downloaded source corpora. One consequence is a reproducibility gap rather than a privacy one: nine
small derived artefacts cited by the evidence matrix are not tracked. That is blocker **B1**, with
its file list, sizes and hashes.

No raw downloaded document corpus is tracked. `DATA_RELEASE_POLICY.md` explains the licensing reason
this is also the right choice for redistribution.

## 6. Unresolved blockers from this audit

| id | item | owner |
|---|---|---|
| **B4** | personal email in 54 tracked files | user |
| **B1** | nine cited artefacts untracked (reproducibility, not privacy) | user |

No other issue found. **The repository contains no secret that would be exposed by publication.**
