import streamlit as st
import sys, os
import pandas as pd
import pickle
import matplotlib

matplotlib.rcParams["font.family"] = "NanumGothic"
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt

from plotly.subplots import make_subplots

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../../"))
from gui.base_page import PageFrame


class PlottingPage(PageFrame):
    def __init__(self) -> None:
        super().__init__()

        self.encoded_df = None
        self.raw_df = None

        self.new_columns = {
            "Engine_type": "learning",
            "Driving_type": "learning",
            "Specific_type": "split",
            "Ton_type": "split",
            "Series": "split",
            "Category": "learning",
            "System": "learning",
            "Failure_class": "learning",
            "Failure_distinguish": "learning",
        }
        self._init_layout()
        self._body_layout()
        self._side_layout()

    @staticmethod
    def _init_layout():
        st.set_page_config(
            page_title="Plotting Demo",
            page_icon="📈",
            layout="wide",
        )
        st.markdown("# 📈 Plotting Demo")
        st.sidebar.header("Feature engineering")
        st.sidebar.markdown("---")

    def _body_layout(self):
        self._introduction()
        self._model_layout()
        self._training_layout()
        raw_df = self._testing_layout(self.encoded_df)

        if raw_df is not None:
            st.text("Predicted Result.")
            self.raw_df = raw_df
            raw_processed_df = self._raw_preprocessing(raw_df)
            st.dataframe(raw_processed_df)
            if raw_processed_df is not None:
                dataset = st.selectbox("Choose a type", ("series", "tons", "2d", "3d"))

                if dataset == "series":
                    self.visualize_series_frequency()

                if dataset == "tons":
                    self.visualize_tons_frequency()

                if dataset == "2d":
                    self.visualize_clustered_data_2d(
                        ("DS. Amt. Total(KRW)", "num_of_failures"), "Series 구분"
                    )

                if dataset == "3d":
                    self.visualize_clustered_data_3d(
                        ("DS. Amt. Total(KRW)", "num_of_failures", "Operation Hour"),
                        "Series 구분",
                    )

    def _raw_preprocessing(self, df: pd.DataFrame):
        df["Failure_class"] = df["Act. Type"].apply(self._failure_labeling)
        df["num_of_failures"] = df["Serial num"].apply(self._num_failure)
        df = df.drop_duplicates(["Serial num"])
        return df

    @staticmethod
    def _failure_labeling(data):
        fa_act_type = [
            "201",
            "207",
            "209",
            "212",
            "601",
            "602",
            "606",
            "613",
            "202",
            "203",
            "208",
            "213",
            "218",
            "604",
            "615",
            "621",
            "624",
            "630",
            "631",
            "632",
            "633",
            "204",
            "211",
            "605",
            "612",
            "618",
            "619",
            "634",
            "ZPM",
            "ZPP",
            "217",
        ]
        nf_act_type = [
            "610",
            "205",
            "206",
            "210",
            "214",
            "215",
            "607",
            "608",
            "609",
            "611",
            "614",
            "616",
            "617",
            "620",
            "699",
        ]
        re_act_type = ["216", "603", "623"]
        if data in fa_act_type:
            return "fa"
        elif data in nf_act_type:
            return "nf"
        elif data in re_act_type:
            return "re"

    def _num_failure(self, data):
        return len(
            self.raw_df[
                (self.raw_df["Serial num"] == data)
                & (self.raw_df["Failure_class"] == "fa")
            ]
        )

    def _model_layout(self):
        model_file = self._load_model()
        if model_file is not None:
            with open(model_file.name, "rb") as f:
                self.trained_model = pickle.load(f)

    def _side_layout(self):
        pass

    @staticmethod
    def get_data_from_sidebar():
        pass

    @staticmethod
    def _introduction():
        st.title("**Warranty Data Analysis(WDA)**")
        st.subheader(
            """
            This is a page where you can handle datas and show figure from WDA file
            """
        )

        st.markdown(
            """
        - 🗂️ Load a WDA file (The extension of file is .xlsx)
        - ✅ Choose the multiple features you want to learn
        - ⚙️ Pick a model and set its hyper-parameters
        - 📉 Train it and check its performance metrics and decision boundary on train and test data
        - 🩺 Diagnose possible overitting and experiment with other settings
        -----
        """
        )

    def _training_layout(self):
        self.training_file = self._load_training_file()

        df = None
        if self.training_file is not None:
            df = self._load_data_frame(self.training_file, sheet_name="Labeling Data")
        self.encoded_df = None
        processed_df = self.training_button_preprocess(df)

        if processed_df is not None:
            self.encoded_df = self._get_encoded_df(processed_df)

        if self.encoded_df is not None:
            st.text("Done.")
        st.markdown("---")

    def _load_training_file(self):
        training_file = st.file_uploader(
            "WDA 파일 선택(csv or excel)", type=["csv", "xls", "xlsx"], key=0
        )

        return training_file

    def _load_model(self):
        model_file = st.file_uploader("모델 선택(pt or pickle)", type=["pickle", "pt"])
        st.markdown("---")
        return model_file

    def _load_testing_file(self):
        test_file = st.file_uploader(
            "Test 파일 선택(csv or excel)", type=["csv", "xls", "xlsx"], key=1
        )
        st.markdown("---")
        return test_file

    def training_button_preprocess(self, df, is_trainig=True):
        if df is None:
            return

        button = st.checkbox("Training Data Preprocessing")
        if button:
            processed_df = self._preprocessing(df, is_trainig)
            processed_df = processed_df[
                [
                    "type_f1",
                    "Specific_type",
                    "Failure Area",
                    "Cause P/No Desc.",
                    "Operation Hour",
                    "Failure 분류",
                    "DS. Amt. Total(KRW)",
                    "Act. Type",
                    "Failure 구분",
                    "구동 Type 구분",
                    "Engine Type 구분",
                    "Category",
                    "System",
                ]
            ].copy()
            processed_df = processed_df.dropna(axis=0)
            return processed_df

    def _testing_layout(self, encoded_df):
        if encoded_df is None:
            st.text("Preprocess first")
            return

        df = None
        raw_df = None
        self.testing_file = self._load_testing_file()

        if self.testing_file is not None:
            df = self._load_data_frame(self.testing_file)
            raw_df = self.testing_button_preprocess(df, is_trainig=False)

        if raw_df is not None:
            raw_encoded_df = self._get_raw_encoded(raw_df, self.encoded_df)
            preprocessing_raw_df = raw_df[
                [
                    "Failure Area",
                    "Cause P/No Desc.",
                    "Operation Hour",
                    "Act. Type",
                    "DS. Amt. Total(KRW)",
                ]
            ].copy()
            # , 'Failure 구분', '구동 Type 구분', 'Engine Type 구분', 'Category', 'System' 'Failure 분류'

            x_test = {}
            x_test["Failure_distinguish"] = pd.concat(
                (preprocessing_raw_df["Operation Hour"], raw_encoded_df["Act. Type"]),
                axis=1,
            )
            x_test["Driving_type"] = pd.concat(
                (raw_encoded_df["type_f1"], raw_encoded_df["Specific_type"]), axis=1
            )
            x_test["Engine_type"] = pd.concat(
                (raw_encoded_df["type_f1"], raw_encoded_df["Specific_type"]), axis=1
            )

            for k in self.new_columns.keys():
                y = self._predict_RF(k, x_test)
                if y is not None:
                    raw_df[str(k)] = y

        if raw_df is not None:
            st.text("Done.")
        st.markdown("---")
        return raw_df

    def testing_button_preprocess(self, df, is_trainig=True):
        if df is None:
            return

        button2 = st.checkbox("Testing Data Preprocessing", key="test")
        if button2:
            raw_df = self._preprocessing(df, is_trainig)
            # processed_df = processed_df.dropna(axis=0)
            return raw_df

    def _get_raw_encoded(self, raw_df, encoded_df):
        raw_encoded_df = {}
        raw_encoded_df["type_f1"] = pd.DataFrame(
            0, index=range(len(raw_df)), columns=encoded_df["type_f1"]
        )
        for i in range(len(raw_df)):
            raw_encoded_df["type_f1"].iloc[i][raw_df.iloc[i]["type_f1"]] = 1

        raw_encoded_df["Act. Type"] = pd.DataFrame(
            0, index=range(len(raw_df)), columns=encoded_df["Act. Type"]
        )
        for i in range(len(raw_df)):
            raw_encoded_df["Act. Type"].iloc[i][raw_df.iloc[i]["Act. Type"]] = 1

        raw_encoded_df["Specific_type"] = pd.DataFrame(
            0, index=range(len(raw_df)), columns=encoded_df["Specific_type"]
        )
        for i in range(len(raw_df)):
            raw_encoded_df["Specific_type"].iloc[i][raw_df.iloc[i]["상세 Type 구분"]] = 1

        return raw_encoded_df

    def _preprocessing(self, df: pd.DataFrame, is_trainig):
        copied_df = df.copy()
        if is_trainig:
            copied_df["type_f1"] = copied_df["Model"].apply(
                self._convert_type, data_type="f1"
            )
            copied_df["Specific_type"] = copied_df["Model"].apply(
                self._convert_type, data_type="specific"
            )
            copied_df["Series"] = copied_df["Model"].apply(
                self._convert_type, data_type="series"
            )
            copied_df = copied_df.dropna(subset=["Act. Type"], inplace=False)
            copied_df = copied_df.reset_index()
            self.act_type_list = list(copied_df["Act. Type"].value_counts().keys())
            copied_df["Encoding_Act_type"] = copied_df["Act. Type"].apply(
                self._convert_type, data_type="encoding"
            )
            copied_df["QR Operation Hour"] = copied_df["Operation Hour"].apply(
                self._convert_type, data_type="QR"
            )

        if not is_trainig:
            copied_df["Operation Hour"] = copied_df["Operation Hour"].apply(
                self._convert_type, data_type="operation"
            )
            copied_df["DS. Amt. Total(KRW)"] = copied_df["DS. Amt. Total(KRW)"].apply(
                self._convert_type, data_type="price"
            )
            copied_df["Act. Type"] = copied_df["Act. Type"].astype("str")
            copied_df["Specific_type"] = copied_df["Model"].apply(
                self._convert_type, data_type="specific"
            )
            copied_df["type_f1"] = copied_df["Model"].apply(
                self._convert_type, data_type="f1"
            )
            copied_df["상세 Type 구분"] = copied_df["Model"].apply(
                self._convert_type, data_type="specific"
            )
            copied_df["Ton 구분"] = copied_df["Model"].apply(
                self._convert_type, data_type="ton"
            )
            copied_df["Series 구분"] = copied_df["Model"].apply(
                self._convert_type, data_type="series"
            )
        return copied_df

    def _convert_type(self, data, data_type=""):
        result = None

        if data_type == "f1":
            ton = self._change_ton(data)
            result = data.split("-")[0].split(ton)[0]
        if data_type == "specific":
            ton = self._change_ton(data)
            result = data.split("-")[0].split(ton)[1]
        if data_type == "ton":
            ton = self._change_ton(data)
            ton = int(ton)
            if 15 <= ton <= 18:
                result = 1
            elif 20 <= ton <= 35:
                result = 2
            elif 40 <= ton:
                result = 4

        if data_type == "series":
            result = data.split("-")[1]
        if data_type == "encoding":
            result = self.act_type_list.index(data)
        if data_type == "QR":
            if data <= 100:
                result = "Q"
            else:
                result = "R"
        if data_type == "operation" or data_type == "price":
            if type(data) == str:
                if "," in data:
                    result = float("".join(data.split(",")))
                else:
                    result = float(data)

        return result

    @staticmethod
    def _change_ton(datas):
        ton = []
        for i in datas.split("-")[0]:
            if 48 <= ord(i) <= 57:
                ton.append(i)
        ton = "".join(ton)
        return ton

    def _predict_RF(self, label, x_test):
        if label == "Category" or label == "System" or label == "Failure_class":
            return

        label_type = self.new_columns[label]
        if label_type == "learning":
            y = self.trained_model[label].predict(x_test[label])
            return y

    @staticmethod
    def _get_encoded_df(df):
        encoded_df = {}
        encoded_df["type_f1"] = (
            pd.get_dummies(df["type_f1"]).copy().columns.values.tolist()
        )
        encoded_df["Act. Type"] = (
            pd.get_dummies(df["Act. Type"]).copy().columns.values.tolist()
        )
        encoded_df["Specific_type"] = (
            pd.get_dummies(df["Specific_type"]).copy().columns.values.tolist()
        )
        encoded_df["Failure Area"] = (
            pd.get_dummies(df["Failure Area"]).copy().columns.values.tolist()
        )
        encoded_df["Cause P/No Desc."] = (
            pd.get_dummies(df["Cause P/No Desc."]).copy().columns.values.tolist()
        )

        return encoded_df

    def _set_columns(self):
        col1, col2 = st.columns((1, 1))
        with col1:
            self.plot_placeholder = st.empty()

        with col2:
            self.duration_placeholder = st.empty()
            self.model_url_placeholder = st.empty()
            self.code_header_placeholder = st.empty()
            self.snippet_placeholder = st.empty()
            self.tips_header_placeholder = st.empty()
            self.tips_placeholder = st.empty()

        fig = make_subplots(
            rows=2,
            cols=2,
            specs=[
                [{"colspan": 2}, None],
                [{"type": "indicator"}, {"type": "indicator"}],
            ],
            subplot_titles=("Decision Boundary", None, None),
            row_heights=[0.7, 0.30],
        )
        self.plot_placeholder.plotly_chart(fig, True)

    def visualize_series_frequency(self):
        Series_failure_freq = pd.DataFrame(
            0,
            index=self.raw_df["Series 구분"].value_counts().keys().tolist(),
            columns=sorted(
                self.raw_df["num_of_failures"].value_counts().keys().tolist()
            ),
        )
        for r in Series_failure_freq.T.columns.values.tolist():
            for c in Series_failure_freq.columns.values.tolist():
                # print(raw_WDA[(raw_WDA['Series 구분']==r) & (raw_WDA['num_of_failures']==c)])
                if (
                    c
                    in self.raw_df[(self.raw_df["Series 구분"] == r)]["num_of_failures"]
                    .value_counts()
                    .keys()
                ):

                    Series_failure_freq.loc[r][c] = self.raw_df[
                        (self.raw_df["Series 구분"] == r)
                    ]["num_of_failures"].value_counts()[c]
                else:
                    Series_failure_freq.loc[r][c] = 0

        # Series_failure_freq.T.plot.bar(
        #     stacked=True, rot=45, width=0.8, figsize=(15, 10)
        # )
        # fig, ax = plt.subplots()
        # ax.set_title("Series failure frequency", fontsize=20)
        # ax.set_xlabel("num of failures", size=15)
        # ax.legend(fontsize=15)
        st.bar_chart(Series_failure_freq.T)

    def visualize_tons_frequency(self):
        Ton_failure_freq = pd.DataFrame(
            0,
            index=self.raw_df["Ton 구분"].value_counts().keys().tolist(),
            columns=sorted(
                self.raw_df["num_of_failures"].value_counts().keys().tolist()
            ),
        )

        for r in Ton_failure_freq.T.columns.values.tolist():
            for c in Ton_failure_freq.columns.values.tolist():
                if (
                    c
                    in self.raw_df[(self.raw_df["Ton 구분"] == r)]["num_of_failures"]
                    .value_counts()
                    .keys()
                ):

                    Ton_failure_freq.loc[r][c] = self.raw_df[
                        (self.raw_df["Ton 구분"] == r)
                    ]["num_of_failures"].value_counts()[c]
                else:
                    Ton_failure_freq.loc[r][c] = 0

        # fig, ax = plt.subplots()
        # ax.set_title("Ton 구분 failure frequency", fontsize=20)
        # ax.set_xlabel("num of failures", size=15)
        # ax.legend(fontsize=15)
        st.bar_chart(Ton_failure_freq.T)

    def visualize_clustered_data_2d(self, features, cluster_name):

        fig, ax = plt.subplots()
        for i in self.raw_df[cluster_name].value_counts().keys().tolist():
            ax.scatter(
                self.raw_df[self.raw_df[cluster_name] == i][features[0]],
                self.raw_df[self.raw_df[cluster_name] == i][features[1]],
                alpha=0.3,
                label=str(i),
            )

        ax.set_xlabel("" + str(features[0]), fontsize=15)
        ax.set_ylabel("" + str(features[1]), fontsize=15)
        ax.legend(title="Clusters")

        # if 'Amt' in features[0] or 'Hour' in features[0]:
        #     ax.set_xscale('log')
        # if 'Amt' in features[1] or 'Hour' in features[1]:
        #     ax.set_yscale('log')

        plt.title(cluster_name)
        plt.legend(title=cluster_name, fontsize=15)
        plt.show()
        st.pyplot(fig)

    def visualize_clustered_data_3d(self, features, cluster_name):

        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")

        for c in self.raw_df[cluster_name].value_counts().keys().tolist():

            ax.scatter(
                self.raw_df[self.raw_df[cluster_name] == c][features[0]],
                self.raw_df[self.raw_df[cluster_name] == c][features[1]],
                self.raw_df[self.raw_df[cluster_name] == c][features[2]],
                alpha=0.3,
                label=str(c),
            )

        ax.set_xlabel("" + str(features[0]))
        ax.set_ylabel("" + str(features[1]))
        ax.set_zlabel("" + str(features[2]))

        plt.title(cluster_name)

        ax.legend(title=cluster_name, fontsize=15)
        st.pyplot(fig)


plot_demo = PlottingPage()
