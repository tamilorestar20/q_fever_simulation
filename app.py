
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
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

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🏠 Welcome", "📁 Upload Data", "📊 Simulation"])

# Welcome Page
if page == "🏠 Welcome":
    st.markdown("""
        # 🧬 Q Fever SEIRV Simulation Tool

        Welcome to the interactive modeling platform for understanding and predicting the spread of **Coxiella burnetii** (Q Fever) among small ruminants in Nigeria.

        This tool allows you to:
        - Upload real-world prevalence data (CSV or Excel)
        - Simulate disease dynamics with adjustable parameters
        - Explore intervention impacts and download results

        Click **Next →** on the sidebar to begin!
    """)
    
# Upload Page
elif page == "📁 Upload Data":
    st.header("📁 Upload Your Dataset")
    uploaded_file = st.file_uploader("Upload your dataset (CSV or Excel)", type=["csv", "xlsx"])
    df = None
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("Dataset uploaded successfully!")
        st.write("### Preview of Uploaded Dataset")
        st.dataframe(df.head())
        st.session_state["df"] = df
    else:
        st.info("Upload a dataset containing region, species, number_examined, number_positive, etc.")

# Simulation Page
elif page == "📊 Simulation":
    df = st.session_state.get("df")
    if df is not None:
        st.title("📊 Run SEIRV Simulation")

        regions = sorted(df["region"].dropna().unique())
        selected_region = st.selectbox("Select Region", regions)
        filtered_region = df[df["region"] == selected_region]
        species_list = sorted(filtered_region["species"].dropna().unique())
        selected_species = st.selectbox("Select Species", species_list)

        filtered_data = filtered_region[filtered_region["species"] == selected_species]
        total_examined = filtered_data["number_examined"].sum()
        total_positive = filtered_data["number_positive"].sum()
        prevalence = total_positive / total_examined if total_examined > 0 else 0

        population = st.slider("Simulated Population", 100, 5000, 1000, step=100)
        initial_infected = int(prevalence * population)
        st.markdown(f"**Estimated Prevalence**: {prevalence:.2%} → Initial Infected: {initial_infected}")

        beta = st.slider("Infection Rate (β)", 0.05, 0.5, 0.3)
        sigma = st.slider("Progression Rate (σ)", 0.1, 0.5, 0.2)
        gamma = st.slider("Recovery Rate (γ)", 0.05, 0.3, 0.1)
        mortality_rate = st.slider("Mortality Rate (μ)", 0.0, 0.1, 0.01)
        vaccination_rate = st.slider("Vaccination Rate (ϕ)", 0.0, 0.1, 0.01)
        diagnostic_rate = st.slider("Diagnostic Rate (δ)", 0.0, 1.0, 0.7)
        tick_prevalence = st.slider("Tick Prevalence (γ_tick)", 0.5, 2.0, 1.0)
        compare = st.checkbox("Enable Scenario Comparison")

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

        # Save chart as PNG for download
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        st.download_button(
            label="📥 Download Infection Curve",
            data=buf.getvalue(),
            file_name=f"{selected_region}_{selected_species}_infection_curve.png",
            mime="image/png"
        )

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

        st.markdown("---")
        st.subheader("🌍 Regional Prevalence Map")
        region_summary = df.groupby("region")[["number_examined", "number_positive"]].sum().reset_index()
        region_summary["prevalence"] = region_summary["number_positive"] / region_summary["number_examined"]
        fig_map = px.bar(region_summary, x="region", y="prevalence", color="prevalence", title="Estimated Q Fever Prevalence by Region")
        st.plotly_chart(fig_map, use_container_width=True)

        # Save map chart as PNG for download
        fig_map.write_image("/tmp/prevalence_chart.png", format="png")
        with open("/tmp/prevalence_chart.png", "rb") as img_file:
            st.download_button(
                label="📥 Download Regional Prevalence Chart",
                data=img_file,
                file_name="regional_prevalence_chart.png",
                mime="image/png"
            )

    else:
        st.warning("Please upload a dataset first from the 📁 Upload Data section.")
