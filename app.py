import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Pro Business Analyzer", layout="wide")

# Custom CSS for the Results Box
st.markdown("""
    <style>
    .result-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #d1d5d8;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. Sidebar: Configuration Panel ---
st.sidebar.markdown("<b style='font-size:18px'>ANALYSIS PARAMETERS</b><hr>", unsafe_allow_html=True)

mode = st.sidebar.radio("Goal:", ["Calculate BEP Units", "Calculate Required Price"])

st.sidebar.markdown("---")
initial_investment = st.sidebar.number_input("Setup Cost ($):", value=20000.0)
target_payback_months = st.sidebar.number_input("Target Payback Period (Months):", value=12, min_value=1)
monthly_overheads = st.sidebar.number_input("Monthly Fixed Costs ($):", value=5000.0)
var_costs = st.sidebar.number_input("Var. Cost per Unit ($):", value=50.0)
marketing = st.sidebar.number_input("Monthly Marketing ($):", value=1500.0)
discount = st.sidebar.number_input("Discount (%):", value=0.0)

if mode == "Calculate BEP Units":
    price = st.sidebar.number_input("Unit Price ($):", value=150.0)
    units_sold = None
else:
    units_sold = st.sidebar.number_input("Monthly Units Sold:", value=100)
    price = None

# --- 2. Calculations ---
fixed_total = monthly_overheads + marketing
# Monthly profit needed to hit payback goal
required_monthly_profit = initial_investment / target_payback_months

if mode == "Break-Even Units":
    adj_price = price * (1 - (discount / 100))
    margin = adj_price - var_costs
    
    if margin > 0:
        bep_units = fixed_total / margin
        # Calculation for Payback Goal
        # Required Revenue = Fixed Costs + Required Profit + (Units * VarCost)
        # But we need to know the units for the revenue. 
        # Revenue = (Fixed + ReqProfit) + (Units * VarCost)
        required_monthly_revenue = fixed_total + required_monthly_profit + (( (fixed_total + required_monthly_profit)/margin ) * var_costs)
        # To simplify: The units needed to pay back in X months:
        units_for_payback = (fixed_total + required_monthly_profit) / margin
        final_revenue_goal = units_for_payback * adj_price
    else:
        bep_units = 0
        final_revenue_goal = 0
else:
    # Required price to cover fixed costs at these units
    needed_adj_price = (fixed_total / units_sold) + var_costs
    bep_price = needed_adj_price / (1 - (discount / 100))
    
    # Required price to hit Payback Goal
    price_for_payback_adj = ((fixed_total + required_monthly_profit) / units_sold) + var_costs
    final_price_goal = price_for_payback_adj / (1 - (discount / 100))
    final_revenue_goal = units_sold * price_for_payback_adj

# --- 3. Layout & Display ---
st.title("Business Intelligence Dashboard")

# Results Table in a Box
with st.container():
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    if mode == "Break-Even Units":
        res_data = {
            "Metric": ["Monthly Break-Even Units", f"Units for {target_payback_months}-Mo Payback", "Required Monthly Revenue"],
            "Value": [f"{int(bep_units)} Units", f"{int(units_for_payback)} Units", f"${final_revenue_goal:,.2f}"]
        }
    else:
        res_data = {
            "Metric": ["Monthly Break-Even Price", f"Price for {target_payback_months}-Mo Payback", "Required Monthly Revenue"],
            "Value": [f"${bep_price:.2f}", f"${final_price_goal:.2f}", f"${final_revenue_goal:,.2f}"]
        }
    
    df_res = pd.DataFrame(res_data).set_index("Metric")
    st.table(df_res)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. Professional Graph ---
st.markdown("### Profitability Projection")
fig, ax = plt.subplots(figsize=(12, 5))

if mode == "Break-Even Units":
    x = np.linspace(0, max(bep_units * 2.5, 50), 100)
    y_rev = x * adj_price
    y_cost = fixed_total + (x * var_costs)
    
    ax.plot(x, y_rev, color='#2ecc71', label='Total Revenue', lw=2.5)
    ax.plot(x, y_cost, color='#e74c3c', label='Total Costs', lw=2.5)
    ax.fill_between(x, y_rev, y_cost, where=(y_rev > y_cost), color='#2ecc71', alpha=0.1)
    ax.axvline(bep_units, color='black', linestyle='--', alpha=0.5, label='BEP Units')
    ax.axvline(units_for_payback, color='blue', linestyle=':', label=f'Goal ({target_payback_months} Mo)')
    ax.set_xlabel("Quantity")
else:
    p_range = np.linspace(var_costs * 1.1, bep_price * 2, 100)
    profit_curve = (units_sold * (p_range * (1 - (discount/100)) - var_costs)) - fixed_total
    
    ax.plot(p_range, profit_curve, color='#3498db', lw=2.5, label='Monthly Operating Profit')
    ax.axhline(0, color='black', lw=1)
    ax.axhline(required_monthly_profit, color='blue', linestyle=':', label='Required Profit for Goal')
    ax.axvline(final_price_goal, color='green', linestyle='--', label='Required Price')
    ax.set_xlabel("Unit Price ($)")

ax.set_ylabel("USD ($)")
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend()
st.pyplot(fig)
