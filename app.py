import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="BEP Profitability Calculator", layout="wide")

# --- 1. Sidebar: Configuration Panel ---
st.sidebar.header("CALCULATOR INPUTS")

# Choice between finding Units or Price
mode = st.sidebar.radio("Goal:", ["Calculate BEP Units", "Calculate Required Price"])

st.sidebar.markdown("---")
# Inputs without currency symbols
setup_cost = st.sidebar.number_input("Total Setup Cost:", value=20000.0, min_value=0.0)
fixed_costs = st.sidebar.number_input("Recurring Fixed Costs:", value=5000.0, min_value=0.0)
var_costs = st.sidebar.number_input("Variable Cost per Unit:", value=50.0, min_value=0.0)
marketing = st.sidebar.number_input("Marketing Budget:", value=1500.0, min_value=0.0)
discount = st.sidebar.number_input("Discount (%):", value=0.0, min_value=0.0, max_value=100.0)

# The total burden to be covered
total_burden = setup_cost + fixed_costs + marketing

# Mode specific logic with safety checks
if mode == "Calculate BEP Units":
    price = st.sidebar.number_input("Unit Price:", value=150.0, min_value=0.1)
    adj_price = price * (1 - (discount / 100))
    margin = adj_price - var_costs
    
    if margin > 0:
        bep_result = total_burden / margin
        required_revenue = bep_result * adj_price
    else:
        st.error("Price must be higher than Variable Cost.")
        st.stop()
else:
    units = st.sidebar.number_input("Target Units:", value=100, min_value=1)
    # Required Price = (Total Burden / Units) + Var Cost
    needed_adj_price = (total_burden / units) + var_costs
    bep_result = needed_adj_price / (1 - (discount / 100))
    required_revenue = units * needed_adj_price

# --- 2. Results Display ---
st.title("Break-Even Analysis")

# Results table without serial numbers
if mode == "Calculate BEP Units":
    data = {
        "Metric": ["Break-Even Units", "Total Revenue Required"],
        "Value": [f"{int(bep_result)} Units", f"{required_revenue:,.2f}"]
    }
else:
    data = {
        "Metric": ["Required Unit Price", "Total Revenue Required"],
        "Value": [f"{bep_result:.2f}", f"{required_revenue:,.2f}"]
    }

df_results = pd.DataFrame(data).set_index("Metric")
st.table(df_results)

# --- 3. Professional Graph ---
# Always displays and transitions smoothly
fig, ax = plt.subplots(figsize=(12, 5))
plt.style.use('dark_background')

if mode == "Calculate BEP Units":
    # Plotting Revenue vs Costs
    x = np.linspace(0, max(bep_result * 2, 50), 100)
    rev = x * adj_price
    costs = total_burden + (x * var_costs)
    
    ax.plot(x, rev, color='#2ecc71', label='Total Revenue', lw=2.5)
    ax.plot(x, costs, color='#e74c3c', label='Total Costs', lw=2.5)
    ax.fill_between(x, rev, costs, where=(rev > costs), color='#2ecc71', alpha=0.1)
    ax.axvline(bep_result, color='white', linestyle='--', alpha=0.6, label='Break-Even Point')
    ax.set_xlabel("Units Sold")
else:
    # Plotting Profit vs Price
    p_range = np.linspace(var_costs * 1.1, bep_result * 2, 100)
    profit = (units * (p_range * (1 - (discount/100)) - var_costs)) - total_burden
    
    ax.plot(p_range, profit, color='#3498db', lw=2.5, label='Profitability Curve')
    ax.axhline(0, color='white', lw=1, alpha=0.5)
    ax.axvline(bep_result, color='#2ecc71', linestyle='--', label='Required Price')
    ax.set_xlabel("Unit Price")

ax.set_ylabel("Total Value")
ax.grid(True, linestyle=':', alpha=0.3)
ax.legend()
st.pyplot(fig)
