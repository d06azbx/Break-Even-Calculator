import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Professional BEP Analyzer", layout="wide")

# Custom CSS for the Results Box
st.markdown("""
    <style>
    .result-container {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #444;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. Sidebar: Configuration Panel ---
st.sidebar.header("ANALYSIS PARAMETERS")

# Toggle between Unit or Price mode
mode = st.sidebar.radio("Analysis Goal:", ["Calculate BEP Units", "Calculate Required Price"])

st.sidebar.markdown("---")
# Core inputs based on your business logic
setup_cost = st.sidebar.number_input("Setup Cost ($):", value=20000.0, min_value=0.0)
monthly_fixed = st.sidebar.number_input("Monthly Fixed Costs ($):", value=5000.0, min_value=0.0)
var_costs = st.sidebar.number_input("Var. Cost per Unit ($):", value=50.0, min_value=0.0)
marketing = st.sidebar.number_input("Monthly Marketing ($):", value=1500.0, min_value=0.0)
discount = st.sidebar.number_input("Discount (%):", value=0.0, min_value=0.0, max_value=100.0)

# Total Monthly Fixed expenses (Fixed + Marketing)
total_fixed_monthly = monthly_fixed + marketing

# Mode specific inputs with safety checks
if mode == "Calculate BEP Units":
    price = st.sidebar.number_input("Unit Price ($):", value=150.0, min_value=0.1)
    adj_price = price * (1 - (discount / 100))
    margin = adj_price - var_costs
    
    if margin > 0:
        bep_units = total_fixed_monthly / margin
        required_revenue = bep_units * adj_price
    else:
        st.error("Price is too low to cover variable costs!")
        st.stop()
else:
    # Set min_value to 1 to prevent division by zero error
    units_sold = st.sidebar.number_input("Monthly Units Sold:", value=100, min_value=1)
    
    # Logic for Price
    bep_adj_price = (total_fixed_monthly / units_sold) + var_costs
    bep_price = bep_adj_price / (1 - (discount / 100))
    required_revenue = units_sold * bep_adj_price

# --- 2. Results Display ---
st.title("Business Intelligence Dashboard")

with st.container():
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.subheader("Key Simulation Results")
    
    if mode == "Calculate BEP Units":
        data = {
            "Metric": ["Break-Even Point (Units)", "Monthly Contribution Margin", "Total Monthly Fixed Costs", "Required Monthly Revenue"],
            "Value": [f"{int(bep_units)} Units/Mo", f"${margin:,.2f}", f"${total_fixed_monthly:,.2f}", f"${required_revenue:,.2f}"]
        }
    else:
        data = {
            "Metric": ["Break-Even Price", "Required Revenue per Month", "Total Monthly Fixed Costs"],
            "Value": [f"${bep_price:,.2f}", f"${required_revenue:,.2f}", f"${total_fixed_monthly:,.2f}"]
        }
    
    # Convert to DataFrame and remove serial numbers (index)
    df_results = pd.DataFrame(data).set_index("Metric")
    st.table(df_results)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. Professional Graph ---
# Graph remains visible and transitions smoothly
fig, ax = plt.subplots(figsize=(12, 5))
plt.style.use('dark_background')

if mode == "Calculate BEP Units":
    # Break-Even Chart
    x = np.linspace(0, max(bep_units * 2, 50), 100)
    rev = x * adj_price
    costs = total_fixed_monthly + (x * var_costs)
    
    ax.plot(x, rev, color='#2ecc71', label='Revenue', lw=2.5)
    ax.plot(x, costs, color='#e74c3c', label='Costs', lw=2.5)
    ax.fill_between(x, rev, costs, where=(rev > costs), color='#2ecc71', alpha=0.1)
    ax.axvline(bep_units, color='white', linestyle='--', alpha=0.6, label='Break-Even Point')
    ax.set_xlabel("Units Sold")
else:
    # Price Sensitivity Chart
    p_range = np.linspace(var_costs * 1.1, bep_price * 2, 100)
    profit = (units_sold * (p_range * (1 - (discount/100)) - var_costs)) - total_fixed_monthly
    
    ax.plot(p_range, profit, color='#3498db', lw=2.5, label='Monthly Operating Profit')
    ax.axhline(0, color='white', lw=1, alpha=0.5)
    ax.axvline(bep_price, color='#2ecc71', linestyle='--', label='Required Price')
    ax.set_xlabel("Unit Price ($)")

ax.set_ylabel("USD ($)")
ax.grid(True, linestyle=':', alpha=0.3)
ax.legend()
st.pyplot(fig)
