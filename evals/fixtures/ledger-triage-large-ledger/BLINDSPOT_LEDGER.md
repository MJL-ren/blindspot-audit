---
status: active
lifecycle_class: ledger
canonical_owner: evals/fixtures/ledger-triage-large-ledger/BLINDSPOT_LEDGER.md
review_trigger: "ledger triage regression fixture"
---

# Blindspot Audit Ledger

## Project Context (verified 2026-07-01)

- Intent: public commercial SaaS prototype
- Target users and regions: small studios, US/KR
- Stage and deadline: pre-launch beta
- Owner strong areas: backend automation, Python
- Owner weak or new areas: UX/UI, payments, legal, public launch operations
- Web-search privacy rule: category-only
- Standing decisions: avoid adding new product scope during this fixture

## Audit Log

| Date | Host | Mode | Scope | Notes |
| --- | --- | --- | --- | --- |
| 2026-07-01 | no-choice host | deep | fixture project | external-change scan skipped; peer expectation scan ran; context intake persisted |
| 2026-07-03 | choice-capable host | focus/ux-ui | fixture project | ux-ui pack run; several decisions deferred |

## Findings

| ID | Finding | Priority | Awareness | Status | Next check / owner |
| --- | --- | --- | --- | --- | --- |
| BS-20260701-01 | Public beta date appears in three places with different meanings; future agents may close the wrong launch gate. | now | unknown_known | pending | Bundle with launch wording decision. |
| BS-20260701-02 | The pricing page says subscriptions are coming, but the billing provider is not chosen. | now | unknown_unknown | pending | Owner chooses Stripe Checkout, Lemon Squeezy, or defer billing. |
| BS-20260701-03 | The terms/privacy row depends on whether the product stores end-user personal data. | now | unconfirmed | pending | External legal confirmation needed after data-flow note. |
| BS-20260701-04 | The Korean onboarding copy uses informal language while the English copy uses formal business language. | next | 미확인 | 대기 | Product voice decision. |
| BS-20260701-05 | The saved-report export was removed from the UI but still appears in the beta checklist. | next | unknown_known | pending | Check UI route and archive if gone. |
| BS-20260701-06 | Mobile signup was intentionally skipped for alpha, but the re-check trigger is missing. | later | deliberate_skip | deferred | Add trigger or archive skip reason. |
| BS-20260701-07 | Password reset email copy has no owner because transactional email was postponed. | next | unconfirmed | pending | Decide whether beta needs email auth. |
| BS-20260701-08 | The support contact is a placeholder in the footer. | next | unknown_unknown | accepted | Owner approves real support route or keeps private beta route. |
| BS-20260701-09 | Error states for failed payment are tracked, but payment is no longer in beta scope. | later | unknown_known | pending | Reject or defer with billing trigger. |
| BS-20260701-10 | Accessibility keyboard pass is open, but the main form was replaced last week. | next | unconfirmed | pending | Re-run cheap tab-through before keeping row. |
| BS-20260701-11 | AI-generated summary disclosure is listed twice with different wording. | now | unknown_unknown | pending | Bundle with public disclosure wording. |
| BS-20260701-12 | The admin invite flow was cut from scope but remains in launch blockers. | next | unknown_known | pending | Confirm removed route, then archive. |
| BS-20260701-13 | Refund policy depends on provider terms and regional sales plan. | now | unconfirmed | pending | Needs provider/legal confirmation. |
| BS-20260701-14 | The analytics consent row is still open, but analytics is disabled in config. | later | unknown_known | pending | Cheap config check, then resolve or defer. |
| BS-20260701-15 | Beta waitlist capacity is not decided; the ops note alternates between 50 and 200 users. | now | unknown_known | pending | Owner capacity decision. |
| BS-20260701-16 | Dark mode was skipped as "later", but there is no re-check trigger. | watch | deliberate_skip | deferred | Add trigger after beta feedback. |
| BS-20260701-17 | The product tour row is probably stale because onboarding now starts with sample data. | next | unconfirmed | pending | Owner chooses archive or keep. |
| BS-20260701-18 | Public roadmap is mentioned in marketing draft but not planned anywhere else. | later | unknown_unknown | pending | Decide whether to reject for beta. |
| BS-20260701-19 | Data retention language uses "30 days" in one doc and "90 days" in another. | now | unknown_unknown | pending | Needs owner/legal decision. |
| BS-20260701-20 | Incident response contact is a single person, but beta support says team response. | later | unconfirmed | pending | Decide operational owner. |
| BS-20260701-21 | The old "manual invoice" finding looks resolved because invoices were removed from beta scope. | later | unknown_known | pending | Archive if scope note is confirmed. |
| BS-20260701-22 | The region list includes EU in marketing copy, but compliance notes only mention US/KR. | now | unknown_unknown | pending | External legal/provider confirmation. |

## Resolved Archive

- BS-20260620-01 - Old CSV export backup - resolved 2026-07-01: export feature removed from alpha scope.
- BS-20260620-02 - First-run context missing - resolved 2026-07-01: Project Context added.

## Checked And Well Covered (as of 2026-07-03)

- Main app has a current README, beta checklist, and launch blockers document.
- UX/UI focus run already inspected main onboarding and dashboard screens.

## Skipped For Now (with re-check triggers)

- Dark mode - intentionally deferred - re-check when beta users ask for long reading sessions.
- Enterprise SSO - out of scope - re-check after paid team accounts exist.

## Decision Packet

| ID | Decision | Recommended option | Options | Why it matters | Status |
| --- | --- | --- | --- | --- | --- |
| DP-20260703-01 | Billing route for beta | Defer paid subscriptions until after private beta | Stripe Checkout / Lemon Squeezy / defer billing | Controls privacy, refund, and payment-error rows | pending |
| DP-20260703-02 | Public launch wording | Use "private beta" everywhere | private beta / public beta / waitlist preview | Prevents launch gates from closing on the wrong milestone | pending |
| DP-20260703-03 | Regions in marketing copy | US/KR only until legal review | US/KR / add EU / remove region wording | Region wording changes compliance expectations | pending |

