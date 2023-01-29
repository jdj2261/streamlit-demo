import streamlit as st
import pandas as pd
import time
import datetime
import altair as alt
from urllib.error import URLError

st.set_page_config(
    page_title="Train Demo",
    page_icon="💯",
    layout="wide",
)

file = st.file_uploader("파일 선택(csv or excel)", type=["csv", "xls", "xlsx"])
