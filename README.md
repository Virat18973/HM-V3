# Hospet Cost Studio

One app for the cost of one tonne of hot metal (Rs/tHM): the **sinter model**, the **MBF (furnace) model** and a
**combined model** that feeds the sinter plant's result into the furnace. The two original dashboards are kept whole.

    pip install -r requirements.txt
    streamlit run app.py

Python 3.10+ recommended. Google Fonts and the Material icon font need internet; every font has a fallback.

## What is in it

| Workspace | Pages |
|---|---|
| **Combined cost model** (landing) | Hot metal cost, Uploads & shared settings, Basicity scan, Price drivers, Saved scenarios, Export, Glossary |
| **Sinter model** (original dashboard, 12 pages) | Upload & Settings, Inputs, RM Stock & Materials, Dashboard, Recipe & Composition, Inventory Usage, Manual Burden Control, Scenario Analysis, Plant Run Validation, Productivity, Wet Specific Consumption, Reports |
| **MBF model** (original dashboard, 10 pages) | Upload & settings, Inputs, Materials & stock, Dashboard, Burden & cost, Slag oxides, Trends, Scenario analysis, Reports & export, Heat audit |

## How the combined model works

1. The sinter model runs on its own Excel file. Its result (price = dry raw-material cost + O&M, plus Fe, CaO, SiO2,
   Al2O3, MgO) replaces the furnace table's one switched-on **Sinter** row. Moisture, S and Mn stay from the MBF Excel.
2. The furnace model runs and says how much sinter it uses (kg/tHM). Times the plan (tHM) that is the sinter tonnage
   needed, and the sinter model runs again at that tonnage. This repeats until the tonnage settles.
3. Rules: the run reports whether it converged; a failed sinter run stops the loop with the sinter model's message;
   sinter is capped at what the plant can make within tolerance (Optimal or Relaxed), and the furnace then takes more
   ore for the rest; sinter and furnace materials, stock and stock checks are never mixed, even when names match.

The MBF workspace has a switch, **Sinter row in the furnace table**: *From sinter model* (default) or *Typed row*
(the original MBF behaviour, typed values restored). The combined page always uses the sinter model.

Plan (tHM) sets the furnace's stock caps and the sinter tonnage. It is a combined-page setting (default 9,000).

## Known behaviour to read before trusting a number

* **Knife-edge near the sinter ceiling.** With the sample files the furnace's sinter demand flips between two burdens
  within a tonne or so of sinter, because several slag limits bind together. The loop narrows it to about half a tonne
  and shows the result from the side where the plant makes at least what the furnace uses. Differences of about
  Rs 50/tHM or less are noise. The page says so when it happens.
* **Relaxed sinter.** The sample sinter misses SiO2 (6.07 against 5.8) and Al2O3/SiO2 but is inside the approved
  tolerance, so the hot metal cost is an estimate.
* A combined run takes 15 to 25 s; price drivers about a minute; scans about 20 s per few points.
* Fonts (Barlow Condensed, Source Sans 3) are a best match to the prototype screenshot and live in `shared/theme.py`.

## Layout

    app.py                 router, sidebar, MBF sinter-row banner
    combined/loop.py       the loop (no Streamlit code): convergence, cap, failure stop, knife-edge refinement
    combined/handoff.py    sinter -> furnace row, stale detection, input diffs, the two stock checks
    combined/page.py       the combined pages
    shared/nsrun.py        runs the original dashboards unchanged (see below)
    shared/theme.py        palette, fonts, one stylesheet for all three workspaces
    sinter/                original sinter dashboard + engine (optimizer.py)       -- unchanged
    mbf/                   original MBF dashboard + engine (optimiser.py, analytics.py) + its tests -- unchanged
    sample_inputs/         SInter_Input.xlsx, MBF_Input.xlsx
    tests/                 combined tests; ENGINE_HASHES.txt records the SHA-256 of the untouched files

### How the originals are reused without editing them

`shared/nsrun.py` reads each original `app.py`, applies a few mechanical rewrites **in memory**, and runs it: it drops
`set_page_config`, the dashboard's own CSS and sidebar, gives each dashboard a prefixed view of `st.session_state` and
prefixed widget keys (`sinter__`, `mbf__`) so they never collide, maps the old colours and fonts to the shared theme,
and lets the MBF page say why it cannot run when the sinter row is missing. Every page function, table, chart and
export is the original code. Both originals still run alone: `streamlit run sinter/app.py`, `streamlit run mbf/app.py`.

## Tests

    pip install -r requirements-dev.txt
    pytest -q tests                  # combined tests (about 5 minutes)
    cd mbf && pytest -q tests        # the original MBF tests, against the unchanged mbf/app.py (about 5 minutes)

`tests/test_engines_unchanged.py` fails if any engine or original dashboard file is edited.
