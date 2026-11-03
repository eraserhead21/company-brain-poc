<!-- Export of the Google Drive doc "Alpha - Team Channel Log (September)" (Drive file 1vIZP8YRXJJ01sj8EXGqgoKjtrvkklN3nyZkv59l76oA), 2026-11-03.
Fictional test data: every name, contact detail, secret and commercial term
below is planted for the redaction test. Capture reads the Drive copy;
the brief and cards cite this file. -->

TEAM CHANNEL LOG - #alpha (stand-in for the Teams channel)

- [16 Sep 09:12] Marco: if the build breaks tonight call me, +31 6 0000 0000
- [16 Sep 09:40] Jun: dup prototype works. Key = meter_id + reading_ts, upsert on conflict. PR soon.
- [18 Sep 14:03] Tom: anyone have the Northwind API test token? nvm found it: nwapi_test_7f3a9c2e1b55
- [18 Sep 14:05] Marco: Tom please don't paste tokens here.
- [21 Sep 11:30] Aisha: DST question. Readings at 02:30 on 25 Oct exist twice in meter local time. We will double count unless we store UTC.
- [21 Sep 11:45] Marco: agreed, store UTC, convert only at the billing export. I'll write ADR-001.
- [23 Sep 16:20] Priya: heads up, Janet says Northwind is talking to Contoso Metering about switching vendor next year. Keep it between us.
- [25 Sep 10:02] Aisha: shadow-run dashboard draft is up. Compares daily totals per meter group.
- [26 Sep 17:48] Marco: congrats Aisha, your raise to EUR 72k is approved!
- [29 Sep 08:55] Priya: Aisha owns the on-call rota from October.
- [30 Sep 13:10] Jun: firmware v2.3 meters send timestamps like 2026-13-01. Logging them and rejecting for now.
