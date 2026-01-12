# Fertiliser Conversion Lookup

A simple Streamlit web application to look up fertiliser conversion rates.

The user selects an input column, enters a value, and the app returns the
corresponding row(s) from the conversion table.

## Features
- Select input column (e.g. kg/ha nutrient, unit/ac)
- Enter a numeric value
- Choose matching mode:
  - Nearest
  - Exact
  - Bracket (below and above)
- View the corresponding conversion row(s)

## Local setup

### Requirements
- Python 3.10+
- Streamlit
- Pandas

### Install dependencies
```bash
pip install -r requirements.txt
