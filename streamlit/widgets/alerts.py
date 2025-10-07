from __future__ import annotations
import streamlit as st

def ok(msg: str): st.success(msg)
def warn(msg: str): st.warning(msg)
def err(msg: str): st.error(msg)
