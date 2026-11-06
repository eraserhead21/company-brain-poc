<!-- Export of the Google Drive doc "Alpha - Cutover Rehearsal Notes 2026-10-20" (Drive file 1gT8STEC4uI-F77v98NnShcYwy8iwWwUp59OyeRIDJcw), 2026-11-05.
Fictional test data: every name, contact detail, secret and commercial term
below is planted for the redaction test. Capture reads the Drive copy;
the brief and cards cite this file. -->

PROJECT ALPHA - CUTOVER REHEARSAL NOTES

20 October 2026. Present: Priya, Marco, Aisha, Lena.

What we did

- Ran the new streaming billing export against a copy of September's real invoices, before cutover.
- The rehearsal found 3 tariff codes (night rate, weekend rate, export credit) that the new export did not map. The old batch job handled them in a lookup table nobody had documented.
- Aisha added the 3 codes to the export mapping and the rerun matched September's invoices line for line.

Lesson

- Reconcile a new export against last month's real invoices before cutover, not against test data. Undocumented business rules live in the old system and only show up against real data.

Next

- Add the reconciliation run to the go-live checklist.
