<!-- Export of the Google Drive doc "Alpha - Meeting Notes 2026-10-13 Weekly" (Drive file 1Hx_L-zPTGFqLDC12rQv9Yu3V7Der_D7k4c0xWAloYdo), 2026-11-03.
Fictional test data: every name, contact detail, secret and commercial term
below is planted for the redaction test. Capture reads the Drive copy;
the brief and cards cite this file. -->

MEETING NOTES - PROJECT ALPHA WEEKLY

13 October 2026. Present: Priya, Marco, Aisha, Jun, Tom, Lena.

Welcome

- Lena Vogt joins as an Engineer from today, on a contractor day rate of EUR 850.
- Lena's private email for the onboarding paperwork: lena.vogt.private@example.com

Updates

- Dry run of the shadow comparison started Monday.
- On day 2 of the dry run the mismatch alert fired. Batch totals use the billing local day (00:00 to 00:00 Amsterdam time); the stream comparison used the UTC day. Same readings, different day boundaries. Aisha aligned both to the billing local day. Lesson: fix the comparison window to the billing day boundary before a shadow run starts, not during it.
- Northwind's firmware v2.4 rollout slipped one week, to 27 October, because it collided with their change-freeze week. We never asked for their change-freeze calendar. Next time, ask for the customer's change-freeze calendar at kickoff and plan around it.
- Shadow run start moved to 19 November (was 17 November) because of the firmware slip. Go-live stays 28 November.
- Billing export interval: 15 minutes.

People

- Marco off sick 14 and 15 October with flu. Aisha covers his reviews.

Access

- Staging Grafana: admin / Gr4fana-stg-11
