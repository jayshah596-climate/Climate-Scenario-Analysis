import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🌍 Company-Level Climate Scenario Analysis Dashboard")

# Sidebar Inputs
st.sidebar.header("Input Parameters")
company_name = st.sidebar.text_input("Company Name", "Example Corp")
sector = st.sidebar.selectbox("Select Sector", ["Energy", "Manufacturing", "Real Estate", "Finance"])
region = st.sidebar.selectbox("Select Region", ["Europe", "Asia", "North America", "Africa"])

scope1 = st.sidebar.number_input("Scope 1 Emissions (tCO2e)", min_value=0.0, value=5000.0)
scope2 = st.sidebar.number_input("Scope 2 Emissions (tCO2e)", min_value=0.0, value=7000.0)
scope3 = st.sidebar.number_input("Scope 3 Emissions (tCO2e)", min_value=0.0, value=13000.0)
total_emissions = scope1 + scope2 + scope3

ssp_scenario = st.sidebar.selectbox("Select SSP Scenario", ["SSP1-2.6", "SSP2-4.5", "SSP5-8.5"])

st.markdown(f"### Company: `{company_name}`")
st.markdown(f"**Sector:** {sector} | **Region:** {region} | **Scenario:** {ssp_scenario}")
st.metric("Total GHG Emissions (tCO2e)", f"{total_emissions:,.0f}")

# Hazard factors by sector and scenario (simplified dummy multipliers)
hazard_factors = {
    "Energy": {
        "SSP1-2.6": 0.01,
        "SSP2-4.5": 0.03,
        "SSP5-8.5": 0.07
    },
    "Manufacturing": {
        "SSP1-2.6": 0.015,
        "SSP2-4.5": 0.04,
        "SSP5-8.5": 0.08
    },
    "Real Estate": {
        "SSP1-2.6": 0.02,
        "SSP2-4.5": 0.06,
        "SSP5-8.5": 0.10
    },
    "Finance": {
        "SSP1-2.6": 0.005,
        "SSP2-4.5": 0.015,
        "SSP5-8.5": 0.04
    }
}

# Value at Risk Calculation (basic)
def calculate_var(emissions, multiplier):
    return emissions * multiplier * 100  # Simplified assumption: $100 per tCO2e exposure

years = [2025, 2030, 2050]
data = []

for year in years:
    multiplier = hazard_factors[sector][ssp_scenario] * ((year - 2020) / 5)  # Increase with time
    var = calculate_var(total_emissions, multiplier)
    data.append({"Year": year, "Hazard Multiplier": multiplier, "Value at Risk ($)": var})

results_df = pd.DataFrame(data)
st.subheader("📉 Climate-Adjusted Value at Risk")
st.dataframe(results_df.style.format({"Value at Risk ($)": "${:,.0f}", "Hazard Multiplier": "{:.3f}"}))

fig = px.line(results_df, x="Year", y="Value at Risk ($)", title="Projected Climate Value at Risk")
st.plotly_chart(fig, use_container_width=True)

# Download button
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')
csv = convert_df(results_df)
st.download_button("📥 Download Risk Projection", csv, "risk_projection.csv", "text/csv")

