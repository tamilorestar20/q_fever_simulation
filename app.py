
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# Function to simulate SEIRV model
# -------------------------------
def simulate_seirv(population, initial_infected, beta, sigma, gamma, vaccination_rate, time_steps=52):
    S, E, I, R, V = population - initial_infected, 0, initial_infected, 0, 0
    hist = {"S": [], "E": [], "I": [], "R": [], "V": []}

    for _ in range(time_steps):
        new_infected = beta * S * I / population
        new_exposed = sigma * E
        new_recovered = gamma * I
        new_vaccinated = vaccination_rate * S

        S -= new_infected + new_vaccinated
        E += new_infected - new_exposed
        I += new_exposed - new_recovered
        R += new_recovered
        V += new_vaccinated

        hist["S"].append(S)
        hist["E"].append(E)
        hist["I"].append(I)
        hist["R"].append(R)
        hist["V"].append(V)

    return hist

# -------------------------------
# Load Data
# -------------------------------
st.title("Q Fever SEIRV Simulation Dashboard 🐐🐑")

df = pd.read_csv("cleaned_q_fever_dataset.csv")

# Sidebar Filters
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

# Simulation Parameters
population = st.sidebar.slider("Simulated Population", 100, 5000, 1000, step=100)
initial_infected = int(prevalence * population)
st.sidebar.markdown(f"**Estimated Prevalence**: {prevalence:.2%} → Initial Infected: {initial_infected}")

beta = st.sidebar.slider("Infection Rate (β)", 0.05, 0.5, 0.3)
sigma = st.sidebar.slider("Progression Rate (σ)", 0.1, 0.5, 0.2)
gamma = st.sidebar.slider("Recovery Rate (γ)", 0.05, 0.3, 0.1)
vaccination_rate = st.sidebar.slider("Vaccination Rate (ϕ)", 0.0, 0.1, 0.01)

# Run Simulation
result = simulate_seirv(
    population=population,
    initial_infected=initial_infected,
    beta=beta,
    sigma=sigma,
    gamma=gamma,
    vaccination_rate=vaccination_rate,
    time_steps=52
)

# Plotting Results
st.subheader(f"SEIRV Curve for {selected_region} – {selected_species}")

weeks = list(range(52))
plt.figure(figsize=(10, 6))
plt.plot(weeks, result["S"], label="Susceptible")
plt.plot(weeks, result["E"], label="Exposed")
plt.plot(weeks, result["I"], label="Infected")
plt.plot(weeks, result["R"], label="Recovered")
plt.plot(weeks, result["V"], label="Vaccinated")
plt.xlabel("Weeks")
plt.ylabel("Population")
plt.title("SEIRV Model Simulation Over 1 Year")
plt.legend()
plt.grid(True)
st.pyplot(plt)
