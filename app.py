import streamlit as st
from core.llm import generate_sql, generate_insight
from core.sql_runner import run_query
from core.chart import make_chart

st.set_page_config(page_title="SpeQtraL", page_icon="📊", layout="wide")
st.title("📊 SpeQtraL")
st.caption("Ask a business question. Get SQL, results, and an insight.")

question = st.text_input("Ask a question about the Olist e-commerce dataset",
                          placeholder="Which state has the most delayed orders?")

if question:
    with st.spinner("Generating SQL..."):
        sql = generate_sql(question)

    with st.expander("View generated SQL"):
        st.code(sql, language="sql")

    df, error = run_query(sql)

    if error:
        st.error(f"The query couldn't run: {error}")
    elif df.empty:
        st.info("The query ran successfully but returned no results.")
    else:
        st.dataframe(df, use_container_width=True)
        fig = make_chart(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        with st.spinner("Generating insight..."):
            insight = generate_insight(question, df.head(5).to_string())
        st.success(f"💡 {insight}")