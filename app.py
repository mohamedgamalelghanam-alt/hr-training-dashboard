import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as ui
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Training & Development Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] > div { font-size: 24px; font-weight: bold; color: #1E3A8A; }
    div[data-testid="stMetricLabel"] > label { font-size: 14px; font-weight: 600; color: #4B5563; }
    .stCard {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: #1E3A8A; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
""", unsafe_allow_html=True)

# 2. Data Loading Function (Smart & Flexible)
@st.cache_data
def load_data():
    target_file = "training.xlsx"
    files_in_dir = os.listdir(".")
    
    # البحث عن الملف بغض النظر عن حالة الأحرف الكبيرة أو الصغيرة
    matched_file = [f for f in files_in_dir if f.lower() == target_file]
    
    if matched_file:
        actual_filename = matched_file[0]
        df = pd.read_excel(actual_filename)
        df['Start_Date'] = pd.to_datetime(df['Start_Date'])
        df['End_Date'] = pd.to_datetime(df['End_Date'])
        df['Month'] = df['Start_Date'].dt.to_period('M').astype(str)
        return df
    else:
        raise FileNotFoundError(f"الملفات المتاحة في السيرفر حالياً هي: {files_in_dir}")

try:
    df = load_data()
except Exception as e:
    st.error(f"⚠️ حدث خطأ أثناء تحميل البيانات من السيرفر: {e}")
    st.info("💡 نصيحة مهندس: تأكد من رفع ملف الإكسل باسم 'Training.xlsx' في المجلد الرئيسي (Root) بجوار ملف app.py مباشرة وليس داخل مجلد فرعي.")
    st.stop()

# 3. Sidebar Filters
st.sidebar.header("🔍 فلاتر التحكم (Filters)")
st.sidebar.markdown("---")

# Department Filter
departments = ['الكل'] + list(df['Department'].unique())
selected_dept = st.sidebar.selectbox("القسم (Department)", departments)

# Category Filter
categories = ['الكل'] + list(df['Category'].unique())
selected_cat = st.sidebar.selectbox("الفئة التدريبية (Category)", categories)

# Date Filter
min_date = df['Start_Date'].min().to_pydatetime()
max_date = df['Start_Date'].max().to_pydatetime()
selected_dates = st.sidebar.date_input("فترة التدريب (Date Range)", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply Filters
filtered_df = df.copy()

if selected_dept != 'الكل':
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]

if selected_cat != 'الكل':
    filtered_df = filtered_df[filtered_df['Category'] == selected_cat]

if len(selected_dates) == 2:
    start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
    filtered_df = filtered_df[(filtered_df['Start_Date'] >= start_date) & (filtered_df['Start_Date'] <= end_date)]

# 4. Main Header
st.title("📊 لوحة تحليلات التدريب والتطوير | Training & Development Dashboard")
st.markdown("تحليل شامل ومؤشرات الأداء لبرامج التدريب وتكلفة الموظفين.")
st.markdown("---")

# 5. Key Performance Indicators (KPIs)
st.subheader("📌 المؤشرات الرئيسية (KPIs)")
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

total_trainings = filtered_df.shape[0]
total_employees = filtered_df['Employee_ID'].nunique()
total_duration = filtered_df['Duration_Hours'].sum()
total_cost = filtered_df['Cost_EGP'].sum()
avg_score = filtered_df['Score_%'].mean() if total_trainings > 0 else 0

completion_rate = (filtered_df['Completed'].value_counts().get('Yes', 0) / total_trainings * 100) if total_trainings > 0 else 0
cert_rate = (filtered_df['Certificate'].value_counts().get('Yes', 0) / total_trainings * 100) if total_trainings > 0 else 0

with kpi1:
    st.metric("إجمالي التدريبات", f"{total_trainings:,}")
with kpi2:
    st.metric("الموظفين المشاركين", f"{total_employees:,}")
with kpi3:
    st.metric("الساعات التدريبية", f"{total_duration:,} س")
with kpi4:
    st.metric("التكلفة الإجمالية", f"£ {total_cost:,}")
with kpi5:
    st.metric("متوسط التقييم", f"{avg_score:.1f}%")
with kpi6:
    st.metric("نسبة الإتمام / الشهادات", f"{completion_rate:.1f}% / {cert_rate:.1f}%")

st.markdown("---")

# 6. Charts Section
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏢 التكلفة والساعات لكل قسم (Department)")
    dept_analysis = filtered_df.groupby('Department').agg({'Cost_EGP': 'sum', 'Duration_Hours': 'sum'}).reset_index()
    
    fig_dept = px.bar(
        dept_analysis, 
        x='Department', 
        y='Cost_EGP',
        text_auto='.2s',
        title="إجمالي التكلفة حسب القسم (بالجنيه المصري)",
        color='Duration_Hours',
        color_continuous_scale='Blues',
        labels={'Cost_EGP': 'التكلفة (EGP)', 'Duration_Hours': 'ساعات التدريب'}
    )
    fig_dept.update_layout(template='plotly_white')
    st.plotly_chart(fig_dept, use_container_width=True)

with col2:
    st.subheader("🗂️ التكلفة والساعات لكل فئة تدريبية (Category)")
    cat_analysis = filtered_df.groupby('Category').agg({'Cost_EGP': 'sum', 'Duration_Hours': 'sum'}).reset_index()
    
    fig_cat = px.bar(
        cat_analysis, 
        y='Category', 
        x='Cost_EGP',
        orientation='h',
        text_auto='.2s',
        title="توزيع التكلفة حسب الفئة التدريبية",
        color='Cost_EGP',
        color_continuous_scale='Purples',
        labels={'Cost_EGP': 'التكلفة (EGP)', 'Category': 'الفئة التدريبية'}
    )
    fig_cat.update_layout(template='plotly_white')
    st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.subheader("✅ نسب الإتمام والحصول على الشهادات")
    
    from plotly.subplots import make_subplots
    
    comp_counts = filtered_df['Completed'].value_counts()
    cert_counts = filtered_df['Certificate'].value_counts()
    
    fig_pies = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                             subplot_titles=['نسبة إتمام التدريب', 'نسبة الحصول على شهادة'])
    
    fig_pies.add_trace(ui.Pie(labels=comp_counts.index, values=comp_counts.values, name="الإتمام", marker=dict(colors=['#2563EB', '#EF4444'])), 1, 1)
    fig_pies.add_trace(ui.Pie(labels=cert_counts.index, values=cert_counts.values, name="الشهادات", marker=dict(colors=['#10B981', '#F59E0B'])), 1, 2)
    
    fig_pies.update_traces(hole=.4, hoverinfo="label+percent+name")
    fig_pies.update_layout(title_text="حالة التدريب والشهادات الممنوحة", template='plotly_white')
    st.plotly_chart(fig_pies, use_container_width=True)

with col4:
    st.subheader("📈 الخط الزمني للتدريب والتكلفة على مدار السنة")
    timeline = filtered_df.groupby('Month').agg({'Cost_EGP': 'sum', 'Training_ID': 'count'}).reset_index().sort_values('Month')
    
    fig_time = px.line(
        timeline, 
        x='Month', 
        y='Cost_EGP', 
        markers=True,
        title="الإنفاق الشهري على التدريب خلال السنة",
        labels={'Cost_EGP': 'التكلفة الإجمالية (EGP)', 'Month': 'الشهر'},
        color_discrete_sequence=['#1E3A8A']
    )
    fig_time.update_layout(template='plotly_white')
    st.plotly_chart(fig_time, use_container_width=True)

st.markdown("---")
st.subheader("🎯 توزيع درجات الموظفين وتحليل الأداء (Score % Distribution)")

col5, col6 = st.columns([1, 2])

with col5:
    dept_scores = filtered_df.groupby('Department')['Score_%'].mean().reset_index().sort_values(by='Score_%', ascending=False)
    st.markdown("**📊 متوسط الدرجات حسب الأقسام:**")
    st.dataframe(dept_scores.style.format({'Score_%': '{:.2f}%'}), hide_index=True, use_container_width=True)

with col6:
    fig_hist = px.histogram(
        filtered_df, 
        x='Score_%', 
        nbins=20, 
        title="توزيع درجات الموظفين بالكامل",
        labels={'Score_%': 'الدرجة (%)', 'count': 'عدد الموظفين'},
        color_discrete_sequence=['#10B981']
    )
    fig_hist.update_layout(template='plotly_white', barcode_mode='overlay')
    st.plotly_chart(fig_hist, use_container_width=True)

# 7. Data Preview Section
st.markdown("---")
with st.expander("👀 عرض البيانات المفلترة بالكامل (Show Filtered Data)"):
    st.dataframe(filtered_df, use_container_width=True)
