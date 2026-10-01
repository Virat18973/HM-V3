"""
Hospet Cost Studio: sinter model, MBF model and the combined hot metal cost model in one app.

  streamlit run app.py

Landing page: Combined cost model > Hot metal cost.  The original sinter dashboard (sinter/app.py) and MBF dashboard
(mbf/app.py) are used unchanged: every page, tab, button, chart and export is still there, drawn by the original code
inside this app (see shared/nsrun.py for the few mechanical, in-memory adjustments).
"""
import streamlit as st  # noqa: E402

st.set_page_config(page_title="Hospet Cost Studio", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")

from shared import nsrun, theme  # noqa: E402
from combined import handoff as H, page as CP  # noqa: E402

WORKSPACES = {
    "combined": ("Combined cost model", [("Setup", ["Uploads & shared settings"]), ("Results", ["Hot metal cost"]),
                                         ("Analysis", ["Basicity scan", "Price drivers", "Saved scenarios"]), ("Reports", ["Export", "Glossary"])]),
    "sinter": ("Sinter model", [("Setup", ["Upload & Settings", "Inputs", "RM Stock & Materials"]), ("Results", ["Dashboard", "Recipe & Composition"]),
                                ("Analysis", ["Inventory Usage", "Manual Burden Control", "Scenario Analysis", "Plant Run Validation", "Productivity", "Wet Specific Consumption"]),
                                ("Reports", ["Reports"])]),
    "mbf": ("MBF model", [("Setup", ["Upload & settings", "Inputs", "Materials & stock"]), ("Results", ["Dashboard", "Burden & cost"]),
                          ("Analysis", ["Slag oxides", "Trends", "Scenario analysis", "Heat audit"]), ("Reports", ["Reports & export"])]),
}
DEFAULT_PAGE = {"combined": "Hot metal cost", "sinter": "Dashboard", "mbf": "Dashboard"}
W = CP.W

S = st.session_state
for k in WORKSPACES:
    S.setdefault(f"route_{k}", DEFAULT_PAGE[k])
S.setdefault("ws", "combined")
S.setdefault("mbf_sinter_mode", H.MODEL)

sns, mns = H.boot()            # both dashboards' state is created here (nothing is drawn)

# ---------------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("<div class='brand'>Hospet Cost Studio</div><div class='brand-sub'>Sinter plant + blast furnace: cost of one tonne of hot metal</div>", unsafe_allow_html=True)
    ws = st.radio("Workspace", list(WORKSPACES), key="ws", format_func=lambda k: WORKSPACES[k][0], label_visibility="collapsed")
    for group, items in WORKSPACES[ws][1]:
        st.markdown(f"<div class='nav-group'>{group}</div>", unsafe_allow_html=True)
        for it in items:
            if st.button(it, key=f"nav_{ws}_{it}", type="primary" if S[f"route_{ws}"] == it else "secondary", **W):
                S[f"route_{ws}"] = it
                st.rerun()
    foot = st.container()

st.markdown(theme.css(ws), unsafe_allow_html=True)
page = S[f"route_{ws}"]


def mbf_banner():
    mode = st.radio("Sinter row in the furnace table", [H.MODEL, H.TYPED], key="mbf_sinter_mode", horizontal=True,
                    help="'From sinter model' replaces the switched-on Sinter row with the sinter model's last result. 'Typed row' is the MBF dashboard exactly as it was.")
    info = H.sync_mbf_sinter_row(sns, mode)
    st_ = info["state"]
    if st_ == "typed":
        st.markdown("<div class='notice w'><b>Typed row (original behaviour).</b> The furnace uses the sinter values in its materials table. The combined cost model does not use this setting: it always takes sinter from the sinter model.</div>", unsafe_allow_html=True)
    elif st_ == "norow":
        st.markdown("<div class='notice r'><b>No Sinter row is switched on.</b> Switch one on under Materials &amp; stock. The sinter model's result takes its place.</div>", unsafe_allow_html=True)
    elif st_ == "missing":
        st.markdown("<div class='notice r'><b>The sinter model has not been run.</b> The sinter row comes from it, so the furnace cannot run yet. Run the sinter model, or choose Typed row.</div>", unsafe_allow_html=True)
        if st.button("Open the sinter model", key="mbf_open_sinter"):
            S["ws"] = "sinter"
            S["route_sinter"] = "Dashboard"
            st.rerun()
    else:
        h = info["handoff"]
        v = h["vals"]
        extra = ""
        if h["stale"]:
            extra += " <b>Sinter inputs have changed since that run:</b> run the sinter model again."
        if h["status"] != "Optimal":
            extra += f" Sinter status is {h['status']}: read costs as an estimate."
        kind = "w" if (h["stale"] or h["status"] != "Optimal") else "g"
        st.markdown(f"<div class='notice {kind}'><b>Sinter row from the sinter model</b>, run at {h['time']:%H:%M}, {h['tonnes']:,.0f} t assumed: "
                    f"₹{v['Price_Rs_t']:,.0f} per t, Fe {v['Fe']:.2f}, CaO {v['CaO']:.2f}, SiO2 {v['SiO2']:.2f}, Al2O3 {v['Al2O3']:.2f}, MgO {v['MgO']:.2f}; "
                    f"moisture, S and Mn stay from the MBF table.{extra}</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------------- the page
if ws == "combined":
    CP.render(page, sns, mns)
elif ws == "sinter":
    nsrun.load_app("sinter", render=True)
    H.track_sinter_run(sns)
else:
    mbf_banner()
    nsrun.load_app("mbf", render=True, extra_blockers=lambda: H.mbf_extra_blockers(sns))

# ---------------------------------------------------------------------------------- sidebar footer (after the page, so it is current)
with foot:
    sl, _ = sns["status_label"]()
    ml, _ = mns["status_label"]()
    run = S.get("cmb_run")
    cl = (f"run {run['time']:%H:%M}, {'knife-edge' if run.get('jump') else ('converged' if run['converged'] else 'not converged')}" if run and run.get("ok") else "not run")
    st.markdown(f"<div class='side-foot'><b>Sinter model</b><br>{sl.split(' — ')[0].title()}<br><br><b>MBF model</b><br>{ml}<br><br><b>Combined</b><br>{cl}</div>"
                , unsafe_allow_html=True)
