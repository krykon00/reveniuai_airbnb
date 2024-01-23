"""Data mainpulator functions"""
import copy

import pandas as pd


def get_joined_dfs(df: pd.DataFrame, group_cols: list[str], aggs: list[str]) -> pd.DataFrame:
    """Return joined data frame with avg, min & max values"""
    result_df: pd.DataFrame = pd.DataFrame()
    for agg_type in aggs:
        group_df: pd.DataFrame = df.groupby(by=group_cols, as_index=False).agg(agg_type)
        col_names = copy.copy(group_cols)
        col_names.append(agg_type)
        group_df.columns = col_names
        if result_df.empty:
            result_df = group_df
        else:
            result_df = pd.merge(result_df, group_df, how="outer", on=group_cols) 

    return result_df 
