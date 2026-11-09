import pandas as pd
import plotly.express as px

def make_chart(df: pd.DataFrame):
    if df is None or df.empty or len(df.columns) < 2:
        return None

    # Identify column types
    text_cols = [c for c in df.columns if df[c].dtype == object]
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    date_cols = [c for c in df.columns if 'date' in c.lower() or 'timestamp' in c.lower()]

    if date_cols and num_cols:
        # Line chart for time series
        return px.line(df, x=date_cols[0], y=num_cols[0], title="Trend over time")
    elif text_cols and num_cols:
        # Bar chart — sort descending, show top 20
        plot_df = df.sort_values(num_cols[0], ascending=False).head(20)
        return px.bar(plot_df, x=text_cols[0], y=num_cols[0],
                      title=f"{num_cols[0]} by {text_cols[0]}")
    return None  # Fall back to table