#%%
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../../"))
from gui.base_page import PageFrame

plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "NanumGothic"


#%%
class DataFramePage(PageFrame):
    def __init__(self):
        super().__init__()
        self._init_layout()

    def _init_layout(self):
        st.set_page_config(page_title="DataFrame Demo", layout="wide", page_icon="📊")
        st.markdown("# 📊 DataFrame Demo")
        st.sidebar.header("DataFrame Demo")
        st.title("MasterTable")

    def load_file(self):
        file = st.file_uploader("파일 선택(csv or excel)", type=["csv", "xls", "xlsx"])
        return file

    def select_feature(self, df):
        if df is not None:
            features = df.columns.to_list()
            feature = st.selectbox("Choose a feature", features[1:])
            return feature

    def show_graph(self, feature):
        if feature is not None:
            if "방향" in feature:
                direction_df = df[feature].copy()
                direction_df[direction_df == "전진"] = 1
                direction_df[direction_df == "후진"] = -1
                st.line_chart(direction_df)

            elif "가속" in feature:
                direction_df = df[feature].copy()
                direction_df[direction_df.isna()] = 0
                direction_df[direction_df == "급가속"] = 1
                direction_df[direction_df == "가속"] = 0.5
                st.line_chart(direction_df)

            elif "감속" in feature:
                direction_df = df[feature].copy()
                direction_df[direction_df.isna()] = 0
                direction_df[direction_df == "급감속"] = 1
                direction_df[direction_df == "감속"] = 0.5
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
