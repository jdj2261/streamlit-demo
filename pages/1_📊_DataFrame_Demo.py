#%%
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../"))
from base_page import PageFrame

plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "NanumGothic"


#%%
class DataFramePage(PageFrame):
    def __init__(self):
        super().__init__()
        self._init_layout()

    def _init_layout(self):
        st.set_page_config(page_title="DataFrame Demo", layout="wide", page_icon="π")
        st.markdown("# π DataFrame Demo")
        st.sidebar.header("DataFrame Demo")
        st.title("MasterTable")

    def load_file(self):
        file = st.file_uploader("νμΌ μ ν(csv or excel)", type=["csv", "xls", "xlsx"])
        return file

    def select_feature(self, df):
        if df is not None:
            features = df.columns.to_list()
            feature = st.selectbox("Choose a feature", features[1:])
            return feature

    def show_graph(self, feature):
        if feature is not None:
            if "λ°©ν₯" in feature:
                direction_df = df[feature].copy()
                direction_df[direction_df == "μ μ§"] = 1
                direction_df[direction_df == "νμ§"] = -1
                st.line_chart(direction_df)

            elif "κ°μ" in feature:
                direction_df = df[feature].copy()
                direction_df[direction_df.isna()] = 0
                direction_df[direction_df == "κΈκ°μ"] = 1
                direction_df[direction_df == "κ°μ"] = 0.5
                st.line_chart(direction_df)

            elif "κ°μ" in feature:
                direction_df = df[feature].copy()
                direction_df[direction_df.isna()] = 0
                direction_df[direction_df == "κΈκ°μ"] = 1
                direction_df[direction_df == "κ°μ"] = 0.5
                st.line_chart(direction_df)

            else:
                len_isna = len(df[df[feature].isna()].copy())
                len_df = len(df[feature].copy())

                if len_isna == len_df:
                    st.text("No data exists")
                else:
                    st.line_chart(df[feature])


#%%
data_page = DataFramePage()
file = data_page.load_file()
if file is not None:
    df = data_page._load_data_frame(file)
    feature = data_page.select_feature(df)
    data_page.show_graph(feature)
