# Advance detection of the assessment family from the exam-invitation URL

The family of assessment can be detected in advance from the domain of the exam-invitation email or the assessment page's URL, so this is used at Step 0 when a URL is available. At Step 2 it is used to cross-check the provisional detection against the Step 1 investigation results.

## Detection table

| Domain string in the URL | Family this detects | Corresponding assessment |
|---|---|---|
| `arorua.net` | Recruit family | SPI (Test Center / Web Testing) |
| `e-exam` | Japan SHL family | One of 玉手箱 (Tamatebako), GAB, or CAB |
| `nsvs` | Japan SHL family | One of 玉手箱 (Tamatebako), GAB, or CAB |
| `tsvs` | Japan SHL family | One of 玉手箱 (Tamatebako), GAB, or CAB |
| `c-personal` | Humanage family | TG-WEB |

Multiple preparation outlets consistently mention this correspondence as a way to identify the assessment type from the URL or the assessment screen. The source for this detection table is the following preparation outlet (evidence level C).

- Source: Levtech Rookie, 「適性検査 20 種類の見分け方！URL・WEB 画面から判断する方法」 ("How to tell apart 20 types of aptitude test! Judging from the URL and web screen") https://rookie.levtech.jp/guide/detail/90170/ (Level C. Preparation outlet)

## How to use it

- Detection is done by matching the URL string only. It involves no external access to the URL and no external transmission of the profile.
- The detection result is provisional, and its confidence is set to `推定` (estimate). Confirmation happens through the Step 1 investigation by `job-change-exam-scout` (checking the careers page and candidate write-ups).

## Limitations

The following limitations apply to this detection. When conveying the provisional detection at Step 0, present these together with it.

- **Paper-format tests cannot be detected.** A test administered on paper, such as 内田クレペリン検査 (Uchida-Kraepelin), has no exam URL, so it cannot be detected from a URL (source: the Levtech Rookie article cited above, level C).
- **The Japan SHL family cannot be narrowed to a single test.** `e-exam`, `nsvs`, and `tsvs` are Japan SHL's assessment platforms, so from these alone the type can only be narrowed to one of 玉手箱 (Tamatebako), GAB, or CAB. The final type is confirmed through the Step 1 investigation.
- **An assessment vendor may change its domain.** The domain of an assessment vendor's platform can change over time. The detection table reflects the current correspondence at the time of writing; the URL may not match the table, or the actual assessment may differ even when it does match. Do not rely on URL-based detection alone; prioritize the Step 1 investigation results.
