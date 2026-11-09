import html

import streamlit as st
from core.llm import generate_sql, generate_insight
from core.sql_runner import run_query
from core.chart import make_chart
from core.schema import get_schema_string

st.set_page_config(page_title="SpeQtraL", page_icon="📊", layout="wide")
st.markdown(
    """
    <style>
    #MainMenu, footer {visibility: hidden;}
    .block-container {max-width: 1000px; padding-top: 1.5rem;}
    @media (max-width: 640px) {
        .block-container {padding: 1rem;}
        h1 {font-size: 2.25rem !important;}
        div[data-testid="stHorizontalBlock"] {flex-wrap: wrap; gap: 0.5rem;}
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            flex: 1 1 150px;
            min-width: 0;
        }
        div[data-testid="stButton"] button {height: auto; min-height: 3rem; white-space: normal;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h1 style="font-size: 3rem; margin-bottom: 0.25rem;">📊 SpeQtraL</h1>
    <p style="font-size: 1.15rem; margin: 0;">Ask a business question. Get SQL, results, and an insight.</p>
    <p style="color: #9CA3AF; margin-top: 0.4rem;">Powered by Groq, Llama and SQLite · 100k+ Olist orders</p>
    """,
    unsafe_allow_html=True,
)

def _select_example(question: str) -> None:
    st.session_state["question"] = question


if not st.session_state.get("question"):
    st.markdown("#### Try an example")
    example_questions = [
        "Which state has the most orders?",
        "What are the top 5 product categories by revenue?",
        "How many orders were delivered late?",
        "Which sellers generated the most revenue?",
        "What is the average review score by state?",
        "How many orders are there by status?",
    ]
    for row_start in (0, 3):
        columns = st.columns(3)
        for column, example in zip(columns, example_questions[row_start:row_start + 3]):
            column.button(
                example,
                key=f"example_{row_start}_{example}",
                on_click=_select_example,
                args=(example,),
                width="stretch",
            )

question = st.text_input(
    "Ask a question about the Olist e-commerce dataset",
    placeholder="Which state has the most delayed orders?",
    key="question",
)

with st.sidebar:
    st.markdown("### About")
    st.caption("Explore insights from the Olist Brazilian e-commerce dataset with natural-language questions.")
    st.markdown("[View SpeQtraL on GitHub](https://github.com/komalharshita/SpeQtraL)")
    with st.expander("Database schema", expanded=False):
        st.code(get_schema_string(), language="text")

if question:
    with st.status("Writing SQL", expanded=True) as status:
        sql = generate_sql(question)
        status.update(label="Running query")
        df, error = run_query(sql)

        if error:
            st.error(f"The query couldn't run: {error}")
            status.update(label="Query failed", state="error", expanded=False)
        elif df.empty:
            st.info("The query ran successfully but returned no results.")
            status.update(label="No results", state="complete", expanded=False)
        else:
            status.update(label="Summarising results")
            fig = make_chart(df)
            insight = generate_insight(question, df.head(5).to_string())
            status.update(label="Done", state="complete", expanded=False)

            st.markdown(
                f"""
                <div style="border: 1px solid #30363D; border-left: 4px solid #8B5CF6;
                            border-radius: 0.6rem; padding: 1rem 1.25rem; margin: 1rem 0;">
                    <strong style="color: #C4B5FD;">Business insight</strong>
                    <div style="margin-top: 0.4rem;">{html.escape(insight)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            row_metric, column_metric = st.columns(2)
            row_metric.metric("Rows returned", f"{len(df):,}")
            column_metric.metric("Columns returned", f"{len(df.columns):,}")

            chart_tab, table_tab, sql_tab = st.tabs(["Chart", "Table", "SQL"])
            with chart_tab:
                if fig:
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=12, r=12, t=40, b=12),
                        colorway=["#8B5CF6"],
                    )
                    for trace in fig.data:
                        if trace.type == "bar":
                            trace.marker.color = "#8B5CF6"
                    st.plotly_chart(fig, width="stretch")
                else:
                    st.info("No chart is available for this result; see the Table tab.")

            with table_tab:
                column_config = {
                    column: st.column_config.NumberColumn(
                        format="%d" if df[column].dtype.kind in "iu" else "%.2f"
                    )
                    for column in df.select_dtypes(include="number").columns
                }
                st.dataframe(
                    df,
                    hide_index=True,
                    column_config=column_config,
                    width="stretch",
                )

            with sql_tab:
                st.code(sql, language="sql")