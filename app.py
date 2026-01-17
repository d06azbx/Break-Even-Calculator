import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Page Configuration
st.set_page_config(page_title="Break-Even Simulator", layout="wide")
st.title("Business Break-Even Simulation")

# --- SIDEBAR: COMMAND PANEL ---
# These inputs match the variables found in your Jupyter Notebook
st.sidebar.header("COMMAND PANEL")
startup_cost = st.sidebar.number_input("Startup Cost ($)", value=20000.0, step=1000.0)
monthly_overheads = st.sidebar.number_input("Monthly Overheads ($)", value=5000.0, step=500.0)
unit_price = st.sidebar.number_input("Unit Price ($)", value=150.0, step=10.0)
var_cost = st.sidebar.number_input("Variable Cost per Unit ($)", value=50.0, step=5.0)
monthly_sales_target = st.sidebar.number_input("Target Monthly Sales (Units)", value=100)

# Additional parameters from your notebook
discount = st.sidebar.number_input("Discount (%)", value=0.0) / 100
marketing_spend = st.sidebar.number_input("Marketing Spend ($)", value=1500.0)

# --- CALCULATIONS ---
# Logic derived from your Break-Even simulation
effective_price = unit_price * (1 - discount)
unit_margin = effective_price - var_cost
total_fixed_costs = startup_cost + monthly_overheads + marketing_spend

if st.sidebar.button("RUN DETAILED SIMULATION"):
    if unit_margin > 0:
        # Calculate Break-Even Point
        be_units = total_fixed_costs / unit_margin
        
        # Display Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Break-Even Units", f"{be_units:.2f}")
        col2.metric("Unit Margin", f"${unit_margin:.2f}")
        col3.metric("Fixed Costs", f"${total_fixed_costs:,.2f}")

        # --- VISUALIZATION ---
        # Creating a range for the X-axis (Units)
        max_x = int(max(be_units * 1.5, monthly_sales_target * 1.5))
        x = np.linspace(0, max_x, 100)
        
        revenue = x * effective_price
        total_costs = total_fixed_costs + (x * var_cost)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(x, revenue, label="Total Revenue", color="#2ecc71", lw=2)
        ax.plot(x, total_costs, label="Total Costs", color="#e74c3c", lw=2)
        ax.axvline(be_units, color='gray', linestyle='--', label="Break-Even Point")
        
        ax.set_title("Break-Even Analysis Chart")
        ax.set_xlabel("Units Sold")
        ax.set_ylabel("Currency ($)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
    else:
        st.error("Error: Unit Margin is zero or negative. Increase your price or lower variable costs.")
else:
    st.info("Adjust the parameters in the sidebar and click 'Run Detailed Simulation'.")