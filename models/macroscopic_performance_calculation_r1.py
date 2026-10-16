import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="EIS Macroscopic Metrics Calculator", layout="wide")
st.title("🔋 EIS to Macroscopic Performance Calculator")
st.markdown("This app calculates effective capacitance, internal resistance, energy density, and maximum power density from Electrochemical Impedance Spectroscopy (EIS) parameters.")

# --- Equations Display ---
with st.expander("📖 View Governing Equations"):
    st.latex(r"C_{\mathrm{eff}} = Q^{1/\alpha} \left(\frac{1}{R_s}+\frac{1}{R_{ct}}\right)^{(1-\alpha)/\alpha}")
    st.latex(r"R_{\mathrm{int}} = R_s + R_{ct}")
    st.latex(r"E = \frac{1}{2X}C_{\mathrm{eff}}V^2 \quad \text{(in J/kg or J/L)}")
    st.latex(r"P_{\max} = \frac{V^2}{4(R_s+R_{ct})X} \quad \text{(in W/kg or W/L)}")
    st.markdown("**Where:**\n- $X$ is the normalizing factor (Mass in kg or Volume in L)\n- $V$ is the operating voltage (V)")

# --- Sidebar Inputs ---
st.sidebar.header("Input Parameters")
st.sidebar.subheader("EIS Parameters (Randles-CPE)")

# Using min_value to prevent math domain errors (e.g., division by zero)
# Format="%.2e" allows scientific notation input
Q = st.sidebar.number_input("Q (Pseudo-capacitance, F·s^(α-1))", value=1.5e-4, format="%.2e", min_value=1e-12, step=1e-5)
alpha = st.sidebar.number_input("α (Non-ideality factor)", value=0.85, min_value=0.01, max_value=1.0, step=0.01)
Rs = st.sidebar.number_input("Rs (Series resistance, Ω)", value=0.05, min_value=1e-12, format="%.4f", step=0.01)
Rct = st.sidebar.number_input("Rct (Charge-transfer resistance, Ω)", value=0.50, min_value=1e-12, format="%.4f", step=0.01)

st.sidebar.subheader("Device & Operating Parameters")
V = st.sidebar.number_input("V (Operating voltage, V)", value=3.7, min_value=0.0, step=0.1)
X = st.sidebar.number_input("X (Mass or Volume, kg or L)", value=0.05, min_value=1e-12, format="%.4f", step=0.01)

unit_x = "kg" if X < 1 else "L" # Simple heuristic for label, user understands their own X

# --- Calculations ---
try:
    # 1. Effective Capacitance
    sum_reciprocal_R = (1 / Rs) + (1 / Rct)
    Ceff = (Q ** (1 / alpha)) * (sum_reciprocal_R ** ((1 - alpha) / alpha))
    
    # 2. Internal Resistance
    Rint = Rs + Rct
    
    # 3. Energy Density (J/kg or J/L)
    E_joules = (1 / (2 * X)) * Ceff * (V ** 2)
    E_watt_hours = E_joules / 3600.0  # Convert J to Wh
    
    # 4. Max Power Density (W/kg or W/L)
    Pmax = (V ** 2) / (4 * Rint * X)

    # --- Display Results ---
    st.subheader("Computed Macroscopic Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Effective Capacitance ($C_{eff}$)", 
            value=f"{Ceff:.4e} F",
            delta="Derived from Brug's relation"
        )
        st.metric(
            label="Total Internal Resistance ($R_{int}$)", 
            value=f"{Rint:.4f} Ω"
        )
        
    with col2:
        st.metric(
            label="Energy Density ($E$)", 
            value=f"{E_watt_hours:.2f} Wh/{unit_x}",
            delta=f"({E_joules:.2f} J/{unit_x})"
        )
        st.metric(
            label="Maximum Power Density ($P_{max}$)", 
            value=f"{Pmax:.2f} W/{unit_x}"
        )

    # --- Detailed Breakdown ---
    with st.expander("🔍 Calculation Breakdown"):
        st.markdown("**Step 1: CPE Conversion to Effective Capacitance**")
        st.write(f"Sum of reciprocal resistances: (1/Rs + 1/Rct) = {sum_reciprocal_R:.4f} Ω⁻¹")
        st.write(f"Q^(1/α) = {Q**(1/alpha):.4e}")
        st.write(f"(1/Rs + 1/Rct)^((1-α)/α) = {sum_reciprocal_R**((1-alpha)/alpha):.4e}")
        st.write(f"➡️ C_eff = {Ceff:.4e} F")
        
        st.markdown("---")
        st.markdown("**Step 2: Resistive Parameters**")
        st.write(f"R_int = Rs + Rct = {Rs:.4f} + {Rct:.4f} = {Rint:.4f} Ω")
        
        st.markdown("---")
        st.markdown("**Step 3: Energy & Power Densities**")
        st.write(f"Energy (Joules) = 0.5 * C_eff * V² / X = {E_joules:.4f} J/{unit_x}")
        st.write(f"Energy (Watt-hours) = Joules / 3600 = {E_watt_hours:.4f} Wh/{unit_x}")
        st.write(f"Max Power = V² / (4 * R_int * X) = {Pmax:.4f} W/{unit_x}")

except Exception as e:
    st.error(f"An error occurred during calculation: {e}. Please check your inputs.")
