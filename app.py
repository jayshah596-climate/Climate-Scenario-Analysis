import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Climate Scenario Analysis", layout="wide")
st.title("🌍 Company-Level Climate Scenario Analysis Dashboard")
st.caption("Physical & transition risk modelling under NGFS and IPCC scenarios — TCFD-aligned")

# ─────────────────────────────────────────────────────────────────────────────
# REFERENCE DATA
# ─────────────────────────────────────────────────────────────────────────────

SCENARIOS = {
    "Net Zero 2050 (NGFS ~1.5°C)":      {"warming": 1.5, "cp_2030": 160, "cp_2050": 250, "cp_2025": 50,  "pathway": "Orderly",     "ipcc": "SSP1-1.9"},
    "Below 2°C (NGFS ~1.8°C)":          {"warming": 1.8, "cp_2030": 75,  "cp_2050": 140, "cp_2025": 25,  "pathway": "Orderly",     "ipcc": "SSP1-2.6"},
    "Delayed Transition (NGFS ~1.8°C)": {"warming": 1.8, "cp_2030": 30,  "cp_2050": 300, "cp_2025": 5,   "pathway": "Disorderly",  "ipcc": "SSP2-4.5"},
    "Divergent Net Zero (NGFS ~1.6°C)": {"warming": 1.6, "cp_2030": 120, "cp_2050": 220, "cp_2025": 35,  "pathway": "Disorderly",  "ipcc": "SSP1-2.6"},
    "Hot House World (NGFS ~4°C)":       {"warming": 4.0, "cp_2030": 5,   "cp_2050": 10,  "cp_2025": 2,   "pathway": "No transition","ipcc": "SSP5-8.5"},
    "SSP1-2.6 (IPCC ~1.9°C)":           {"warming": 1.9, "cp_2030": 50,  "cp_2050": 100, "cp_2025": 20,  "pathway": "Orderly",     "ipcc": "SSP1-2.6"},
    "SSP2-4.5 (IPCC ~2.7°C)":           {"warming": 2.7, "cp_2030": 20,  "cp_2050": 40,  "cp_2025": 10,  "pathway": "Moderate",    "ipcc": "SSP2-4.5"},
    "SSP3-7.0 (IPCC ~3.6°C)":           {"warming": 3.6, "cp_2030": 8,   "cp_2050": 15,  "cp_2025": 4,   "pathway": "No transition","ipcc": "SSP3-7.0"},
    "SSP5-8.5 (IPCC ~4.4°C)":           {"warming": 4.4, "cp_2030": 5,   "cp_2050": 10,  "cp_2025": 2,   "pathway": "No transition","ipcc": "SSP5-8.5"},
}

SECTORS = [
    "Energy", "Manufacturing", "Real Estate", "Finance",
    "Agriculture", "Transport", "Technology", "Healthcare",
    "Utilities", "Retail", "Custom"
]

REGIONS = [
    "Europe", "Asia-Pacific", "North America",
    "Latin America", "Africa", "Middle East", "South Asia"
]

# Physical risk hazard intensity per °C of warming (fraction of asset value at risk)
PHYSICAL_RISK = {
    "Energy":        {"Flood": 0.07, "Heat Stress": 0.06, "Water Stress": 0.09, "Storm/Wind": 0.05},
    "Manufacturing": {"Flood": 0.08, "Heat Stress": 0.05, "Water Stress": 0.07, "Storm/Wind": 0.06},
    "Real Estate":   {"Flood": 0.12, "Heat Stress": 0.04, "Water Stress": 0.05, "Storm/Wind": 0.10},
    "Finance":       {"Flood": 0.03, "Heat Stress": 0.01, "Water Stress": 0.02, "Storm/Wind": 0.02},
    "Agriculture":   {"Flood": 0.10, "Heat Stress": 0.12, "Water Stress": 0.15, "Storm/Wind": 0.07},
    "Transport":     {"Flood": 0.09, "Heat Stress": 0.04, "Water Stress": 0.03, "Storm/Wind": 0.08},
    "Technology":    {"Flood": 0.04, "Heat Stress": 0.03, "Water Stress": 0.02, "Storm/Wind": 0.03},
    "Healthcare":    {"Flood": 0.05, "Heat Stress": 0.03, "Water Stress": 0.03, "Storm/Wind": 0.04},
    "Utilities":     {"Flood": 0.08, "Heat Stress": 0.07, "Water Stress": 0.11, "Storm/Wind": 0.06},
    "Retail":        {"Flood": 0.06, "Heat Stress": 0.03, "Water Stress": 0.02, "Storm/Wind": 0.05},
    "Custom":        {"Flood": 0.06, "Heat Stress": 0.04, "Water Stress": 0.05, "Storm/Wind": 0.05},
}

# Regional multiplier on physical risk (coastal/tropical regions more exposed)
REGION_MULTIPLIER = {
    "Europe": 0.85, "Asia-Pacific": 1.15, "North America": 0.90,
    "Latin America": 1.20, "Africa": 1.30, "Middle East": 1.25, "South Asia": 1.35,
}

# Transition risk: revenue-at-risk % per scenario (policy + market + tech + reputational)
TRANSITION_RISK = {
    "Energy":        {"policy": 0.18, "market": 0.14, "technology": 0.10, "reputational": 0.04},
    "Manufacturing": {"policy": 0.10, "market": 0.08, "technology": 0.09, "reputational": 0.03},
    "Real Estate":   {"policy": 0.07, "market": 0.05, "technology": 0.04, "reputational": 0.02},
    "Finance":       {"policy": 0.06, "market": 0.07, "technology": 0.05, "reputational": 0.04},
    "Agriculture":   {"policy": 0.09, "market": 0.06, "technology": 0.08, "reputational": 0.03},
    "Transport":     {"policy": 0.14, "market": 0.12, "technology": 0.13, "reputational": 0.03},
    "Technology":    {"policy": 0.04, "market": 0.05, "technology": 0.06, "reputational": 0.02},
    "Healthcare":    {"policy": 0.05, "market": 0.04, "technology": 0.05, "reputational": 0.02},
    "Utilities":     {"policy": 0.15, "market": 0.10, "technology": 0.11, "reputational": 0.03},
    "Retail":        {"policy": 0.06, "market": 0.07, "technology": 0.05, "reputational": 0.03},
    "Custom":        {"policy": 0.08, "market": 0.07, "technology": 0.06, "reputational": 0.03},
}

# Stranded asset rate by scenario (% of fixed asset base at risk by 2050)
STRANDED_RATE = {
    "Net Zero 2050 (NGFS ~1.5°C)":      0.35,
    "Below 2°C (NGFS ~1.8°C)":          0.22,
    "Delayed Transition (NGFS ~1.8°C)": 0.28,
    "Divergent Net Zero (NGFS ~1.6°C)": 0.30,
    "Hot House World (NGFS ~4°C)":       0.05,
    "SSP1-2.6 (IPCC ~1.9°C)":           0.20,
    "SSP2-4.5 (IPCC ~2.7°C)":           0.12,
    "SSP3-7.0 (IPCC ~3.6°C)":           0.06,
    "SSP5-8.5 (IPCC ~4.4°C)":           0.04,
}

YEARS = [2025, 2030, 2035, 2040, 2050]

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR INPUTS
# ─────────────────────────────────────────────────────────────────────────────

st.sidebar.header("🏢 Company Information")
company_name = st.sidebar.text_input("Company Name", "Example Corp")
sector_choice = st.sidebar.selectbox("Sector", SECTORS)
if sector_choice == "Custom":
    sector = st.sidebar.text_input("Enter custom sector name", "Custom")
    if sector not in PHYSICAL_RISK:
        sector = "Custom"
else:
    sector = sector_choice
region = st.sidebar.selectbox("Region", REGIONS)

st.sidebar.header("📊 Financials")
revenue = st.sidebar.number_input("Annual Revenue ($M)", min_value=0.0, value=500.0, step=10.0)
total_assets = st.sidebar.number_input("Total Assets ($M)", min_value=0.0, value=1000.0, step=10.0)
fixed_assets = st.sidebar.number_input("Fixed / Physical Assets ($M)", min_value=0.0, value=400.0, step=10.0)

st.sidebar.header("🌿 GHG Emissions (tCO2e/yr)")
scope1 = st.sidebar.number_input("Scope 1", min_value=0.0, value=5000.0)
scope2 = st.sidebar.number_input("Scope 2", min_value=0.0, value=7000.0)
scope3 = st.sidebar.number_input("Scope 3", min_value=0.0, value=13000.0)
total_emissions = scope1 + scope2 + scope3

st.sidebar.header("🌡️ Scenario Selection")
selected_scenarios = st.sidebar.multiselect(
    "Select scenarios to model",
    list(SCENARIOS.keys()),
    default=["Net Zero 2050 (NGFS ~1.5°C)", "Below 2°C (NGFS ~1.8°C)", "Hot House World (NGFS ~4°C)"]
)
if not selected_scenarios:
    st.sidebar.warning("Please select at least one scenario.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# CALCULATIONS
# ─────────────────────────────────────────────────────────────────────────────

def carbon_price_for_year(scenario_key, year):
    s = SCENARIOS[scenario_key]
    if year <= 2025:
        return s["cp_2025"]
    elif year <= 2030:
        t = (year - 2025) / 5
        return s["cp_2025"] + t * (s["cp_2030"] - s["cp_2025"])
    elif year <= 2050:
        t = (year - 2030) / 20
        return s["cp_2030"] + t * (s["cp_2050"] - s["cp_2030"])
    return s["cp_2050"]

def physical_var(scenario_key, year, sector, region, total_assets_m):
    warming = SCENARIOS[scenario_key]["warming"]
    # Warming accumulates gradually; apply fraction by year
    year_fraction = min(1.0, (year - 2020) / 30)
    effective_warming = warming * year_fraction
    hazards = PHYSICAL_RISK.get(sector, PHYSICAL_RISK["Custom"])
    region_mult = REGION_MULTIPLIER.get(region, 1.0)
    total_hazard = sum(hazards.values()) * effective_warming * region_mult
    return total_assets_m * total_hazard  # $M

def transition_cost(scenario_key, year, sector, total_emissions_tco2, revenue_m):
    s = SCENARIOS[scenario_key]
    cp = carbon_price_for_year(scenario_key, year)
    carbon_cost = (total_emissions_tco2 * cp) / 1e6  # convert to $M

    # Transition risk scales with how aggressive the scenario is (higher carbon price = more disruption)
    transition_intensity = cp / 250  # normalised against max carbon price
    t_risks = TRANSITION_RISK.get(sector, TRANSITION_RISK["Custom"])
    market_cost = revenue_m * (t_risks["market"] + t_risks["technology"] + t_risks["reputational"]) * transition_intensity
    return carbon_cost + market_cost  # $M

def stranded_assets(scenario_key, year, fixed_assets_m):
    rate = STRANDED_RATE.get(scenario_key, 0.1)
    year_fraction = min(1.0, (year - 2020) / 30)
    return fixed_assets_m * rate * year_fraction  # $M

def build_projection(scenario_key):
    rows = []
    for year in YEARS:
        phys = physical_var(scenario_key, year, sector, region, total_assets)
        trans = transition_cost(scenario_key, year, sector, total_emissions, revenue)
        strand = stranded_assets(scenario_key, year, fixed_assets)
        total = phys + trans + strand
        rows.append({
            "Year": year,
            "Scenario": scenario_key,
            "Warming (°C)": SCENARIOS[scenario_key]["warming"],
            "Pathway": SCENARIOS[scenario_key]["pathway"],
            "Physical Risk ($M)": round(phys, 2),
            "Transition Cost ($M)": round(trans, 2),
            "Stranded Assets ($M)": round(strand, 2),
            "Total Exposure ($M)": round(total, 2),
            "Carbon Price ($/tCO2)": round(carbon_price_for_year(scenario_key, year), 0),
        })
    return rows

all_rows = []
for sc in selected_scenarios:
    all_rows.extend(build_projection(sc))
df_all = pd.DataFrame(all_rows)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard", "🌊 Physical Risk", "⚡ Transition Risk",
    "💰 Financial Projections", "📋 TCFD Narratives", "📥 Export"
])

# ── TAB 1: DASHBOARD ─────────────────────────────────────────────────────────
with tab1:
    st.subheader(f"Overview — {company_name}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total GHG Emissions", f"{total_emissions:,.0f} tCO2e")
    c2.metric("Sector", sector)
    c3.metric("Region", region)
    c4.metric("Scenarios Modelled", len(selected_scenarios))

    st.markdown("---")

    # Peak exposure table
    peak_rows = []
    for sc in selected_scenarios:
        sc_df = df_all[df_all["Scenario"] == sc]
        peak = sc_df.loc[sc_df["Total Exposure ($M)"].idxmax()]
        peak_rows.append({
            "Scenario": sc,
            "Warming": f"{SCENARIOS[sc]['warming']}°C",
            "Pathway": SCENARIOS[sc]["pathway"],
            "IPCC Equivalent": SCENARIOS[sc]["ipcc"],
            "Peak Total Exposure ($M)": f"${peak['Total Exposure ($M)']:,.1f}M",
            "Peak Year": int(peak["Year"]),
        })
    st.subheader("Scenario Summary")
    st.dataframe(pd.DataFrame(peak_rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    # Scenario comparison chart
    fig = px.line(
        df_all, x="Year", y="Total Exposure ($M)", color="Scenario",
        markers=True,
        title="Total Climate Financial Exposure by Scenario (2025–2050)",
        labels={"Total Exposure ($M)": "Total Exposure ($M)", "Year": "Year"},
    )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.4))
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 2: PHYSICAL RISK ─────────────────────────────────────────────────────
with tab2:
    st.subheader("Physical Risk Assessment")
    st.markdown(
        "Physical risks arise from climate hazards that damage assets or disrupt operations. "
        "Assessed across flood, heat stress, water stress, and storm/wind."
    )

    hazards = PHYSICAL_RISK.get(sector, PHYSICAL_RISK["Custom"])
    region_mult = REGION_MULTIPLIER.get(region, 1.0)

    # Hazard breakdown per scenario at 2050
    hazard_rows = []
    for sc in selected_scenarios:
        warming = SCENARIOS[sc]["warming"]
        for hazard, intensity in hazards.items():
            exposure = total_assets * intensity * warming * region_mult
            hazard_rows.append({
                "Scenario": sc,
                "Hazard Type": hazard,
                "Warming (°C)": warming,
                "Intensity (per °C)": f"{intensity:.2%}",
                "Region Multiplier": region_mult,
                "Asset Exposure ($M)": round(exposure, 2),
            })
    df_hazard = pd.DataFrame(hazard_rows)

    # Heatmap: hazard × scenario
    pivot = df_hazard.pivot_table(
        index="Hazard Type", columns="Scenario", values="Asset Exposure ($M)", aggfunc="sum"
    )
    fig_heat = px.imshow(
        pivot,
        text_auto=".1f",
        color_continuous_scale="YlOrRd",
        title="Physical Risk Exposure Heatmap ($M) — by Hazard Type & Scenario",
        labels={"color": "Exposure ($M)"},
        aspect="auto",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # Physical risk over time
    fig_phys = px.line(
        df_all, x="Year", y="Physical Risk ($M)", color="Scenario",
        markers=True, title="Physical Risk ($M) Over Time by Scenario",
    )
    st.plotly_chart(fig_phys, use_container_width=True)

    st.subheader("Hazard Breakdown Table")
    st.dataframe(df_hazard, use_container_width=True, hide_index=True)

# ── TAB 3: TRANSITION RISK ────────────────────────────────────────────────────
with tab3:
    st.subheader("Transition Risk Assessment")
    st.markdown(
        "Transition risks arise from policy changes (carbon pricing), market shifts, "
        "technology disruption, and reputational pressure as the economy decarbonises."
    )

    t_risks = TRANSITION_RISK.get(sector, TRANSITION_RISK["Custom"])

    # Carbon price paths
    cp_rows = []
    for sc in selected_scenarios:
        for year in YEARS:
            cp_rows.append({
                "Scenario": sc,
                "Year": year,
                "Carbon Price ($/tCO2)": carbon_price_for_year(sc, year),
            })
    df_cp = pd.DataFrame(cp_rows)

    fig_cp = px.line(
        df_cp, x="Year", y="Carbon Price ($/tCO2)", color="Scenario",
        markers=True, title="Carbon Price Pathway by Scenario ($/tCO2)",
    )
    st.plotly_chart(fig_cp, use_container_width=True)

    # Transition risk decomposition at 2050
    decomp_rows = []
    for sc in selected_scenarios:
        cp_2050 = SCENARIOS[sc]["cp_2050"]
        intensity = cp_2050 / 250
        carbon_cost = (total_emissions * cp_2050) / 1e6
        for rtype, rate in t_risks.items():
            if rtype == "policy":
                val = carbon_cost
                label = "Carbon Cost (Policy)"
            else:
                val = revenue * rate * intensity
                label = rtype.capitalize() + " Risk"
            decomp_rows.append({"Scenario": sc, "Risk Type": label, "Exposure ($M)": round(val, 2)})

    df_decomp = pd.DataFrame(decomp_rows)
    fig_decomp = px.bar(
        df_decomp, x="Scenario", y="Exposure ($M)", color="Risk Type", barmode="stack",
        title="Transition Risk Decomposition at 2050 ($M)",
    )
    fig_decomp.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig_decomp, use_container_width=True)

    # Transition cost over time
    fig_trans = px.line(
        df_all, x="Year", y="Transition Cost ($M)", color="Scenario",
        markers=True, title="Transition Cost ($M) Over Time by Scenario",
    )
    st.plotly_chart(fig_trans, use_container_width=True)

    st.subheader("Sector Transition Risk Profile")
    tr_profile = pd.DataFrame([{
        "Risk Type": k.capitalize(),
        "Base Rate (% revenue)": f"{v:.1%}",
        "Applies To": sector,
    } for k, v in t_risks.items()])
    st.dataframe(tr_profile, use_container_width=True, hide_index=True)

# ── TAB 4: FINANCIAL PROJECTIONS ──────────────────────────────────────────────
with tab4:
    st.subheader("Financial Impact Projections (2025–2050)")
    st.markdown(
        "Cumulative financial exposure by scenario, decomposed into physical risk, "
        "transition costs, and stranded assets."
    )

    # Multi-pathway stacked area (last selected scenario shown individually; full comparison as lines)
    fig_proj = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Total Exposure Comparison ($M)", "Risk Decomposition at 2050 ($M)"),
        shared_yaxes=False,
    )

    colors = px.colors.qualitative.Plotly
    for i, sc in enumerate(selected_scenarios):
        sc_df = df_all[df_all["Scenario"] == sc]
        fig_proj.add_trace(go.Scatter(
            x=sc_df["Year"], y=sc_df["Total Exposure ($M)"],
            mode="lines+markers", name=sc,
            line=dict(color=colors[i % len(colors)]),
        ), row=1, col=1)

    # Decomposition bar at 2050
    df_2050 = df_all[df_all["Year"] == 2050]
    for col_name, color in [("Physical Risk ($M)", "#3182bd"), ("Transition Cost ($M)", "#e6550d"), ("Stranded Assets ($M)", "#756bb1")]:
        fig_proj.add_trace(go.Bar(
            x=df_2050["Scenario"], y=df_2050[col_name],
            name=col_name.replace(" ($M)", ""), marker_color=color,
        ), row=1, col=2)
    fig_proj.update_layout(barmode="stack", height=500, showlegend=True)
    fig_proj.update_xaxes(tickangle=-30, row=1, col=2)
    st.plotly_chart(fig_proj, use_container_width=True)

    # Stranded assets
    fig_strand = px.area(
        df_all, x="Year", y="Stranded Assets ($M)", color="Scenario",
        title="Stranded Asset Risk Over Time ($M)",
    )
    st.plotly_chart(fig_strand, use_container_width=True)

    # Sensitivity: ±20% range on total exposure for primary scenario
    primary = selected_scenarios[0]
    primary_df = df_all[df_all["Scenario"] == primary].copy()
    primary_df["Upper Bound ($M)"] = primary_df["Total Exposure ($M)"] * 1.20
    primary_df["Lower Bound ($M)"] = primary_df["Total Exposure ($M)"] * 0.80

    fig_sens = go.Figure()
    fig_sens.add_trace(go.Scatter(
        x=primary_df["Year"], y=primary_df["Upper Bound ($M)"],
        fill=None, mode="lines", line_color="lightblue", name="Upper (±20%)"
    ))
    fig_sens.add_trace(go.Scatter(
        x=primary_df["Year"], y=primary_df["Lower Bound ($M)"],
        fill="tonexty", mode="lines", line_color="lightblue", name="Lower (±20%)"
    ))
    fig_sens.add_trace(go.Scatter(
        x=primary_df["Year"], y=primary_df["Total Exposure ($M)"],
        mode="lines+markers", line=dict(color="steelblue", width=2), name="Central"
    ))
    fig_sens.update_layout(title=f"Sensitivity Analysis — {primary} (±20% range)")
    st.plotly_chart(fig_sens, use_container_width=True)

    st.subheader("Full Projection Data")
    st.dataframe(
        df_all.style.format({
            "Physical Risk ($M)": "${:,.1f}",
            "Transition Cost ($M)": "${:,.1f}",
            "Stranded Assets ($M)": "${:,.1f}",
            "Total Exposure ($M)": "${:,.1f}",
            "Carbon Price ($/tCO2)": "${:,.0f}",
        }),
        use_container_width=True,
    )

# ── TAB 5: TCFD NARRATIVES ────────────────────────────────────────────────────
with tab5:
    st.subheader("TCFD-Aligned Scenario Narrative Templates")
    st.markdown(
        "The following narratives are auto-generated based on your inputs and selected scenarios. "
        "They are structured around the four TCFD pillars. Copy and adapt for your disclosure."
    )

    primary_sc = selected_scenarios[0]
    sc_info = SCENARIOS[primary_sc]
    worst_sc = max(selected_scenarios, key=lambda s: SCENARIOS[s]["warming"])
    best_sc  = min(selected_scenarios, key=lambda s: SCENARIOS[s]["warming"])
    df_2050_primary = df_all[(df_all["Scenario"] == primary_sc) & (df_all["Year"] == 2050)].iloc[0]

    st.markdown("---")

    # 1. GOVERNANCE
    with st.expander("🏛️ Governance", expanded=True):
        gov_text = f"""
**{company_name}** has integrated climate-related risk into its board-level governance framework.
The Board of Directors maintains oversight of climate-related risks and opportunities, with
management-level accountability assigned to the Chief Risk Officer and Chief Sustainability Officer.

Climate scenario analysis — including NGFS and IPCC pathways — is reviewed annually by the Board
Risk Committee. The analysis covers both physical and transition risks across the company's operations
in the {sector} sector and its primary operating region of {region}.

The scenarios modelled in this analysis span warming outcomes from {SCENARIOS[best_sc]['warming']}°C
({best_sc}) to {SCENARIOS[worst_sc]['warming']}°C ({worst_sc}), in alignment with TCFD
guidance on using a range of scenarios including a well-below-2°C scenario.
"""
        st.markdown(gov_text.strip())
        st.download_button("Download Governance Narrative", gov_text, file_name="tcfd_governance.txt", key="dl_gov")

    # 2. STRATEGY
    with st.expander("🗺️ Strategy", expanded=True):
        total_exp_2050 = df_2050_primary["Total Exposure ($M)"]
        strat_text = f"""
**{company_name}** has assessed the potential impact of climate scenarios on its business strategy,
financial planning, and value chain across the {sector} sector.

Under the primary scenario — **{primary_sc}** ({sc_info['warming']}°C, {sc_info['pathway']} transition)
— the company faces an estimated total climate-related financial exposure of
**${total_exp_2050:,.1f}M** by 2050, comprising:

- Physical risk exposure: **${df_2050_primary['Physical Risk ($M)']:,.1f}M** (driven by {region} regional
  hazards including flood, heat stress, water stress, and storm risk)
- Transition cost: **${df_2050_primary['Transition Cost ($M)']:,.1f}M** (including carbon pricing at
  ${sc_info['cp_2050']}/tCO2 by 2050 and market/technology disruption costs)
- Stranded asset risk: **${df_2050_primary['Stranded Assets ($M)']:,.1f}M** (of total fixed assets
  of ${fixed_assets:,.0f}M)

The company has identified the following strategic responses: accelerating emissions reduction to
limit carbon pricing exposure; diversifying revenue streams to reduce transition-sensitive revenues;
and investing in physical asset resilience in high-risk geographies.

Under a Hot House World scenario, physical risks dominate and transition risks are lower; under an
orderly Net Zero scenario, transition risks and stranded asset risk are the primary drivers.
The company's strategy is designed to be resilient across both extremes.
"""
        st.markdown(strat_text.strip())
        st.download_button("Download Strategy Narrative", strat_text, file_name="tcfd_strategy.txt", key="dl_strat")

    # 3. RISK MANAGEMENT
    with st.expander("🔍 Risk Management", expanded=True):
        risk_text = f"""
**{company_name}** identifies and assesses climate-related risks through its enterprise risk management
(ERM) framework. Climate risk has been formally integrated as a principal risk category.

**Physical Risk Identification:** Site-level exposure assessments are conducted using IPCC-aligned
climate projections for {region}. The primary physical hazards for the {sector} sector —
flood, heat stress, water stress, and storm events — are assessed against asset locations and
operational dependencies.

**Transition Risk Identification:** Policy and regulatory risks are monitored through the
carbon pricing trajectory under each modelled scenario (ranging from ${SCENARIOS[best_sc]['cp_2030']}/tCO2
to ${SCENARIOS[worst_sc]['cp_2030']}/tCO2 by 2030). Market, technology, and reputational risks are
assessed against sector-specific disruption curves.

**Risk Integration:** Climate risks are incorporated into capital allocation decisions, M&A due
diligence, asset investment appraisals, and annual budgeting processes. Scenarios are reviewed
annually and updated for material changes in policy, technology, or climate science.
"""
        st.markdown(risk_text.strip())
        st.download_button("Download Risk Management Narrative", risk_text, file_name="tcfd_risk_management.txt", key="dl_risk")

    # 4. METRICS & TARGETS
    with st.expander("📏 Metrics & Targets", expanded=True):
        carbon_intensity = (total_emissions / revenue) if revenue > 0 else 0
        metrics_text = f"""
**{company_name}** discloses the following climate-related metrics and targets in alignment with TCFD
recommendations.

**Emissions Metrics (Base Year: 2024):**
- Scope 1: **{scope1:,.0f} tCO2e/yr**
- Scope 2: **{scope2:,.0f} tCO2e/yr**
- Scope 3: **{scope3:,.0f} tCO2e/yr**
- Total GHG Emissions: **{total_emissions:,.0f} tCO2e/yr**
- Carbon Intensity: **{carbon_intensity:.2f} tCO2e per $M revenue**

**Climate-Related Financial Metrics:**
- Physical Risk Value at Risk (2050, primary scenario): **${df_2050_primary['Physical Risk ($M)']:,.1f}M**
- Transition Cost Exposure (2050, primary scenario): **${df_2050_primary['Transition Cost ($M)']:,.1f}M**
- Stranded Asset Exposure (2050, primary scenario): **${df_2050_primary['Stranded Assets ($M)']:,.1f}M**

**Scenario Assumptions:**
- Primary scenario: {primary_sc} | Carbon price 2030: ${sc_info['cp_2030']}/tCO2 | 2050: ${sc_info['cp_2050']}/tCO2
- Analysis covers {len(selected_scenarios)} scenarios from {SCENARIOS[best_sc]['warming']}°C to {SCENARIOS[worst_sc]['warming']}°C warming
- Methodology: NGFS Phase 4 / IPCC AR6 aligned hazard factors and carbon price pathways

**Targets:** [Insert company-specific net-zero targets, SBTi commitments, and reduction milestones here]
"""
        st.markdown(metrics_text.strip())
        st.download_button("Download Metrics & Targets Narrative", metrics_text, file_name="tcfd_metrics.txt", key="dl_metrics")

# ── TAB 6: EXPORT ─────────────────────────────────────────────────────────────
with tab6:
    st.subheader("Export Results")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Full Projection Data (all scenarios)**")
        csv_all = df_all.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download All Projections (CSV)",
            csv_all,
            file_name=f"{company_name.replace(' ', '_')}_climate_projections.csv",
            mime="text/csv",
        )

    with col2:
        st.markdown("**2050 Scenario Comparison Summary**")
        summary_df = df_all[df_all["Year"] == 2050][[
            "Scenario", "Warming (°C)", "Pathway",
            "Physical Risk ($M)", "Transition Cost ($M)",
            "Stranded Assets ($M)", "Total Exposure ($M)", "Carbon Price ($/tCO2)"
        ]]
        csv_summary = summary_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download 2050 Summary (CSV)",
            csv_summary,
            file_name=f"{company_name.replace(' ', '_')}_2050_summary.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.markdown("**Physical Risk Detail**")
    df_phys = df_all[["Year", "Scenario", "Physical Risk ($M)"]].copy()
    csv_phys = df_phys.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Physical Risk Data (CSV)",
        csv_phys,
        file_name=f"{company_name.replace(' ', '_')}_physical_risk.csv",
        mime="text/csv",
    )

    st.markdown("**Transition Risk Detail**")
    df_trans = df_all[["Year", "Scenario", "Transition Cost ($M)", "Carbon Price ($/tCO2)"]].copy()
    csv_trans = df_trans.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Transition Risk Data (CSV)",
        csv_trans,
        file_name=f"{company_name.replace(' ', '_')}_transition_risk.csv",
        mime="text/csv",
    )
