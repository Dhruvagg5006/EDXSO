"""
Streamlit Web Dashboard for Automated Micro-Influencer Outreach System.
Provides interactive pipeline execution, influencer data inspection,
message review/editing, and live outreach tracking.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import sqlite3
import pandas as pd
import streamlit as st
import config
from src.pipeline import MicroInfluencerPipeline
from src.sending.tracker import OutreachTracker
from src.personalization.generator import MessagePersonalizer
from src.sending.email_service import EmailDispatcher

# Page Setup
st.set_page_config(
    page_title="Micro-Influencer Outreach System",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .badge-pass {
        color: #15803d;
        background-color: #dcfce7;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-fail {
        color: #b91c1c;
        background-color: #fee2e2;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def load_data():
    if config.FINAL_DATASET_CSV.exists():
        return pd.read_csv(config.FINAL_DATASET_CSV)
    return pd.DataFrame()

def load_db_logs():
    tracker = OutreachTracker()
    logs = tracker.get_all_logs()
    if logs:
        return pd.DataFrame(logs)
    return pd.DataFrame(columns=[
        "id", "sent_at", "influencer_name", "platform", "email",
        "channel", "status", "message_content", "notes"
    ])

# Sidebar Configuration
st.sidebar.title("🚀 Pipeline Controls")
st.sidebar.markdown(f"**Target Niche:** `{config.TARGET_NICHE}`")
st.sidebar.markdown(f"**Brand:** `{config.CAMPAIGN_BRAND_NAME}`")
st.sidebar.markdown(f"**Campaign:** `{config.CAMPAIGN_TYPE}`")

st.sidebar.divider()
st.sidebar.subheader("Filter Thresholds")
st.sidebar.markdown(f"- Followers: `{config.MIN_FOLLOWERS:,}` to `{config.MAX_FOLLOWERS:,}`")
st.sidebar.markdown(f"- Min Engagement: `{config.MIN_ENGAGEMENT_RATE:.1f}%`")

st.sidebar.divider()
st.sidebar.subheader("Execution Controls")
run_pipeline_btn = st.sidebar.button("▶ Run Full Pipeline", type="primary", use_container_width=True)
reset_db_btn = st.sidebar.button("🔄 Reset Tracker Database", use_container_width=True)

if reset_db_btn:
    tracker = OutreachTracker()
    tracker.clear_tracker()
    st.sidebar.success("Outreach tracker database reset!")
    st.rerun()

if run_pipeline_btn:
    with st.spinner("Executing discovery, filtering, enrichment, AI generation, and outreach..."):
        pipeline = MicroInfluencerPipeline()
        summary = pipeline.run_full_pipeline()
        st.sidebar.success("Pipeline executed successfully!")
        st.rerun()

# Main Header
st.title("🎯 Automated Micro-Influencer Outreach System")
st.caption("AI-Powered Discovery, Rule-Based Classification, Profile Enrichment, and Multi-Channel Outreach Pipeline")

# Load Datasets
df_creators = load_data()
df_logs = load_db_logs()

# Metric Banners
col1, col2, col3, col4, col5 = st.columns(5)
total_discovered = len(df_creators) if not df_creators.empty else 0
passed_count = len(df_creators[df_creators["Status"] == "PASSED"]) if not df_creators.empty else 0
failed_count = len(df_creators[df_creators["Status"] == "FAILED"]) if not df_creators.empty else 0
valid_emails = len(df_creators[(df_creators["Status"] == "PASSED") & (df_creators["Email"] != "Not Found")]) if not df_creators.empty else 0
outreach_logged = len(df_logs) if not df_logs.empty else 0

with col1:
    st.metric("Discovered Profiles", total_discovered)
with col2:
    st.metric("Shortlisted (Passed)", passed_count)
with col3:
    st.metric("Filtered Out (Failed)", failed_count)
with col4:
    st.metric("Verified Emails", valid_emails)
with col5:
    st.metric("Outreach Events", outreach_logged)

st.divider()

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Influencer Discovery & Filtering",
    "✍️ AI Message Personalization",
    "📬 Sending Hub & Outreach Tracker",
    "ℹ️ System Architecture & Logic"
])

# TAB 1: Discovery & Filtering
with tab1:
    st.subheader("Discovered Creators & Classification Results")
    st.markdown("Each discovered profile is evaluated against follower range, engagement thresholds, niche relevance, and brand alignment.")

    if not df_creators.empty:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            search_query = st.text_input("🔍 Search creator name, platform, or theme:", "")
        with c2:
            status_filter = st.selectbox("Filter by Status", ["All", "PASSED", "FAILED"])
        with c3:
            platform_filter = st.selectbox("Platform", ["All", "Instagram", "YouTube", "TikTok"])

        filtered_view = df_creators.copy()
        if status_filter != "All":
            filtered_view = filtered_view[filtered_view["Status"] == status_filter]
        if platform_filter != "All":
            filtered_view = filtered_view[filtered_view["Platform"] == platform_filter]
        if search_query:
            q = search_query.lower()
            filtered_view = filtered_view[
                filtered_view["Name"].str.lower().str.contains(q, na=False) |
                filtered_view["Content Theme"].str.lower().str.contains(q, na=False) |
                filtered_view["Platform"].str.lower().str.contains(q, na=False)
            ]

        # Display Data Table
        display_cols = ["Name", "Platform", "Followers", "Engagement", "Niche", "Email", "Status", "Filter Reason"]
        st.dataframe(filtered_view[display_cols], use_container_width=True, height=420)

        # Download Button
        csv_data = filtered_view.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Current Filtered Table (CSV)",
            data=csv_data,
            file_name="micro_influencers_filtered.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data found. Click '▶ Run Full Pipeline' in the sidebar to run the system.")

# TAB 2: AI Message Personalization
with tab2:
    st.subheader("Tailored Outreach Copy Review")
    st.markdown("AI generates bespoke **Email pitches (strictly 60–90 words)** and **Instagram DMs (strictly 15–30 words)** dynamically for shortlisted creators.")

    if not df_creators.empty:
        shortlisted = df_creators[df_creators["Status"] == "PASSED"].reset_index(drop=True)
        if not shortlisted.empty:
            creator_names = shortlisted["Name"].tolist()
            selected_name = st.selectbox("Select a qualified creator to review messages:", creator_names)

            selected_row = shortlisted[shortlisted["Name"] == selected_name].iloc[0]

            col_info, col_messages = st.columns([1, 2])

            with col_info:
                st.markdown(f"### {selected_row['Name']}")
                st.markdown(f"**Platform:** {selected_row['Platform']}")
                st.markdown(f"**Followers:** {selected_row['Followers']:,}")
                st.markdown(f"**Engagement Rate:** {selected_row['Engagement']}")
                st.markdown(f"**Category:** {selected_row['Niche']}")
                st.markdown(f"**Contact Email:** `{selected_row['Email']}`")
                st.markdown(f"**Content Themes:** {selected_row['Content Theme']}")
                st.markdown(f"[View Profile Page]({selected_row['Profile URL']})")

            with col_messages:
                # Email Pitch Box
                st.markdown("#### 📧 Email Collaboration Pitch")
                email_wc = int(selected_row["Email Word Count"]) if pd.notnull(selected_row["Email Word Count"]) else 0
                wc_badge = "✅ Compliant (60-90 words)" if 60 <= email_wc <= 90 else f"⚠️ {email_wc} words"
                st.caption(f"Word Count: **{email_wc} words** | Requirement: 60–90 words | {wc_badge}")

                edited_email = st.text_area("Email Body", selected_row["Email Pitch"], height=160)

                # Instagram DM Box
                st.markdown("#### 💬 Instagram DM")
                dm_wc = int(selected_row["DM Word Count"]) if pd.notnull(selected_row["DM Word Count"]) else 0
                dm_badge = "✅ Compliant (15-30 words)" if 15 <= dm_wc <= 30 else f"⚠️ {dm_wc} words"
                st.caption(f"Word Count: **{dm_wc} words** | Requirement: 15–30 words | {dm_badge}")

                edited_dm = st.text_area("Instagram DM Body", selected_row["Instagram DM"], height=80)

                st.info("💡 Changes made here allow human-in-the-loop review before final dispatch.")
        else:
            st.info("No creators have passed the filter yet.")
    else:
        st.warning("Please run the pipeline first to generate outreach copy.")

# TAB 3: Sending Hub & Outreach Tracker
with tab3:
    st.subheader("Outreach Dispatcher & Audit Log")
    st.markdown("Tracks all outgoing communication attempts, prevents duplicate contact, and records delivery statuses in SQLite.")

    if not df_logs.empty:
        c_filter1, c_filter2 = st.columns(2)
        with c_filter1:
            chan_filter = st.selectbox("Channel", ["All", "EMAIL", "INSTAGRAM_DM"])
        with c_filter2:
            status_filter = st.selectbox("Status", ["All"] + list(df_logs["status"].unique()))

        logs_view = df_logs.copy()
        if chan_filter != "All":
            logs_view = logs_view[logs_view["channel"] == chan_filter]
        if status_filter != "All":
            logs_view = logs_view[logs_view["status"] == status_filter]

        st.dataframe(
            logs_view[["sent_at", "influencer_name", "platform", "email", "channel", "status", "notes"]],
            use_container_width=True,
            height=350
        )

        st.download_button(
            label="📥 Export Outreach Audit Log (CSV)",
            data=logs_view.to_csv(index=False).encode('utf-8'),
            file_name="outreach_audit_log.csv",
            mime="text/csv"
        )
    else:
        st.info("No outreach logs recorded in database yet.")

# TAB 4: Architecture & Methodology
with tab4:
    st.subheader("System Architecture & Workflow Design")
    st.markdown("""
    ### 1. Influencer Discovery Layer
    - **Candidate Pool:** Queries social media creators across Instagram, YouTube, and TikTok within the targeted niche.
    - **Scale:** Evaluates 50+ candidates per batch.
    - **Data Integrity:** Strict capture of real profile URLs, verified subscriber counts, and engagement figures.

    ### 2. Filtering & Classification Engine
    - **Follower Floor & Ceiling:** Micro-influencer standard of `5,000` to `100,000` followers.
    - **Engagement Quality Floor:** Requires `≥ 2.0%` average engagement rate.
    - **Category & Brand Fit:** Assesses content themes and post captions against brand keywords.
    - **Auditability:** Every single candidate receives an explicit `PASSED` or `FAILED` status with an explanatory reason string.

    ### 3. Profile Enrichment
    - **Mandatory Attributes:** Full Name, Platform, Profile URL, Follower Count, Engagement Rate, Category, Content Themes, and Contact Email.
    - **Email Protocol:** If an email is absent from public bio, it is explicitly preserved as **`Not Found`** without guessing or hallucinating.
    - **Demographic Attribution:** Audience age, gender split, and primary geographies are mapped.

    ### 4. AI Message Personalization
    - **Email Pitch:** Dynamically crafted at **60–90 words**, referencing specific recent content titles, tone of voice, and proposing structured collaborations (UGC, Barter, Sponsorship).
    - **Instagram DM:** Casual, high-converting hook at **15–30 words**.
    - **Fallback Guarantee:** Integrated contextual dynamic engine ensures 100% uptime even if external LLM API keys are unset or rate-limited.

    ### 5. Sending Layer & Duplicate Suppression
    - **Email Dispatch:** Integrates SMTP and simulated Dry-Run delivery. Filters out records where email is `Not Found`.
    - **Duplicate Prevention:** Checks email and creator ID indexes in SQLite before sending, stopping redundant outreach.
    - **Meta/Instagram Terms Compliance:** Avoids unauthorized DM botting by offering a simulated dispatch and manual copy workflow.
    """)
