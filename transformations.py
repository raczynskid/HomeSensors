import pandas as pd

def dataframe_pivot(df : pd.DataFrame) -> tuple:
    # flattens the data into a timeseries
    return df.melt(id_vars=["recordDate"], value_vars=["living_room_temp", "bathroom_temp", "closet_temp", "humidity", "pressure"])

def breakdown(df: pd.DataFrame) -> tuple:
    # break the flattened dataframe based on variable type
    temperatures = df[["recordDate","variable","value"]].loc[df["variable"].isin(["living_room_temp", "bathroom_temp", "closet_temp"])]
    other = df[["recordDate","variable","value"]].loc[df["variable"].isin(["recordDate","pressure","humidity"])]
    return temperatures, other