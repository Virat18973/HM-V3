# Hospet Sinter Burden Control — v42.0

Streamlit dashboard + Colab backend for the sinter burden cost optimisation (PuLP / CBC).

## Files (deploy together in one folder)

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard |
| `optimizer.py` | Backend model v42.0 (same solver code as the Colab notebook) |
| `master_chemistry_uploader.py` | Thin wrapper around the backend Excel loader (unchanged — `app.py` calls the backend loader directly) |
| `Master_Chemistry_Input_Template.xlsx` | Master workbook template |
| `requirements.txt` | `streamlit`, `pandas`, `numpy`, `PuLP>=2.8,<4`, `openpyxl` |

Run locally: `pip install -r requirements.txt` then `streamlit run app.py`.

## What changed from v40 to v42

**The solver is now a goal-programming ladder.** It always returns the best recipe it can and says what it gave up.

1. **Hard limits, never relaxed:** RM stock over the horizon, mass balance, Mill Scale 5–15 %, fixed recycle rates, IOL share, coke min/max, heat balance, FeO band.
2. **Quality goals, in priority order:** Fe and Basicity first, then CaO, MgO, Al₂O₃, SiO₂, Al₂O₃/SiO₂. Deviation from the *spec* is minimised tier by tier. The plant-approved *tolerance* is a hard outer wall.
3. **Then:** FeO closeness → RM stock ratio (inventory weight dial) → cost.

**Status values**

| Status | Meaning | Dashboard |
|---|---|---|
| Optimal | every spec met | green, QUALITY = PASS |
| Relaxed | a spec missed, everything inside the approved tolerance | amber, QUALITY = WITHIN TOLERANCE |
| Production_Risk (recipe shown) | no recipe stays inside tolerance; closest recipe shown | red, QUALITY = OUT OF TOLERANCE |
| Production_Risk (no recipe) | hard limits cannot be met; a shortage message gives the maximum producible tonnes | red banner |
| No_Production | no fuel available | red banner |

**New in the dashboard**

* Quality cards are green / amber / red against spec and approved tolerance, and a **goal table** shows spec, achieved, outside-by, tolerance and status (Dashboard and Recipe pages).
* **Inputs → Quality & Solver** (new tab): the approved tolerances, "let the model choose IOL / BFR", safety margin on SiO₂ / Al₂O₃ / Fe, hold-the-ratio band, FeO closeness allowance.
* **Inventory Usage** page: ore share drift against stock share, days of cover, and the **A vs B comparison** (A = quality first, B = hold every ore within the band).
* "What the model wants you to know" messages under the status banner (goal misses, ore drift, shortage, fastest-drawn ore).
* **Master data check**: available rows whose chemistry is all zero, or an ore with SiO₂, Al₂O₃ and LOI all zero, are flagged when a master is loaded.
* Reports workbook adds Quality Goals, Ore Drift, Ratio Options, Messages and Tolerances sheets.
* The what-if table no longer shows a cost impact for Production_Risk rows (that recipe is only the closest one, so its cost is not comparable).
* A rounding fix: a run the solver labels Optimal is no longer shown as REVIEW because a value sits 0.003 outside a bound.

Unchanged from v40: return sinter as a share of the charged mix (BFR chemistry-only, IOL in the burden), ore and coke usage following the stock ratio, Mill Scale rule, fixed recycle rates, flux by requirement, planning-horizon stock caps, Manual Burden Control, Plant Run Validation, Productivity.

## Master workbook

Columns are matched by header, sheet names do not matter. Required: Material, Group, Fe_%, SiO2_%, Al2O3_%, CaO_%, MgO_%, LOI_%, Moisture_%, Available_Stock_t, Price_Rs_t. Optional: Material_Role, Tech_Min_kg_t, Tech_Max_kg_t, CV_kcal_kg, FC_Pct (Fuel rows), Fines_% or Fines_Pct.

Tech Min / Max (blank or 0 = no limit) only matter for flux limits and fixed recycle rates (Tech Min = Tech Max). Iron ores, coke, IOL and BFR ignore them unless "Also apply Tech Min/Max to iron ores and coke" is ticked. A Tech Min above 0 on a flux **forces** that usage.

## Placeholders — confirm with the plant before using results for decisions

* Every quality **tolerance** except SiO₂ max 6.2 % (edit under Inputs → Quality & Solver).
* Strand area (default 50 m²) and the feed-rate basis (charged mix, dry).
* FeO / heat-balance coefficients (provisional; calibrate against plant coke / FeO history).
* Goal weights, the FeO closeness allowance and the hold-ratio band.
* Fuel-ash composition is not read from the Excel; it uses the model defaults unless edited under Inputs → Fuel Ash Chemistry.
* Element recovery factors in Plant Run Validation are 1.0 until calibrated.

## Known limitations

* At inventory weight 1.0 the recipe can cost more than the pure-cost recipe; the dashboard shows the exact premium.
* Solver state (last-run report, active fuel-ash settings) is held at module level, so two people running the optimizer at the same moment on one shared deployment could see each other's report details. Use one instance per user if that matters.
* Back-test against real plant days before using the numbers for decisions.
