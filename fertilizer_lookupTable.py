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
# 2) Lookup logic
# -----------------------------
def lookup(df: pd.DataFrame, column: str, value: float, mode: str):
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found. Choose from: {list(df.columns)}")

    s = pd.to_numeric(df[column], errors="coerce")

    if mode == "Exact":
        return df[df[column] == value]

    if s.isna().all():
        raise ValueError(f"Column '{column}' isn't numeric (can't do nearest/bracket).")

    if mode == "Nearest":
        idx = (s - value).abs().idxmin()
        return df.loc[[idx]]

    if mode == "Bracket (below + above)":
        df2 = df.copy()
        df2["_col"] = s
        df2 = df2.sort_values("_col")

        lower = df2[df2["_col"] <= value].tail(1)
        upper = df2[df2["_col"] >= value].head(1)

        out = pd.concat([lower, upper]).drop(columns="_col").drop_duplicates()
        return out

    raise ValueError("Unknown mode")


# -----------------------------
# 3) Streamlit UI
# -----------------------------
st.set_page_config(page_title="Conversion Table Lookup", layout="wide")
st.title("Conversion Table Lookup")

st.write("Choose a column, enter a value, and get the corresponding row(s).")

col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    column = st.selectbox("Input column", df.columns.tolist())

with col2:
    # sensible defaults
    numeric_series = pd.to_numeric(df[column], errors="coerce")
    min_v = float(numeric_series.min()) if numeric_series.notna().any() else 0.0
    max_v = float(numeric_series.max()) if numeric_series.notna().any() else 1000.0
    value = st.number_input("Value", min_value=0.0, value=float(min_v), step=1.0)

with col3:
    mode = st.radio("Match mode", ["Nearest", "Exact", "Bracket (below + above)"], horizontal=True)

if st.button("Lookup"):
    try:
        result = lookup(df, column, value, mode)
        if result.empty:
            st.warning("No exact match found (try Nearest or Bracket).")
        else:
            st.success(f"Returned {len(result)} row(s).")
            st.dataframe(result, use_container_width=True)
    except Exception as e:
        st.error(str(e))

st.divider()
st.subheader("Full table (reference)")
st.dataframe(df, use_container_width=True)
