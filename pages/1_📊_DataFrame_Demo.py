#%%
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "NanumGothic"


#%%
class DataFramePage:
    def __init__(self):
        self._init_layout()
        self.file = None
        self.df = None
        self.feature = None

    def _init_layout(self):
        st.set_page_config(page_title="DataFrame Demo", layout="wide", page_icon="📊")
        st.markdown("# 📊 DataFrame Demo")
        st.sidebar.header("DataFrame Demo")
        st.title("MasterTable")

    def load_file(self):
        self.file = st.file_uploader("파일 선택(csv or excel)", type=["csv", "xls", "xlsx"])

    def show_data_frame(self):
        if self.file is not None:
            self.df = self._load_data_frame(self.file)

    def select_feature(self):
        if self.df is not None:
            features = self.df.columns.to_list()
            self.feature = st.selectbox("Choose a feature", features[1:])

    def show_graph(self):
        if self.feature is not None:
            if "방향" in self.feature:
                direction_df = self.df[self.feature].copy()
                direction_df[direction_df == "전진"] = 1
                direction_df[direction_df == "후진"] = -1
                st.line_chart(direction_df)

            elif "가속" in self.feature:
                direction_df = self.df[self.feature].copy()
                direction_df[direction_df.isna()] = 0
                direction_df[direction_df == "급가속"] = 1
                direction_df[direction_df == "가속"] = 0.5
                st.line_chart(direction_df)

            elif "감속" in self.feature:
                direction_df = self.df[self.feature].copy()
                direction_df[direction_df.isna()] = 0
                direction_df[direction_df == "급감속"] = 1
                direction_df[direction_df == "감속"] = 0.5
                st.line_chart(direction_df)
            else:
                len_isna = len(self.df[self.df[self.feature].isna()].copy())
                len_df = len(self.df[self.feature].copy())

                if len_isna == len_df:
                    st.text("No data exists")
                else:
                    st.line_chart(self.df[self.feature])

    def _load_data_frame(self, file):
        extension = file.name.split(".")[-1]
        if extension == "csv":
            df = pd.read_csv(file)
            st.dataframe(df)
        elif "xls" in extension:
            df = pd.read_excel(file, engine="openpyxl")
            st.dataframe(df)

        return df


#%%
data_page = DataFramePage()
data_page.load_file()
data_page.show_data_frame()
data_page.select_feature()
data_page.show_graph()


#     data = df.sort_index(ascending=True).loc[:, "부하"]
#     tab1, tab2 = st.tabs(["차트", "데이터"])

#     with tab1:
#         st.line_chart(data)

#     with tab2:
#         st.dataframe(df.sort_index(ascending=True))

#     with st.expander("컬럼 설명"):
#         st.markdown(
#             """
#         """
#         )

#     # 다운로드 버튼 연결
#     st.download_button(
#         label="CSV로 다운로드", data=df.to_csv(), file_name="sample.csv", mime="text/csv"
#     )

# @st.cache
# def get_UN_data():
#     AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
#     df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
#     return df.set_index("Region")


# try:
#     df = get_UN_data()
#     countries = st.multiselect(
#         "Choose countries", list(df.index), ["China", "United States of America"]
#     )
#     if not countries:
#         st.error("Please select at least one country.")
#     else:
#         data = df.loc[countries]
#         data /= 1000000.0
#         st.write("### Gross Agricultural Production ($B)", data.sort_index())

#         data = data.T.reset_index()
#         data = pd.melt(data, id_vars=["index"]).rename(
#             columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
#         )
#         chart = (
#             alt.Chart(data)
#             .mark_area(opacity=0.3)
#             .encode(
#                 x="year:T",
#                 y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
#                 color="Region:N",
#             )
#         )
#         st.altair_chart(chart, use_container_width=True)
# except URLError as e:
#     st.error(
#         """
#         **This demo requires internet access.**
#         Connection error: %s
#     """
#         % e.reason
#     )
