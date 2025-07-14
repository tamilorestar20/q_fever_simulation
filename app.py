import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd
import io

st.set_page_config(
    page_title="Q Fever Simulation",
    page_icon="🐐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .main { background-color: #f8f4ff; }
        h1, h2, h3 { color: #5e17eb; }
        .stButton>button, .stDownloadButton>button { background-color: #5e17eb; color: white; border-radius: 8px; }
        .stSidebar { background-color: #e6ddff; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Function to simulate SEIRV model with extended parameters
# -------------------------------
def simulate_seirv(
    population,
    initial_infected,
    beta,
    sigma,
    gamma,
    mortality_rate,
    vaccination_rate,
    diagnostic_rate,
    tick_prevalence,
    time_steps=52
):
    S, E, I, R, V, D = population - initial_infected, 0, initial_infected, 0, 0, 0
    hist = {"S": [], "E": [], "I": [], "R": [], "V": [], "D": []}

    for _ in range(time_steps):
        effective_beta = beta * tick_prevalence
        new_infected = effective_beta * S * I / population
        new_exposed = sigma * E
        new_recovered = gamma * I * diagnostic_rate
        new_mortality = mortality_rate * I * (1 - diagnostic_rate)
        new_vaccinated = vaccination_rate * S

        S -= new_infected + new_vaccinated
        E += new_infected - new_exposed
        I += new_exposed - new_recovered - new_mortality
        R += new_recovered
        V += new_vaccinated
        D += new_mortality

        hist["S"].append(S)
        hist["E"].append(E)
        hist["I"].append(I)
        hist["R"].append(R)
        hist["V"].append(V)
        hist["D"].append(D)

    return hist

# -------------------------------
# Load Data
# -------------------------------
st.title("🐐 Q Fever SEIRV Simulation Dashboard")

uploaded_file = st.sidebar.file_uploader("Upload your dataset (CSV)", type=["csv"])
uploaded_map = st.sidebar.file_uploader("Upload GeoJSON or Shapefile (ZIP)", type=["geojson", "zip"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.success("Dataset uploaded successfully!")
    st.write("### Preview of Uploaded Dataset")
    st.dataframe(df.head())

    st.sidebar.header("Simulation Settings")
    regions = sorted(df["region"].dropna().unique())
    selected_region = st.sidebar.selectbox("Select Region", regions)
    filtered_region = df[df["region"] == selected_region]
    species_list = sorted(filtered_region["species"].dropna().unique())
    selected_species = st.sidebar.selectbox("Select Species", species_list)

    filtered_data = filtered_region[filtered_region["species"] == selected_species]
    total_examined = filtered_data["number_examined"].sum()
    total_positive = filtered_data["number_positive"].sum()
    prevalence = total_positive / total_examined if total_examined > 0 else 0

    population = st.sidebar.slider("Simulated Population", 100, 5000, 1000, step=100)
    initial_infected = int(prevalence * population)
    st.sidebar.markdown(f"**Estimated Prevalence**: {prevalence:.2%} → Initial Infected: {initial_infected}")

    beta = st.sidebar.slider("Infection Rate (β)", 0.05, 0.5, 0.3)
    sigma = st.sidebar.slider("Progression Rate (σ)", 0.1, 0.5, 0.2)
    gamma = st.sidebar.slider("Recovery Rate (γ)", 0.05, 0.3, 0.1)
    mortality_rate = st.sidebar.slider("Mortality Rate (μ)", 0.0, 0.1, 0.01)
    vaccination_rate = st.sidebar.slider("Vaccination Rate (ϕ)", 0.0, 0.1, 0.01)
    diagnostic_rate = st.sidebar.slider("Diagnostic Rate (δ)", 0.0, 1.0, 0.7)
    tick_prevalence = st.sidebar.slider("Tick Prevalence (γ_tick)", 0.5, 2.0, 1.0)

    compare = st.sidebar.checkbox("Enable Scenario Comparison")

    # Single or Multiple Scenario
    scenarios = {
        "Current": simulate_seirv(population, initial_infected, beta, sigma, gamma, mortality_rate, vaccination_rate, diagnostic_rate, tick_prevalence)
    }

    if compare:
        scenarios["Tick Control"] = simulate_seirv(population, initial_infected, beta * 0.5, sigma, gamma, mortality_rate, vaccination_rate, diagnostic_rate, tick_prevalence * 0.8)
        scenarios["Vaccination Boost"] = simulate_seirv(population, initial_infected, beta, sigma, gamma, mortality_rate, vaccination_rate + 0.02, diagnostic_rate, tick_prevalence)

    st.subheader(f"📈 SEIRV Curve for {selected_region} – {selected_species}")
    weeks = list(range(52))
    fig, ax = plt.subplots(figsize=(10, 6))
    for label, res in scenarios.items():
        ax.plot(weeks, res["I"], label=f"Infected - {label}")
    ax.set_xlabel("Weeks")
    ax.set_ylabel("Population")
    ax.set_title("Infection Curve Comparison")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("📝 Simulation Summary (Main Scenario)")
    main = scenarios["Current"]
    st.markdown(f"- **Peak Infected:** {int(max(main['I']))}")
    st.markdown(f"- **Total Recovered:** {int(main['R'][-1])}")
    st.markdown(f"- **Total Vaccinated:** {int(main['V'][-1])}")
    st.markdown(f"- **Total Deaths:** {int(main['D'][-1])}")

    export_df = pd.DataFrame(main)
    csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Main Scenario as CSV", data=csv, file_name="main_simulation.csv", mime="text/csv")

    if uploaded_map is not None:
        try:
            if uploaded_map.name.endswith(".geojson"):
                geo_df = gpd.read_file(uploaded_map)
            elif uploaded_map.name.endswith(".zip"):
                geo_df = gpd.read_file(f"zip://{uploaded_map.name}")
            st.subheader("🗺️ QGIS-Based Regional Overlay")
            fig_map = px.choropleth(geo_df, geojson=geo_df.geometry, locations=geo_df.index, color=geo_df.columns[1], title="Map Visualization")
            fig_map.update_geos(fitbounds="locations", visible=False)
            st.plotly_chart(fig_map, use_container_width=True)
        except Exception as e:
            st.error(f"Map loading failed: {e}")
else:
    st.warning("Please upload a dataset in CSV format containing columns: region, species, number_examined, number_positive, etc.")
