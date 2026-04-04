import os
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine


st.set_page_config(
    page_title="Brewery Data Portal",
    page_icon="🏢",
    layout="wide",
)


load_dotenv()


def get_secret(name: str) -> str | None:
    if name in st.secrets:
        return st.secrets[name]
    return os.getenv(name)


@st.cache_data
def get_brewery_data():
    db_url = get_secret("SUPABASE_DB_URL")

    if not db_url:
        st.error("ไม่พบ SUPABASE_DB_URL")
        st.info(
            "บน Streamlit Cloud ให้เพิ่มค่าใน App Settings > Secrets โดยใส่บรรทัด "
            '`SUPABASE_DB_URL = "postgresql://..."`'
        )
        return pd.DataFrame()

    engine = create_engine(db_url)
    return pd.read_sql(
        "SELECT * FROM dbt_chotiratwithgit_public.stg_breweries",
        engine,
    )


st.title("🏢 Brewery Data Portal")
st.markdown("ระบบศูนย์กลางข้อมูลสำหรับการวิเคราะห์และปฏิบัติการ (Self-Service Analytics)")

df_breweries = get_brewery_data()

if df_breweries.empty:
    st.stop()

required_columns = ["id", "brewery_name", "brewery_type", "city", "state_name", "country"]
missing_columns = [col for col in required_columns if col not in df_breweries.columns]

if missing_columns:
    st.error(f"ไม่พบคอลัมน์ที่จำเป็น: {', '.join(missing_columns)}")
    st.write("Available columns:", df_breweries.columns.tolist())
    st.stop()


selected_type = sorted(df_breweries["brewery_type"].dropna().unique())
selected_state = sorted(df_breweries["state_name"].dropna().unique())
search_name = ""
filtered_df = df_breweries.copy()
quarantine_df = pd.DataFrame()


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Executive Overview",
    "🔍 Data Explorer",
    "📥 Data Download",
    "📑 Saved Reports",
    "🚨 Quarantine",
    "⚙️ Pipeline Health",
])


with tab1:
    st.subheader("ภาพรวมข้อมูลโรงเบียร์")

    total_breweries = len(df_breweries)
    total_types = df_breweries["brewery_type"].nunique()
    total_states = df_breweries["state_name"].nunique()
    total_countries = df_breweries["country"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Breweries ทั้งหมด", total_breweries)
    col2.metric("Brewery Types", total_types)
    col3.metric("States Covered", total_states)
    col4.metric("Countries", total_countries)

    st.divider()
    left, right = st.columns(2)

    with left:
        st.write("📍 Breweries by Type")
        st.bar_chart(df_breweries["brewery_type"].value_counts())

    with right:
        st.write("📖 Top States with Breweries")
        st.bar_chart(df_breweries["state_name"].value_counts().head(10))

    st.divider()
    st.write("🌍 Top Cities")
    top_cities = df_breweries["city"].value_counts().reset_index()
    top_cities.columns = ["city", "brewery_count"]
    st.dataframe(top_cities.head(10), use_container_width=True, hide_index=True)


with tab2:
    st.subheader("Brewery Explorer")
    st.info("💡 ค้นหา กรอง และตรวจข้อมูลโรงเบียร์จากหน้านี้")

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        selected_type = st.multiselect(
            "เลือกประเภทโรงเบียร์ (Brewery Type)",
            options=sorted(df_breweries["brewery_type"].dropna().unique()),
            default=selected_type,
        )
    with col_filter2:
        selected_state = st.multiselect(
            "เลือก รัฐ (State)",
            options=sorted(df_breweries["state_name"].dropna().unique()),
            default=selected_state,
        )

    search_name = st.text_input("ค้นหาชื่อโรงเบียร์ (Search by Name)")

    filtered_df = df_breweries[
        df_breweries["brewery_type"].isin(selected_type)
        & df_breweries["state_name"].isin(selected_state)
    ].copy()

    if search_name:
        filtered_df = filtered_df[
            filtered_df["brewery_name"].str.contains(search_name, case=False, na=False)
        ]

    st.caption(f"พบข้อมูล {len(filtered_df):,} รายการ")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)


with tab3:
    st.subheader("Data Download")
    st.markdown("ดาวน์โหลดข้อมูลที่กรองจากหน้า Data Explorer ได้โดยตรง")

    export_columns = st.multiselect(
        "เลือกคอลัมน์สำหรับดาวน์โหลด",
        options=filtered_df.columns.tolist(),
        default=filtered_df.columns.tolist(),
    )

    export_df = filtered_df[export_columns] if export_columns else filtered_df.copy()

    st.caption(f"พร้อมดาวน์โหลด {len(export_df):,} รายการ")
    st.dataframe(export_df, use_container_width=True, hide_index=True)
    st.download_button(
        "📥 Download Filtered Data (CSV)",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_breweries.csv",
        mime="text/csv",
    )


with tab4:
    st.subheader("Standard Data Reports (รายงานมาตรฐาน)")
    report_type = st.selectbox(
        "รายงาน",
        [
            "จำนวนโรงเบียร์ตามประเภท (Breweries by Type)",
            "จำนวนโรงเบียร์ตามรัฐ (Breweries by State)",
            "เมืองที่มีโรงเบียร์มากที่สุด (Top Cities)",
        ],
    )

    if report_type == "จำนวนโรงเบียร์ตามรัฐ (Breweries by State)":
        report_df = filtered_df["state_name"].value_counts().reset_index()
        report_df.columns = ["state_name", "brewery_count"]
    elif report_type == "จำนวนโรงเบียร์ตามประเภท (Breweries by Type)":
        report_df = filtered_df["brewery_type"].value_counts().reset_index()
        report_df.columns = ["brewery_type", "brewery_count"]
    else:
        report_df = filtered_df["city"].value_counts().reset_index()
        report_df.columns = ["city", "brewery_count"]

    st.dataframe(report_df, use_container_width=True, hide_index=True)
    st.download_button(
        "📥 Download Report (CSV)",
        data=report_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{report_type.replace(' ', '_')}.csv",
        mime="text/csv",
    )


with tab5:
    st.subheader("Data Quality (คุณภาพข้อมูล)")
    st.markdown("รายการที่ควรตรวจสอบก่อนนำข้อมูลไปใช้วิเคราะห์หรือรายงาน")

    df_qc = df_breweries.copy()
    issues = []

    for _, row in df_qc.iterrows():
        if pd.isna(row["id"]) or str(row["id"]).strip() == "":
            issues.append({**row.to_dict(), "issue": "Missing ID"})
        elif pd.isna(row["brewery_name"]) or str(row["brewery_name"]).strip() == "":
            issues.append({**row.to_dict(), "issue": "Missing Brewery Name"})
        elif pd.isna(row["brewery_type"]) or str(row["brewery_type"]).strip() == "":
            issues.append({**row.to_dict(), "issue": "Missing Brewery Type"})
        elif pd.isna(row["city"]) or str(row["city"]).strip() == "":
            issues.append({**row.to_dict(), "issue": "Missing City"})
        elif pd.isna(row["state_name"]) or str(row["state_name"]).strip() == "":
            issues.append({**row.to_dict(), "issue": "Missing State Name"})
        elif pd.isna(row["country"]) or str(row["country"]).strip() == "":
            issues.append({**row.to_dict(), "issue": "Missing Country"})

    dup_id = df_qc[df_qc["id"].duplicated(keep=False)]
    for _, row in dup_id.iterrows():
        issues.append({**row.to_dict(), "issue": "Duplicate ID"})

    quarantine_df = pd.DataFrame(issues).drop_duplicates()

    st.metric("Records with Issues", len(quarantine_df))

    if quarantine_df.empty:
        st.success("✅ ไม่พบข้อมูลผิดปกติ (No data quality issues found)")
    else:
        st.dataframe(quarantine_df, use_container_width=True, hide_index=True)
        st.download_button(
            "📥 Download Data Quality Issues (CSV)",
            data=quarantine_df.to_csv(index=False).encode("utf-8"),
            file_name="data_quality_issues.csv",
            mime="text/csv",
        )


with tab6:
    st.subheader("Pipeline Health (สถานะระบบหลังบ้าน)")
    st.markdown("ตรวจสอบสถานะการทำงานของระบบและประสิทธิภาพของกระบวนการ ETL")

    quarantine_count = len(quarantine_df)
    total_records = len(df_breweries)
    valid_records = total_records - quarantine_count
    last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", total_records)
    col2.metric("Valid Records", valid_records)
    col3.metric("Quarantine Records", quarantine_count)
    col4.metric("Last Refresh", last_refresh)

    st.divider()

    pipeline_status = "healthy" if quarantine_count == 0 else "warning"
    st.write("Pipeline Status:")
    if pipeline_status == "healthy":
        st.success("✅ ระบบทำงานปกติ (All systems operational)")
    else:
        st.warning("⚠️ ระบบมีปัญหา (System has issues)")

    st.write("รายละเอียด:")
    st.code(
        """Source: Supabase PostgreSQL
Data Domain: Brewery Master Data
Load Method: SQL query
Environment: Local, Streamlit"""
    )

    st.write("System Logs:")
    st.text_area(
        "Logs",
        value=(
            f"INFO: Loaded {total_records} records from Supabase\n"
            f"INFO: Valid records: {valid_records}\n"
            f"INFO: Quarantine records: {quarantine_count}\n"
            f"INFO: Last refresh at {last_refresh}\n"
        ),
        height=180,
    )
