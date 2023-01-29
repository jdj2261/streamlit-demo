from abc import *
import streamlit as st
import pandas as pd


class PageFrame(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def _init_layout(self):
        raise NotImplementedError

    def _load_data_frame(self, file, sheet_name=None):
        extension = file.name.split(".")[-1]
        if extension == "csv":
            df = pd.read_csv(file, low_memory=False)
            st.dataframe(df)
        elif "xls" in extension:
            df = pd.read_excel(file)
            if sheet_name is not None:
                df = pd.read_excel(file, sheet_name=sheet_name)
            st.dataframe(df)

        return df
