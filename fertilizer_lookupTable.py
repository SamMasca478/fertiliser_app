import pandas as pd
import streamlit as st

# -----------------------------
# 1) Your table (as-is)
# -----------------------------
data = {
    "unit_ac": [
        5,10,15,20,25,30,35,40,45,50,
        55,60,65,70,75,80,85,90,95,100,
        105,110,115,120,125,130,135,140,145,150,
        155,160,165,170,175,180,185,190,195,200,
        205,210,215,220,225,230,235,240,245,250
    ],
    "kg_ha": [
        6,13,19,25,31,38,44,50,56,63,
        69,75,81,88,94,100,106,113,119,125,
        131,138,144,150,156,163,169,175,181,188,
        194,200,206,213,219,225,231,238,244,250,
        256,263,269,275,281,288,294,300,306,313
    ],
    "kg_ha_nutrient": [
        5,10,15,20,25,30,35,40,45,50,
        55,60,65,70,75,80,85,90,95,100,
        105,110,115,120,125,130,135,140,145,150,
        155,160,165,170,175,180,185,190,195,200,
        205,210,215,220,225,230,235,240,250,260
    ],
    "urea_46_kg_ha": [
        11,22,33,43,54,65,76,87,98,109,
        120,130,141,152,163,174,185,196,207,217,
        228,239,250,261,272,283,293,304,315,326,
        337,348,359,370,380,391,402,413,424,435,
        446,457,467,478,489,500,511,522,543,565
    ],
    "nitram_34_5_kg_ha": [
        14,29,43,58,72,87,101,116,130,145,
        159,174,188,203,217,232,246,261,275,290,
        304,319,333,348,362,377,391,406,420,435,
        449,464,478,493,507,522,536,551,565,580,
        594,609,623,638,652,667,681,696,725,754
    ],
    "nuram_35s_l_ha": [
        14,29,43,57,71,86,100,114,129,143,
        157,171,186,200,214,229,243,257,271,286,
        300,314,329,343,357,371,386,400,414,429,
        443,457,471,486,500,514,529,543,557,571,
        586,600,614,629,643,657,671,686,714,743
    ],
    "n20": [
        25,50,75,100,125,150,175,200,225,250,
        275,300,325,350,375,400,425,450,475,500,
        None,None,None,None,None,None,None,None,None,None,
        None,None,None,None,None,None,None,None,None,None,
        None,None,None,None,None,None,None,None,None,None
    ]
}

df = pd.DataFrame(data)

# -----------------------------
# 2) Lookup logic (unchanged)
# -----------------------------
def lookup(df: pd.DataFrame, column: str, value: float, mode: str):
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found. Choose from: {list(df.columns)}")

    s = pd.to_numeric(df[column], errors="coerce")
    if s.isna().all():
        raise ValueError(f"Column '{column}' isn't numeric.")

    if mode == "Exact":
        return df[s == value]

    df2 = df.copy()
    df2["_x"] = s
    df2 = df2.sort_values("_x").reset_index(drop=True)

    x_min, x_max = float(df2["_x"].min()), float(df2["_x"].max())

    if mode == "Nearest":
        idx = (df2["_x"] - value).abs().idxmin()
        return df2.loc[[idx]].drop(columns="_x")

    if mode == "Bracket (below + above)":
        lower = df2[df2["_x"] <= value].tail(1)
        upper = df2[df2["_x"] >= value].head(1)
        out = pd.concat([lower, upper]).drop(columns="_x").drop_duplicates()
        return out

    if mode == "Interpolated (calculated)":
        if value < x_min or value > x_max:
            idx = (df2["_x"] - value).abs().idxmin()
            return df2.loc[[idx]].drop(columns="_x")

        exact = df2[df2["_x"] == value]
        if not exact.empty:
            return exact.drop(columns="_x")

        lower = df2[df2["_x"] < value].tail(1)
        upper = df2[df2["_x"] > value].head(1)

        if lower.empty or upper.empty:
            idx = (df2["_x"] - value).abs().idxmin()
            return df2.loc[[idx]].drop(columns="_x")

        x0 = float(lower["_x"].iloc[0])
        x1 = float(upper["_x"].iloc[0])
        t = (value - x0) / (x1 - x0)

        row = {}
        row[column] = value

        for c in df.columns:
            if c == column:
                continue
            a = pd.to_numeric(lower[c], errors="coerce").iloc[0]
            b = pd.to_numeric(upper[c], errors="coerce").iloc[0]
            if pd.isna(a) or pd.isna(b):
                row[c] = None
            else:
                row[c] = a + t * (b - a)

        out = pd.DataFrame([row])[df.columns]
        return out

    raise ValueError("Unknown mode")


# -----------------------------
# 3) NEW: Direct calculator from Target N (kg/ha)
# -----------------------------
def rates_from_target_n(target_n_kg_ha: float) -> pd.DataFrame:
    # Product rates from N target
    urea_kg_ha   = target_n_kg_ha / 0.46
    nitram_kg_ha = target_n_kg_ha / 0.345
    n20_kg_ha    = target_n_kg_ha / 0.20

    # Nuram 35S: 35% w/v = 0.35 kg N per litre => L/ha = N / 0.35
    nuram_l_ha   = target_n_kg_ha / 0.35

    # optional: show unit/ac equivalents too (1 unit/ac = 1 lb/ac; 1 lb/ac = 1.12085 kg/ha)
    units_ac = target_n_kg_ha / 1.12085

    row = {
        "Target_N_kg_ha": target_n_kg_ha,
        "unit_ac_equiv": units_ac,
        "urea_46_kg_ha": urea_kg_ha,
        "nitram_34_5_kg_ha": nitram_kg_ha,
        "nuram_35s_l_ha": nuram_l_ha,
        "n20_kg_ha": n20_kg_ha,
    }
    return pd.DataFrame([row])


# -----------------------------
# 4) Streamlit UI
# -----------------------------
st.set_page_config(page_title="Nitrogen Conversion & Product Rates", layout="wide")
st.title("Nitrogen Conversion & Product Rates")

st.write("Enter a target and get either a table lookup OR a calculated product-rate row (recommended for liquids).")

tab1, tab2 = st.tabs(["Calculator (recommended)", "Lookup your reference table"])

# ---- Tab 1: Calculator (always correct for Nuram w/v) ----
with tab1:
    st.subheader("Calculator from Target N (kg/ha)")

    target_n = st.number_input("Target N (kg/ha)", min_value=0.0, value=40.0, step=1.0)

    calc = rates_from_target_n(float(target_n))
    st.dataframe(calc.round(2), use_container_width=True)

    st.caption("Nuram 35S uses 35% w/v (0.35 kg N/L): L/ha = Target N ÷ 0.35.")

# ---- Tab 2: Your existing lookup table ----
with tab2:
    st.subheader("Conversion Table Lookup (your reference table)")
    st.write("Choose a column, enter a value, and get the corresponding row(s).")

    col1, col2, col3 = st.columns([2, 2, 3])

    with col1:
        column = st.selectbox("Input column", df.columns.tolist())

    with col2:
        numeric_series = pd.to_numeric(df[column], errors="coerce")
        min_v = float(numeric_series.min()) if numeric_series.notna().any() else 0.0
        value = st.number_input("Value", min_value=0.0, value=float(min_v), step=0.1, key="lookup_value")

    with col3:
        mode = st.radio(
            "Match mode",
            ["Nearest", "Exact", "Bracket (below + above)", "Interpolated (calculated)"],
            horizontal=True
        )

    if st.button("Lookup"):
        try:
            result = lookup(df, column, float(value), mode)
            if result.empty and mode == "Exact":
                st.warning("No exact match found. Try Nearest or Interpolated.")
            elif result.empty:
                st.warning("No result found.")
            else:
                st.success(f"Returned {len(result)} row(s).")
                st.dataframe(result.round(2), use_container_width=True)
        except Exception as e:
            st.error(str(e))

    st.divider()
    st.subheader("Full table (reference)")
    st.dataframe(df, use_container_width=True)
