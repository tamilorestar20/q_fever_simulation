# Q Fever SEIRV Simulation Dashboard 🐐🐑

This project simulates the spread and control of **Coxiella burnetii (Q Fever)** among small ruminants in Northern Nigeria using a compartmental **SEIRV (Susceptible–Exposed–Infected–Recovered–Vaccinated)** model.

Built with [Streamlit](https://streamlit.io), the app allows users to explore different disease control scenarios and visualize infection dynamics over time based on real epidemiological data.

---

## 🔬 Features

- 📊 Region and species-based simulations using actual seroprevalence data
- 🎛️ Adjustable model parameters: infection rate, recovery, progression, vaccination
- 🧪 Live SEIRV curves updated in real-time
- 📁 Upload your dataset
- 📥 Download simulated results as CSV
- 📝 Summary metrics (peak infection, total recovered, etc.)

---

## 🗂️ Files

- `app.py` – Streamlit web application
- `cleaned_q_fever_dataset.csv` – Real-world cleaned dataset used for modeling
- `requirements.txt` – List of Python packages required for deployment

---

## 🚀 How to Run Locally

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/q_fever_simulation.git
cd q_fever_simulation

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
