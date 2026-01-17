import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="BEP Analyzer", layout="wide")

# --- 1. Sidebar: Command Panel ---
st.sidebar.markdown("<b style='font-size:18px'>COMMAND PANEL</b><hr>", unsafe_allow_html=True)

# User selects the mode
mode = st.sidebar.radio("Analysis Goal:", ["Calculate BEP Units", "Calculate Required Price"])

initial_investment = st.sidebar.number_input("Startup Cost ($):", value=20000.0)
monthly_overheads = st.sidebar.number_input("Monthly Overheads ($):", value=5000.0)
var_costs = st.sidebar.number_input("Var. Cost/Unit ($):", value=50.0)
discount = st.sidebar.number_input("Discount (%):", value=0.0)
mkt_budget = st.sidebar.number_input("Marketing ($):", value=1500.0)
target_revenue = st.sidebar.number_input("Expected Monthly Revenue ($):", value=12000.0)

# Conditional Inputs based on Mode
if mode == "Calculate BEP Units":
    price = st.sidebar.number_input("Unit Price ($):", value=150.0)
    target_units = None
else:
    target_units = st.sidebar.number_input("Target Monthly Unit Sales:", value=100)
    price = None

run_sim = st.sidebar.button("RUN SIMULATION", type="primary", use_container_width=True)

# --- 2. Logic & Calculations ---
total_fixed_monthly = monthly_overheads + mkt_budget

if run_sim:
    st.title("Results")
    
    if mode == "Calculate BEP Units":
        adj_p = price * (1 - (discount / 100))
        unit_margin = adj_p - var_costs
        
        if unit_margin <= 0:
            st.error("Price is lower than Variable Cost.")
        else:
            # Result 1: BEP Units
            be_result = total_fixed_monthly / unit_margin
            
            # Result 2: Months to Break-even (Payback of Startup Cost)
            # Monthly Profit = Monthly Revenue - (Units Sold * Var Cost) - Fixed Costs
            # We estimate units sold based on Revenue / Adj_Price
            est_units_sold = target_revenue / adj_p
            monthly_profit = target_revenue - (est_units_sold * var_costs) - total_fixed_monthly
            
            months_to_be = initial_investment / monthly_profit if monthly_profit > 0 else float('inf')

            # Displaying only the answers
            st.success(f"**Break-Even Point:** {int(be_result)} Units/Month")
            st.success(f"**Months to Recover Startup Cost:** {months_to_be:.1f} Months")

            # --- Professional Graph ---
            upper_limit = int(be_result * 2)
            x = np.linspace(0, upper_limit, 100)
            y_rev = x * adj_p
            y_cost = total_fixed_monthly + (x * var_costs)

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(x, y_rev, color='#2ecc71', label='Revenue', lw=3)
            ax.plot(x, y_cost, color='#e74c3c', label='Total Costs', lw=3)
            ax.fill_between(x, y_rev, y_cost, where=(y_rev > y_cost), color='#2ecc71', alpha=0.15)
            ax.fill_between(x, y_rev, y_cost, where=(y_rev < y_cost), color='#e74c3c', alpha=0.10)
            ax.scatter(be_result, be_result * adj_p, color='black', zorder=5)
            ax.set_title("BEP Units Analysis")
            ax.set_xlabel("Units Sold")
            ax.set_ylabel("USD ($)")
            ax.legend()
            st.pyplot(fig)

    else:  # Calculate Required Price
        # Total Revenue needed to cover costs: (Units * Price) = (Units * VarCost) + FixedCosts
        # Price = (FixedCosts / Units) + VarCost
        needed_adj_price = (total_fixed_monthly / target_units) + var_costs
        raw_price = needed_adj_price / (1 - (discount / 100))
        
        # Months to Break-even
        monthly_profit = target_revenue - (target_units * var_costs) - total_fixed_monthly
        months_to_be = initial_investment / monthly_profit if monthly_profit > 0 else float('inf')

        st.success(f"**Required Unit Price:** ${raw_price:.2f}")
        st.success(f"**Months to Recover Startup Cost:** {months_to_be:.1f} Months")

        # --- Professional Graph ---
        p_range = np.linspace(var_costs * 1.1, raw_price * 2, 100)
        # Profit vs Price at target units
        profit_at_prices = (target_units * (p_range * (1-(discount/100)) - var_costs)) - total_fixed_monthly
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(p_range, profit_at_prices, color='#3498db', lw=3, label='Monthly Profit')
        ax.axhline(0, color='black', lw=1)
        ax.axvline(raw_price, color='red', linestyle='--', label=f'BEP Price: ${raw_price:.2f}')
        ax.set_title("Profitability vs. Unit Price")
        ax.set_xlabel("Unit Price ($)")
        ax.set_ylabel("Monthly Profit ($)")
        ax.legend()
        st.pyplot(fig)
