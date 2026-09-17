import httpx
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Support Ticket AI",
    page_icon="🎫",
    layout="wide",
)


st.title("🎫 Support Ticket AI")
st.caption("AI-powered support ticket analytics dashboard")


def call_query_api(question: str):
    response = httpx.post(
        f"{API_BASE_URL}/api/query",
        json={"question": question},
        timeout=120.0,
    )

    response.raise_for_status()
    return response.json()


def call_anomaly_api():
    response = httpx.get(
        f"{API_BASE_URL}/api/anomalies",
        timeout=120.0,
    )

    response.raise_for_status()
    return response.json()


# Sidebar
st.sidebar.header("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Natural Language Query",
        "Anomaly Detection",
    ],
)


# Natural Language Query
if page == "Natural Language Query":

    st.header("Ask Your Question")

    question = st.text_area(
        "Enter your question",
        placeholder=(
            "Example: How many open tickets are there?"
        ),
        height=100,
    )

    if st.button("Run Query", type="primary"):

        if not question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                with st.spinner("Analyzing your question..."):
                    result = call_query_api(question)

                st.success("Query completed successfully")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Operation",
                        result["operation"],
                    )

                with col2:
                    st.metric(
                        "Status",
                        "Success",
                    )

                st.subheader("Answer")
                st.info(result["answer"])

                st.subheader("Detailed Data")
                st.json(result["data"])

            except httpx.HTTPError as error:
                st.error(
                    f"API request failed: {error}"
                )


# Anomaly Detection
elif page == "Anomaly Detection":

    st.header("Anomaly Detection Dashboard")

    if st.button("Detect Anomalies", type="primary"):

        try:
            with st.spinner("Detecting anomalies..."):
                result = call_anomaly_api()

            total_anomalies = result["total_anomalies"]
            anomalies = result["anomalies"]

            st.metric(
                "Total Anomalies",
                total_anomalies,
            )

            if not anomalies:
                st.success("No anomalies detected.")
            else:
                st.subheader("Detected Anomalies")

                for anomaly in anomalies:

                    with st.expander(
                        f"{anomaly['ticket_id']} - "
                        f"{anomaly['reason']}"
                    ):

                        st.write(
                            f"**Severity:** "
                            f"{anomaly['severity']}"
                        )

                        st.write(
                            f"**Reason:** "
                            f"{anomaly['reason']}"
                        )

                        st.json(anomaly["details"])

        except httpx.HTTPError as error:
            st.error(
                f"API request failed: {error}"
            )