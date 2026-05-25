import streamlit as st
import json

creds = json.load(open('credentials.json'))
if "credentials" not in st.session_state:
    st.session_state.credentials = creds

options = list(st.session_state.credentials.keys())
print("Options:", options[:3])

row = {"Division": "KOMPAS.COM News Division"}
idx = options.index(row["Division"]) if row["Division"] in st.session_state.credentials else 0
print("Index for KOMPAS.COM News Division:", idx)
print("Value at index:", options[idx])
