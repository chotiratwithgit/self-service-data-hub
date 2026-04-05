import os           # นำเข้าโมดูล `os` เพื่อใช้เข้าถึงตัวแปรสภาพแวดล้อมของระบบ
from datetime import datetime       # นำเข้า `datetime` เพื่อใช้สร้างเวลาปัจจุบันสำหรับแสดงสถานะการรีเฟรชข้อมูล
import pandas as pd         # นำเข้า `pandas` และย่อชื่อเป็น `pd` สำหรับจัดการข้อมูลแบบตาราง
import streamlit as st      # นำเข้า `streamlit` และย่อชื่อเป็น `st` เพื่อสร้างหน้าเว็บแอป
from dotenv import load_dotenv      # นำเข้า `load_dotenv` เพื่ออ่านค่าจากไฟล์ `.env`
from sqlalchemy import create_engine        # นำเข้า `create_engine` เพื่อใช้สร้างตัวเชื่อมต่อฐานข้อมูลผ่าน SQLAlchemy


# ตั้งค่าพื้นฐานของหน้า Streamlit ก่อนเริ่มวาด UI ส่วนอื่น
st.set_page_config(
    # ชื่อที่จะแสดงบนแท็บของเบราว์เซอร์
    page_title="Brewery Data Portal",
    # ไอคอนประจำหน้าเว็บ
    page_icon="🏢",
    # ใช้ layout แบบกว้างเพื่อให้แสดง dashboard ได้เต็มพื้นที่
    layout="wide",
)


# โหลดค่าจากไฟล์ `.env` เข้ามาเป็น environment variables
load_dotenv()


# ฟังก์ชันนี้ใช้ดึงค่าความลับหรือค่าคอนฟิกจากสองแหล่งตามลำดับความสำคัญ
def get_secret(name: str) -> str | None:
    # ถ้าชื่อคีย์นี้มีอยู่ในระบบ `st.secrets` ของ Streamlit
    if name in st.secrets:
        # คืนค่าจาก `st.secrets` ทันที
        return st.secrets[name]
    # ถ้าไม่มีใน `st.secrets` ให้ลองอ่านจาก environment variables แทน
    return os.getenv(name)


# ใช้ cache เพื่อไม่ต้องโหลดข้อมูลจากฐานข้อมูลใหม่ทุกครั้งที่หน้า re-run
@st.cache_data
# ฟังก์ชันนี้ใช้ดึงข้อมูลโรงเบียร์จากฐานข้อมูล Supabase
def get_brewery_data():
    # อ่าน URL สำหรับเชื่อมต่อฐานข้อมูลจาก secret ชื่อ `SUPABASE_DB_URL`
    db_url = get_secret("SUPABASE_DB_URL")

    # ถ้าไม่มีค่า URL แปลว่ายังตั้งค่าการเชื่อมต่อฐานข้อมูลไม่ครบ
    if not db_url:
        # แจ้ง error ให้ผู้ใช้เห็นชัด ๆ ว่าไม่พบค่าที่จำเป็น
        st.error("ไม่พบ SUPABASE_DB_URL")
        # แสดงคำแนะนำเพิ่มเติมสำหรับกรณีที่แอปรันอยู่บน Streamlit Cloud
        st.info(
            # บอกตำแหน่งที่ต้องนำค่าไปเพิ่มในหน้า Settings
            "บน Streamlit Cloud ให้เพิ่มค่าใน App Settings > Secrets โดยใส่บรรทัด "
            # แสดงตัวอย่างรูปแบบ secret ที่ถูกต้อง
            '`SUPABASE_DB_URL = "postgresql://..."`'
        )
        # คืนค่า DataFrame ว่าง เพื่อให้โค้ดส่วนล่างรู้ว่าไม่มีข้อมูลให้ใช้งาน
        return pd.DataFrame()

    # สร้าง database engine จาก URL ที่ได้มา
    engine = create_engine(db_url)
    # รันคำสั่ง SQL เพื่อดึงข้อมูลทั้งหมดจากตาราง staging ของ breweries
    return pd.read_sql(
        # คำสั่ง SQL สำหรับอ่านข้อมูลทั้งหมด
        "SELECT * FROM dbt_chotiratwithgit_public.stg_breweries",
        # ส่ง engine ให้ `read_sql` ใช้เชื่อมต่อฐานข้อมูล
        engine,
    )


# แสดงหัวข้อหลักของหน้า dashboard
st.title("🏢 Brewery Data Portal")
# แสดงคำอธิบายสั้น ๆ ของระบบใต้หัวข้อหลัก
st.markdown("ระบบศูนย์กลางข้อมูลสำหรับการวิเคราะห์และปฏิบัติการ (Self-Service Analytics)")

# เรียกฟังก์ชันโหลดข้อมูลทั้งหมดจากฐานข้อมูล
df_breweries = get_brewery_data()

# ถ้า DataFrame ว่าง แสดงว่าโหลดข้อมูลไม่ได้หรือไม่มีข้อมูลให้แสดง
if df_breweries.empty:
    # หยุดการทำงานของแอปทันทีเพื่อป้องกัน error ในโค้ดส่วนถัดไป
    st.stop()

# ระบุคอลัมน์สำคัญที่ทุกหน้าภายใน dashboard ต้องใช้
required_columns = ["id", "brewery_name", "brewery_type", "city", "state_name", "country"]
# ตรวจว่ามีคอลัมน์ใดหายไปจากชุดข้อมูลที่โหลดมาหรือไม่
missing_columns = [col for col in required_columns if col not in df_breweries.columns]

# ถ้ามีคอลัมน์ที่จำเป็นหายไป
if missing_columns:
    # แสดงรายชื่อคอลัมน์ที่ขาด เพื่อให้ตรวจสอบแหล่งข้อมูลได้ง่าย
    st.error(f"ไม่พบคอลัมน์ที่จำเป็น: {', '.join(missing_columns)}")
    # แสดงรายชื่อคอลัมน์ที่มีอยู่จริงใน DataFrame ปัจจุบัน
    st.write("Available columns:", df_breweries.columns.tolist())
    # หยุดการทำงาน เพราะส่วนอื่นของหน้าอาศัยคอลัมน์เหล่านี้
    st.stop()


# เตรียมค่าเริ่มต้นของตัวกรองประเภทโรงเบียร์ โดยใช้ทุกค่าที่ไม่ว่างและเรียงลำดับแล้ว
selected_type = sorted(df_breweries["brewery_type"].dropna().unique())
# เตรียมค่าเริ่มต้นของตัวกรองรัฐ โดยใช้ทุกค่าที่ไม่ว่างและเรียงลำดับแล้ว
selected_state = sorted(df_breweries["state_name"].dropna().unique())
# กำหนดค่าเริ่มต้นของช่องค้นหาชื่อโรงเบียร์ให้เป็นสตริงว่าง
search_name = ""
# เริ่มต้นข้อมูลที่ถูกกรองให้เท่ากับข้อมูลทั้งหมดก่อน
filtered_df = df_breweries.copy()
# สร้าง DataFrame ว่างไว้ก่อนสำหรับเก็บข้อมูลที่มีปัญหาในแท็บ Quarantine
quarantine_df = pd.DataFrame()


# สร้างแท็บหลัก 6 แท็บ แล้วเก็บออบเจ็กต์แท็บแต่ละตัวไว้ใช้งานต่อ
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    # แท็บสรุปภาพรวมสำหรับผู้บริหาร
    "📊 Executive Overview",
    # แท็บสำหรับสำรวจและค้นหาข้อมูล
    "🔍 Data Explorer",
    # แท็บสำหรับดาวน์โหลดข้อมูลที่กรองแล้ว
    "📥 Data Download",
    # แท็บสำหรับรายงานสำเร็จรูป
    "📑 Saved Reports",
    # แท็บสำหรับข้อมูลที่ต้องกักไว้เพราะมีปัญหาด้านคุณภาพ
    "🚨 Quarantine",
    # แท็บสำหรับติดตามสถานะระบบและ pipeline
    "⚙️ Pipeline Health",
])


# เริ่มเนื้อหาภายในแท็บที่ 1: Executive Overview
with tab1:
    # แสดงหัวข้อย่อยของแท็บภาพรวมข้อมูล
    st.subheader("ภาพรวมข้อมูลโรงเบียร์")

    # นับจำนวนแถวทั้งหมดในชุดข้อมูลโรงเบียร์
    total_breweries = len(df_breweries)
    # นับจำนวนประเภทโรงเบียร์ที่ไม่ซ้ำกัน
    total_types = df_breweries["brewery_type"].nunique()
    # นับจำนวนรัฐที่มีอยู่ในข้อมูลแบบไม่ซ้ำกัน
    total_states = df_breweries["state_name"].nunique()
    # นับจำนวนประเทศที่มีอยู่ในข้อมูลแบบไม่ซ้ำกัน
    total_countries = df_breweries["country"].nunique()

    # แบ่งพื้นที่เป็น 4 คอลัมน์เพื่อวาง KPI cards
    col1, col2, col3, col4 = st.columns(4)
    # แสดงจำนวนโรงเบียร์ทั้งหมด
    col1.metric("Breweries ทั้งหมด", total_breweries)
    # แสดงจำนวนประเภทโรงเบียร์
    col2.metric("Brewery Types", total_types)
    # แสดงจำนวนรัฐที่ครอบคลุม
    col3.metric("States Covered", total_states)
    # แสดงจำนวนประเทศที่ครอบคลุม
    col4.metric("Countries", total_countries)

    # แทรกเส้นคั่นก่อนเข้าส่วนกราฟ
    st.divider()
    # แบ่งพื้นที่สำหรับแสดงกราฟออกเป็น 2 คอลัมน์
    left, right = st.columns(2)

    # เริ่มเนื้อหาของคอลัมน์ซ้าย
    with left:
        # แสดงหัวข้อกำกับกราฟแท่ง
        st.write("📍 Breweries by Type")
        # แสดงกราฟแท่งจำนวนโรงเบียร์แยกตามประเภท
        st.bar_chart(df_breweries["brewery_type"].value_counts())

    # เริ่มเนื้อหาของคอลัมน์ขวา
    with right:
        # แสดงหัวข้อกำกับกราฟแท่ง
        st.write("📖 Top States with Breweries")
        # แสดงกราฟแท่ง 10 รัฐที่มีจำนวนโรงเบียร์มากที่สุด
        st.bar_chart(df_breweries["state_name"].value_counts().head(10))

    # แทรกเส้นคั่นก่อน section ตารางเมืองยอดนิยม
    st.divider()
    # แสดงหัวข้อของตารางสรุปเมือง
    st.write("🌍 Top Cities")
    # นับจำนวนโรงเบียร์ต่อเมือง แล้วแปลงผลลัพธ์เป็น DataFrame
    top_cities = df_breweries["city"].value_counts().reset_index()
    # เปลี่ยนชื่อคอลัมน์ให้สื่อความหมายมากขึ้น
    top_cities.columns = ["city", "brewery_count"]
    # แสดงเฉพาะ 10 เมืองแรก พร้อมซ่อน index และใช้ความกว้างเต็มพื้นที่
    st.dataframe(top_cities.head(10), use_container_width=True, hide_index=True)


# เริ่มเนื้อหาภายในแท็บที่ 2: Data Explorer
with tab2:
    # แสดงหัวข้อย่อยของแท็บสำหรับสำรวจข้อมูล
    st.subheader("Brewery Explorer")
    # แสดงข้อความแนะนำว่าหน้านี้ใช้ค้นหาและกรองข้อมูลได้
    st.info("💡 ค้นหา กรอง และตรวจข้อมูลโรงเบียร์จากหน้านี้")

    # แบ่งพื้นที่เป็น 2 คอลัมน์เพื่อวางตัวกรองสองชุด
    col_filter1, col_filter2 = st.columns(2)
    # เริ่มส่วนตัวกรองคอลัมน์ซ้าย
    with col_filter1:
        # สร้างกล่องเลือกหลายค่า สำหรับกรองประเภทโรงเบียร์
        selected_type = st.multiselect(
            # ข้อความกำกับตัวกรองประเภท
            "เลือกประเภทโรงเบียร์ (Brewery Type)",
            # ตัวเลือกทั้งหมดของประเภทโรงเบียร์จากข้อมูลจริง
            options=sorted(df_breweries["brewery_type"].dropna().unique()),
            # ค่าเริ่มต้นคือเลือกทุกประเภทที่มีอยู่
            default=selected_type,
        )
    # เริ่มส่วนตัวกรองคอลัมน์ขวา
    with col_filter2:
        # สร้างกล่องเลือกหลายค่า สำหรับกรองรัฐ
        selected_state = st.multiselect(
            # ข้อความกำกับตัวกรองรัฐ
            "เลือก รัฐ (State)",
            # ตัวเลือกทั้งหมดของรัฐจากข้อมูลจริง
            options=sorted(df_breweries["state_name"].dropna().unique()),
            # ค่าเริ่มต้นคือเลือกทุกรัฐที่มีอยู่
            default=selected_state,
        )

    # สร้างช่องค้นหาด้วยข้อความสำหรับค้นหาชื่อโรงเบียร์
    search_name = st.text_input("ค้นหาชื่อโรงเบียร์ (Search by Name)")

    # กรองข้อมูลตามประเภทและรัฐที่ผู้ใช้เลือก
    filtered_df = df_breweries[
        # เงื่อนไขแรก: ประเภทโรงเบียร์ต้องอยู่ในรายการที่เลือก
        df_breweries["brewery_type"].isin(selected_type)
        # เงื่อนไขที่สอง: รัฐต้องอยู่ในรายการที่เลือก
        & df_breweries["state_name"].isin(selected_state)
        # ทำสำเนาผลลัพธ์ไว้ใช้งานต่อ เพื่อไม่ให้ไปผูกกับ DataFrame ต้นฉบับโดยตรง
    ].copy()

    # ถ้าผู้ใช้กรอกข้อความค้นหาเข้ามา
    if search_name:
        # กรองต่อเฉพาะแถวที่ชื่อโรงเบียร์มีข้อความนั้น โดยไม่สนตัวพิมพ์เล็กหรือใหญ่
        filtered_df = filtered_df[
            filtered_df["brewery_name"].str.contains(search_name, case=False, na=False)
        ]

    # แสดงจำนวนข้อมูลที่เหลือหลังการกรอง
    st.caption(f"พบข้อมูล {len(filtered_df):,} รายการ")
    # แสดงตารางข้อมูลที่กรองแล้ว
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)


# เริ่มเนื้อหาภายในแท็บที่ 3: Data Download
with tab3:
    # แสดงหัวข้อย่อยของแท็บดาวน์โหลดข้อมูล
    st.subheader("Data Download")
    # อธิบายว่าข้อมูลที่ดาวน์โหลดจะอิงจากผลการกรองในหน้า Data Explorer
    st.markdown("ดาวน์โหลดข้อมูลที่กรองจากหน้า Data Explorer ได้โดยตรง")

    # ให้ผู้ใช้เลือกคอลัมน์ที่ต้องการส่งออก
    export_columns = st.multiselect(
        # ป้ายกำกับของกล่องเลือกคอลัมน์
        "เลือกคอลัมน์สำหรับดาวน์โหลด",
        # แสดงตัวเลือกเป็นรายชื่อคอลัมน์ทั้งหมดของข้อมูลที่กรองแล้ว
        options=filtered_df.columns.tolist(),
        # ค่าเริ่มต้นคือเลือกทุกคอลัมน์
        default=filtered_df.columns.tolist(),
    )

    # ถ้ามีการเลือกคอลัมน์ ให้ตัดเฉพาะคอลัมน์นั้นออกมา ไม่เช่นนั้นใช้ข้อมูลทั้งหมด
    export_df = filtered_df[export_columns] if export_columns else filtered_df.copy()

    # แสดงจำนวนแถวที่พร้อมสำหรับการดาวน์โหลด
    st.caption(f"พร้อมดาวน์โหลด {len(export_df):,} รายการ")
    # แสดง preview ของข้อมูลที่จะส่งออก
    st.dataframe(export_df, use_container_width=True, hide_index=True)
    # สร้างปุ่มสำหรับดาวน์โหลดข้อมูลในรูปแบบ CSV
    st.download_button(
        # ข้อความบนปุ่มดาวน์โหลด
        "📥 Download Filtered Data (CSV)",
        # แปลง DataFrame เป็น CSV แบบไม่เอา index และเข้ารหัสเป็น UTF-8
        data=export_df.to_csv(index=False).encode("utf-8"),
        # ตั้งชื่อไฟล์เวลาผู้ใช้กดดาวน์โหลด
        file_name="filtered_breweries.csv",
        # ระบุชนิดไฟล์ให้เบราว์เซอร์รู้ว่าเป็น CSV
        mime="text/csv",
    )


# เริ่มเนื้อหาภายในแท็บที่ 4: Saved Reports
with tab4:
    # แสดงหัวข้อย่อยของแท็บรายงานมาตรฐาน
    st.subheader("Standard Data Reports (รายงานมาตรฐาน)")
    # สร้าง selectbox ให้ผู้ใช้เลือกรูปแบบรายงานที่ต้องการ
    report_type = st.selectbox(
        # ป้ายกำกับของ selectbox
        "รายงาน",
        # รายการตัวเลือกของรายงานมาตรฐานที่รองรับ
        [
            "จำนวนโรงเบียร์ตามประเภท (Breweries by Type)",
            "จำนวนโรงเบียร์ตามรัฐ (Breweries by State)",
            "เมืองที่มีโรงเบียร์มากที่สุด (Top Cities)",
        ],
    )

    # ถ้าผู้ใช้เลือกรายงานสรุปจำนวนโรงเบียร์ตามรัฐ
    if report_type == "จำนวนโรงเบียร์ตามรัฐ (Breweries by State)":
        # นับจำนวนโรงเบียร์แยกตามรัฐ แล้วแปลงผลลัพธ์กลับเป็น DataFrame
        report_df = filtered_df["state_name"].value_counts().reset_index()
        # เปลี่ยนชื่อคอลัมน์ให้อ่านง่ายและพร้อมนำไปแสดงผล
        report_df.columns = ["state_name", "brewery_count"]
    # ถ้าผู้ใช้เลือกรายงานสรุปจำนวนโรงเบียร์ตามประเภท
    elif report_type == "จำนวนโรงเบียร์ตามประเภท (Breweries by Type)":
        # นับจำนวนโรงเบียร์แยกตามประเภท แล้วแปลงผลลัพธ์กลับเป็น DataFrame
        report_df = filtered_df["brewery_type"].value_counts().reset_index()
        # เปลี่ยนชื่อคอลัมน์ให้อ่านง่ายและพร้อมนำไปแสดงผล
        report_df.columns = ["brewery_type", "brewery_count"]
    # กรณีที่ไม่ใช่สองเงื่อนไขด้านบน ให้ถือว่าเป็นรายงาน Top Cities
    else:
        # นับจำนวนโรงเบียร์แยกตามเมือง แล้วแปลงผลลัพธ์กลับเป็น DataFrame
        report_df = filtered_df["city"].value_counts().reset_index()
        # เปลี่ยนชื่อคอลัมน์ให้อ่านง่ายและพร้อมนำไปแสดงผล
        report_df.columns = ["city", "brewery_count"]

    # แสดงตารางรายงานที่คำนวณเสร็จแล้ว
    st.dataframe(report_df, use_container_width=True, hide_index=True)
    # สร้างปุ่มดาวน์โหลดรายงานในรูปแบบ CSV
    st.download_button(
        # ข้อความบนปุ่มดาวน์โหลด
        "📥 Download Report (CSV)",
        # แปลงรายงานเป็น CSV แบบ UTF-8
        data=report_df.to_csv(index=False).encode("utf-8"),
        # ตั้งชื่อไฟล์ตามชื่อรายงานที่เลือก โดยแทนช่องว่างด้วย `_`
        file_name=f"{report_type.replace(' ', '_')}.csv",
        # ระบุชนิดไฟล์เป็น CSV
        mime="text/csv",
    )


# เริ่มเนื้อหาภายในแท็บที่ 5: Quarantine
with tab5:
    # แสดงหัวข้อย่อยของแท็บตรวจคุณภาพข้อมูล
    st.subheader("Data Quality (คุณภาพข้อมูล)")
    # อธิบายว่าข้อมูลส่วนนี้คือรายการที่ควรตรวจสอบก่อนนำไปใช้จริง
    st.markdown("รายการที่ควรตรวจสอบก่อนนำข้อมูลไปใช้วิเคราะห์หรือรายงาน")

    # ทำสำเนาข้อมูลต้นฉบับมาใช้ตรวจคุณภาพ เพื่อไม่กระทบ DataFrame หลัก
    df_qc = df_breweries.copy()
    # สร้าง list ว่างไว้สะสมรายการปัญหาที่ตรวจพบ
    issues = []

    # วนตรวจสอบข้อมูลทีละแถว
    for _, row in df_qc.iterrows():
        # ถ้า `id` หายไปหรือเป็นค่าว่างหลังตัดช่องว่าง
        if pd.isna(row["id"]) or str(row["id"]).strip() == "":
            # เพิ่มแถวนี้เข้า list ปัญหา พร้อมแนบข้อความอธิบายประเภทของปัญหา
            issues.append({**row.to_dict(), "issue": "Missing ID"})
        # ถ้า `brewery_name` หายไปหรือว่าง
        elif pd.isna(row["brewery_name"]) or str(row["brewery_name"]).strip() == "":
            # เพิ่มแถวนี้เข้า list ปัญหาพร้อมระบุว่าไม่มีชื่อโรงเบียร์
            issues.append({**row.to_dict(), "issue": "Missing Brewery Name"})
        # ถ้า `brewery_type` หายไปหรือว่าง
        elif pd.isna(row["brewery_type"]) or str(row["brewery_type"]).strip() == "":
            # เพิ่มแถวนี้เข้า list ปัญหาพร้อมระบุว่าไม่มีประเภทโรงเบียร์
            issues.append({**row.to_dict(), "issue": "Missing Brewery Type"})
        # ถ้า `city` หายไปหรือว่าง
        elif pd.isna(row["city"]) or str(row["city"]).strip() == "":
            # เพิ่มแถวนี้เข้า list ปัญหาพร้อมระบุว่าไม่มีชื่อเมือง
            issues.append({**row.to_dict(), "issue": "Missing City"})
        # ถ้า `state_name` หายไปหรือว่าง
        elif pd.isna(row["state_name"]) or str(row["state_name"]).strip() == "":
            # เพิ่มแถวนี้เข้า list ปัญหาพร้อมระบุว่าไม่มีชื่อรัฐ
            issues.append({**row.to_dict(), "issue": "Missing State Name"})
        # ถ้า `country` หายไปหรือว่าง
        elif pd.isna(row["country"]) or str(row["country"]).strip() == "":
            # เพิ่มแถวนี้เข้า list ปัญหาพร้อมระบุว่าไม่มีชื่อประเทศ
            issues.append({**row.to_dict(), "issue": "Missing Country"})

    # หาแถวที่มี `id` ซ้ำกัน โดยให้เก็บทุกแถวที่ซ้ำออกมาทั้งหมด
    dup_id = df_qc[df_qc["id"].duplicated(keep=False)]
    # วนเพิ่มรายการที่ `id` ซ้ำเข้าไปใน list ปัญหา
    for _, row in dup_id.iterrows():
        # เพิ่มแถวนี้เข้า list ปัญหาพร้อมระบุว่าเป็นรหัสซ้ำ
        issues.append({**row.to_dict(), "issue": "Duplicate ID"})

    # แปลง list ของปัญหาเป็น DataFrame และลบข้อมูลซ้ำที่อาจถูกเพิ่มซ้ำโดยบังเอิญ
    quarantine_df = pd.DataFrame(issues).drop_duplicates()

    # แสดงจำนวน record ที่มีปัญหาคุณภาพข้อมูล
    st.metric("Records with Issues", len(quarantine_df))

    # ถ้าไม่มีข้อมูลที่มีปัญหาเลย
    if quarantine_df.empty:
        # แสดงข้อความ success ว่าคุณภาพข้อมูลปกติ
        st.success("✅ ไม่พบข้อมูลผิดปกติ (No data quality issues found)")
    # ถ้ามีข้อมูลที่มีปัญหาอย่างน้อย 1 แถว
    else:
        # แสดงตารางข้อมูลที่ต้องกักไว้เพื่อตรวจสอบ
        st.dataframe(quarantine_df, use_container_width=True, hide_index=True)
        # สร้างปุ่มดาวน์โหลดรายการปัญหาในรูปแบบ CSV
        st.download_button(
            # ข้อความบนปุ่มดาวน์โหลด
            "📥 Download Data Quality Issues (CSV)",
            # แปลง DataFrame ปัญหาเป็น CSV และเข้ารหัสเป็น UTF-8
            data=quarantine_df.to_csv(index=False).encode("utf-8"),
            # ตั้งชื่อไฟล์ที่ดาวน์โหลด
            file_name="data_quality_issues.csv",
            # ระบุชนิดไฟล์เป็น CSV
            mime="text/csv",
        )


# เริ่มเนื้อหาภายในแท็บที่ 6: Pipeline Health
with tab6:
    # แสดงหัวข้อย่อยของแท็บสถานะระบบหลังบ้าน
    st.subheader("Pipeline Health (สถานะระบบหลังบ้าน)")
    # อธิบายว่าหน้านี้ใช้ติดตามสถานะการทำงานของ ETL และระบบหลังบ้าน
    st.markdown("ตรวจสอบสถานะการทำงานของระบบและประสิทธิภาพของกระบวนการ ETL")

    # นับจำนวน record ที่ถูกจัดเข้า quarantine
    quarantine_count = len(quarantine_df)
    # นับจำนวน record ทั้งหมดของข้อมูลหลัก
    total_records = len(df_breweries)
    # คำนวณจำนวน record ที่ถือว่า valid โดยเอาทั้งหมดลบข้อมูลที่มีปัญหา
    valid_records = total_records - quarantine_count
    # เก็บเวลาปัจจุบันเพื่อใช้แสดงว่า dashboard รีเฟรชล่าสุดเมื่อไร
    last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # แบ่งพื้นที่ออกเป็น 4 คอลัมน์เพื่อแสดง metric ของระบบ
    col1, col2, col3, col4 = st.columns(4)
    # แสดงจำนวน record ทั้งหมด
    col1.metric("Total Records", total_records)
    # แสดงจำนวน record ที่ valid
    col2.metric("Valid Records", valid_records)
    # แสดงจำนวน record ใน quarantine
    col3.metric("Quarantine Records", quarantine_count)
    # แสดงเวลา refresh ล่าสุด
    col4.metric("Last Refresh", last_refresh)

    # แทรกเส้นคั่นก่อน section สถานะระบบ
    st.divider()

    # ถ้าไม่มีข้อมูลเสียเลย ให้ถือว่า pipeline healthy ไม่เช่นนั้นให้เป็น warning
    pipeline_status = "healthy" if quarantine_count == 0 else "warning"
    # แสดงหัวข้อส่วนสถานะของ pipeline
    st.write("Pipeline Status:")
    # ถ้าสถานะเป็น healthy
    if pipeline_status == "healthy":
        # แสดงข้อความว่าระบบทำงานปกติ
        st.success("✅ ระบบทำงานปกติ (All systems operational)")
    # ถ้าไม่ healthy
    else:
        # แสดงข้อความเตือนว่าระบบยังมีปัญหาที่ต้องตรวจสอบ
        st.warning("⚠️ ระบบมีปัญหา (System has issues)")

    # แสดงหัวข้อส่วนรายละเอียดของ pipeline
    st.write("รายละเอียด:")
    # แสดงรายละเอียดเชิงเทคนิคแบบ code block
    st.code(
        # ข้อความหลายบรรทัดที่สรุปแหล่งข้อมูลและวิธีโหลดข้อมูล
        """Source: Supabase PostgreSQL
Data Domain: Brewery Master Data
Load Method: SQL query
Environment: Local, Streamlit"""
    )

    # แสดงหัวข้อส่วน system logs
    st.write("System Logs:")
    # แสดงกล่องข้อความ log จำลองเพื่อให้ผู้ใช้เห็นสภาพการทำงานล่าสุด
    st.text_area(
        # ชื่อ label ของช่องข้อความ log
        "Logs",
        # ประกอบข้อความ log จากค่าที่คำนวณได้ด้านบน
        value=(
            # log บอกจำนวน record ที่โหลดมาจาก Supabase
            f"INFO: Loaded {total_records} records from Supabase\n"
            # log บอกจำนวน record ที่ผ่านเกณฑ์
            f"INFO: Valid records: {valid_records}\n"
            # log บอกจำนวน record ที่ถูกกักไว้
            f"INFO: Quarantine records: {quarantine_count}\n"
            # log บอกเวลารีเฟรชล่าสุด
            f"INFO: Last refresh at {last_refresh}\n"
        ),
        # กำหนดความสูงของ text area
        height=180,
    )
