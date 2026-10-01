# Page-by-page checklist (tick as you go)

Start: `streamlit run app.py`. Use the sample files in `sample_inputs/`.

## Combined cost model
- [ ] Uploads & shared settings: both file cards show; plan, tolerance, passes editable; sinter and furnace upload tabs work
- [ ] Hot metal cost: before a run it says "No run yet"; Run both models gives the three-stage hero, chips, money table, alerts
- [ ] Engineer view lists the full MBF and sinter values; Management view hides them
- [ ] Change a sinter price, the "Inputs changed since this run" chip appears; run again and Rs/tHM moves
- [ ] Use this run as baseline, then "Change vs baseline" reads No change; last-month and budget boxes show differences
- [ ] Change since last run names what you changed
- [ ] Basicity scan, Price drivers, Saved scenarios (save two, compare), Export (workbook downloads), Glossary

## Sinter model (all 12 pages unchanged)
- [ ] Run optimizer on the Dashboard; every page opens; nothing from MBF leaks in

## MBF model (all 10 pages unchanged)
- [ ] Before the sinter model has run: banner says so, Run optimiser is blocked
- [ ] After: banner shows the sinter row values; Materials & stock shows the replaced row; Run optimiser works
- [ ] Typed row mode restores the typed sinter values

## Cross-checks
- [ ] Sinter alone: Rs 6,907.94 raw, Rs 7,657.94 with O&M on the sample file (12 materials on, 10,000 t, 7 days, IOL 8%, BFR 17%, O&M 750)
- [ ] MBF alone with that sinter row, Ore-3, Coke-1, BHQ off: Rs 31,039 at 77.3% sinter (plan tHM off)
