import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Business Intelligence Simulator", layout="wide")

# --- 1. Sidebar (The Command Panel) ---
st.sidebar.markdown("<b style='font-size:18px'>COMMAND PANEL</b><hr>", unsafe_allow_html=True)

initial_investment = st.sidebar.number_input("Startup Cost ($):", value=20000.0)
fixed_costs = st.sidebar.number_input("Monthly Overheads ($):", value=5000.0)
price = st.sidebar.number_input("Unit Price ($):", value=150.0)
var_costs = st.sidebar.number_input("Var. Cost/Unit ($):", value=50.0)
monthly_sales = st.sidebar.number_input("Monthly Sales:", value=100)
discount = st.sidebar.number_input("Discount (%):", value=0.0)
mkt_budget = st.sidebar.number_input("Marketing ($):", value=1500.0)

# The "Run Simulation" Button
run_sim = st.sidebar.button("RUN DETAILED SIMULATION", type="primary", use_container_width=True)

# --- 2. Calculations & Logic ---
total_fc = fixed_costs + mkt_budget
adj_p = price * (1 - (discount / 100))
unit_margin = adj_p - var_costs

if adj_p <= var_costs:
    st.error("⚠️ Error: Adjusted Price must be higher than Variable Cost.")
else:
    be_units = total_fc / unit_margin
    monthly_profit = (monthly_sales * unit_margin) - total_fc

    st.title("Business Viability Dashboard")

    # --- 3. Visuals (The Charts) ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    plt.rcParams.update({'font.size': 10})

    # --- Chart 1: Detailed Break-Even Analysis ---
    upper_limit = max(be_units * 2, monthly_sales * 1.5, 50)
    x_units = np.linspace(0, upper_limit, 100)
    y_rev = x_units * adj_p
    y_cost = total_fc + (x_units * var_costs)

    ax1.plot(x_units, y_rev, color='#2ecc71', label='Total Revenue', lw=3)
    ax1.plot(x_units, y_cost, color='#e74c3c', label='Total Costs', lw=3)
    ax1.fill_between(x_units, y_rev, y_cost, where=(y_rev > y_cost), color='#2ecc71', alpha=0.15, label='Profit Zone')
    ax1.fill_between(x_units, y_rev, y_cost, where=(y_rev < y_cost), color='#e74c3c', alpha=0.10, label='Loss Zone')

    # Intersection Marker
    ax1.scatter(be_units, be_units * adj_p, color='black', s=100, zorder=5)
    ax1.annotate(f'Break-even Point\n{int(be_units)} Units', xy=(be_units, be_units * adj_p),
                 xytext=(be_units*0.5, (be_units * adj_p)*1.5), arrowprops=dict(arrowstyle='->', lw=1.5))

    ax1.set_title("Unit Profitability & Margin Analysis", fontsize=14, pad=15)
    ax1.set_xlabel("Units Sold Per Month")
    ax1.set_ylabel("USD ($)")
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper left')

    # --- Chart 2: Cumulative Cash Flow Timeline ---
    months = np.arange(0, 25)
    cumulative_cf = -initial_investment + (monthly_profit * months)

    ax2.plot(months, cumulative_cf, color='#3498db', lw=3, label='Cumulative Cash Flow')
    ax2.axhline(0, color='black', lw=1.5)

    if monthly_profit > 0:
        pb_month = initial_investment / monthly_profit
        if pb_month <= 24:
            ax2.scatter(pb_month, 0, color='orange', s=120, zorder=6, label='Payback Point')
            ax2.annotate(f'Payback: Month {pb_month:.1f}', xy=(pb_month, 0), xytext=(pb_month+1, initial_investment*0.2),
                         arrowprops=dict(arrowstyle='->'))

    ax2.fill_between(months, 0, cumulative_cf, where=(cumulative_cf > 0), color='#2ecc71', alpha=0.1)
    ax2.fill_between(months, 0, cumulative_cf, where=(cumulative_cf < 0), color='#e74c3c', alpha=0.1)

    ax2.set_title("24-Month Investment Payback Path", fontsize=14, pad=15)
    ax2.set_xlabel("Months in Operation")
    ax2.set_ylabel("Net Position ($)")
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper left')

    plt.tight_layout()
    st.pyplot(fig)

    # --- 4. Table Output (Serial Numbers/Index Removed) ---
    st.markdown("### Key Business Metrics")
    pb_status = f"{initial_investment / monthly_profit:.1f} Months" if monthly_profit > 0 else "Never"
    
    metrics_data = {
        "Metric": ["Break-even Point (Units)", "Monthly Contribution Margin", "Monthly Net Profit", "Payback Period", "Total Monthly Fixed Costs"],
        "Value": [f"{int(be_units)} units", f"${unit_margin:,.2f}", f"${monthly_profit:,.2f}", pb_status, f"${total_fc:,.2f}"]
    }
    
    # We set 'Metric' as the index to remove the 0, 1, 2, 3 serial numbers
    df_metrics = pd.DataFrame(metrics_data).set_index("Metric")
    st.table(df_metrics)
