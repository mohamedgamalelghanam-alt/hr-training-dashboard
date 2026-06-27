import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration (Premium UI Settings)
st.set_page_config(
    page_title="Corporate Training Insights Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise-Level CSS Styling
st.markdown("""
    <style>
    /* Background and global font adjustments */
    .stApp {
        background-color: #f4f6f9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* KPI Card Container styling */
    .kpi-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #1E3A8A;
        transition: transform 0.2s;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
    }
    
    /* Metrics override */
    div[data-testid="stMetricValue"] > div {
        font-size: 26px;
        font-weight: 700;
        color: #0F172A;
    }
    div[data-testid="stMetricLabel"] > label {
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Custom headers and section lines */
    h1 {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 5px;
    }
    h2, h3 {
        color: #334155;
        font-weight: 600;
    }
    
    /* Stylish dividers */
    .custom-hr {
        margin: 20px 0;
        border: 0;
        height: 1px;
        background: linear-gradient(to right, #1E3A8A, #cbd5e1, transparent);
    }
    </style>
""", unsafe_allow_html=True)

# 2. Main Title Layout
st.markdown("<h1>📊 لوحة مؤشرات التدريب والتطوير المؤسسي</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #475569; font-size: 1.1rem; margin-top:-10px;'>تحليلات متقدمة لتقييم كفاءة البرامج التدريبية وعوائد الاستثمار في رأس المال البشري.</p>", unsafe_allow_html=True)
st.markdown("<div class='custom-hr'></div>", unsafe_allow_html=True)

# 3. Streamlined File Uploader inside an Expander / Nice Container
with st.container():
    uploaded_file = st.file_uploader("📂 مركز رفع ملفات البيانات (يدعم صيغ CSV & Excel)", type=["csv", "xlsx"], help="ارفع ملف التدريب المحدث هنا لتحديث اللوحة تلقائياً")

# Function to read and prepare data beautifully
def process_data(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
        
    df['Start_Date'] = pd.to_datetime(df['Start_Date'])
    df['End_Date'] = pd.to_datetime(df['End_Date'])
    df['Month'] = df['Start_Date'].dt.to_period('M').astype(str)
    return df

# Layout Control after file upload
if uploaded_file is not None:
    try:
        df = process_data(uploaded_file)
        
        # 4. Sidebar Filters Styling
        st.sidebar.markdown("<h2 style='color:#1E3A8A; font-size:1.5rem;'>🎯 فلاتر التحكم المتقدمة</h2>", unsafe_allow_html=True)
        st.sidebar.markdown("---")

        departments = ['الكل (All Departments)'] + list(df['Department'].unique())
        selected_dept = st.sidebar.selectbox("🏢 تصفية حسب القسم", departments)

        categories = ['الكل (All Categories)'] + list(df['Category'].unique())
        selected_cat = st.sidebar.selectbox("🗂️ الفئة التدريبية", categories)

        min_date = df['Start_Date'].min().date()
        max_date = df['Start_Date'].max().date()
        selected_dates = st.sidebar.date_input("📅 النطاق الزمني للتدريب", [min_date, max_date], min_value=min_date, max_value=max_date)

        # Base Filter Engine
        filtered_df = df.copy()

        if selected_dept != 'الكل (All Departments)':
            filtered_df = filtered_df[filtered_df['Department'] == selected_dept]

        if selected_cat != 'الكل (All Categories)':
            filtered_df = filtered_df[filtered_df['Category'] == selected_cat]

        if len(selected_dates) == 2:
            start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
            filtered_df = filtered_df[(filtered_df['Start_Date'] >= start_date) & (filtered_df['Start_Date'] <= end_date)]

        # Calculations
        total_trainings = filtered_df.shape[0]
        total_employees = filtered_df['Employee_ID'].nunique() if total_trainings > 0 else 0
        total_duration = filtered_df['Duration_Hours'].sum() if total_trainings > 0 else 0
        total_cost = filtered_df['Cost_EGP'].sum() if total_trainings > 0 else 0
        avg_score = filtered_df['Score_%'].mean() if total_trainings > 0 else 0

        completion_rate = (filtered_df['Completed'].value_counts().get('Yes', 0) / total_trainings * 100) if total_trainings > 0 else 0
        cert_rate = (filtered_df['Certificate'].value_counts().get('Yes', 0) / total_trainings * 100) if total_trainings > 0 else 0

        # 5. Executive KPIs Grid with custom style wrapping
        st.markdown("<h3 style='margin-bottom:15px;'>📌 ملخص الأداء الاستراتيجي</h3>", unsafe_allow_html=True)
        kpi_cols = st.columns(6)
        
        metrics_data = [
            ("إجمالي البرامج", f"{total_trainings:,}", kpi_cols[0]),
            ("الموظفين المشاركين", f"{total_employees:,}", kpi_cols[1]),
            ("الساعات الاستثمارية", f"{total_duration:,} س", kpi_cols[2]),
            ("الاستثمار الإجمالي", f"£ {total_cost:,}", kpi_cols[3]),
            ("معدل تقييم الأداء", f"{avg_score:.1f}%", kpi_cols[4]),
            ("نسبة النجاح / الشهادات", f"{completion_rate:.0f}% / {cert_rate:.0f}%", kpi_cols[5])
        ]
        
        for label, val, col in metrics_data:
            with col:
                st.markdown(f"<div class='kpi-container'>", unsafe_allow_html=True)
                st.metric(label, val)
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='custom-hr'></div>", unsafe_allow_html=True)

        # 6. Charts Section (Advanced Themes)
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("### 🏢 توزيع النفقات وساعات العمل للأقسام")
            if total_trainings > 0:
                dept_analysis = filtered_df.groupby('Department').agg({'Cost_EGP': 'sum', 'Duration_Hours': 'sum'}).reset_index()
                fig_dept = px.bar(
                    dept_analysis, 
                    x='Department', 
                    y='Cost_EGP',
                    text_auto='.3s',
                    color='Duration_Hours',
                    color_continuous_scale='Cividis',
                    labels={'Cost_EGP': 'التكلفة الإجمالية (EGP)', 'Duration_Hours': 'مجموع الساعات'}
                )
                fig_dept.update_layout(
                    template='plotly_white',
                    margin=dict(l=20, r=20, t=10, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_dept, use_container_width=True)
            else:
                st.info("لا توجد بيانات متاحة حالياً للتصفية الحالية.")

        with chart_col2:
            st.markdown("### 🗂️ تحليل الاستثمار حسب الفئات التدريبية")
            if total_trainings > 0:
                cat_analysis = filtered_df.groupby('Category').agg({'Cost_EGP': 'sum', 'Duration_Hours': 'sum'}).reset_index()
                fig_cat = px.bar(
                    cat_analysis, 
                    y='Category', 
                    x='Cost_EGP',
                    orientation='h',
                    text_auto='.3s',
                    color='Cost_EGP',
                    color_continuous_scale='Viridis',
                    labels={'Cost_EGP': 'التكلفة الاستثمارية (EGP)', 'Category': 'الفئة'}
                )
                fig_cat.update_layout(
                    template='plotly_white',
                    margin=dict(l=20, r=20, t=10, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_cat, use_container_width=True)

        st.markdown("<div class='custom-hr'></div>", unsafe_allow_html=True)
        chart_col3, chart_col4 = st.columns(2)

        with chart_col3:
            st.markdown("### ✅ مؤشرات إتمام الدورات وحصد الشهادات")
            if total_trainings > 0:
                from plotly.subplots import make_subplots
                comp_counts = filtered_df['Completed'].value_counts()
                cert_counts = filtered_df['Certificate'].value_counts()
                
                fig_pies = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                         subplot_titles=['إتمام البرنامج', 'استحقاق الشهادة'])
                
                fig_pies.add_trace(go.Pie(labels=comp_counts.index, values=comp_counts.values, name="Completion", marker=dict(colors=['#1E3A8A', '#F1F5F9'])), 1, 1)
                fig_pies.add_trace(go.Pie(labels=cert_counts.index, values=cert_counts.values, name="Certificates", marker=dict(colors=['#10B981', '#E2E8F0'])), 1, 2)
                
                fig_pies.update_traces(hole=.4, hoverinfo="label+percent")
                fig_pies.update_layout(template='plotly_white', margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_pies, use_container_width=True)

        with chart_col4:
            st.markdown("### 📈 المنحنى الزمني للإنفاق على التدريب والشهور")
            if total_trainings > 0:
                timeline = filtered_df.groupby('Month').agg({'Cost_EGP': 'sum'}).reset_index().sort_values('Month')
                fig_time = px.area(
                    timeline, 
                    x='Month', 
                    y='Cost_EGP', 
                    markers=True,
                    labels={'Cost_EGP': 'الميزانية المستهلكة (EGP)', 'Month': 'الفترة الزمنية'}
                )
                fig_time.update_traces(line_color='#1E3A8A', fillcolor='rgba(30, 58, 138, 0.2)')
                fig_time.update_layout(template='plotly_white', margin=dict(l=20, r=20, t=10, b=20))
                st.plotly_chart(fig_time, use_container_width=True)

        st.markdown("<div class='custom-hr'></div>", unsafe_allow_html=True)
        
        # 7. Distribution Section
        st.markdown("### 🎯 مستويات أداء المتدربين والدرجات المستهدفة")
        dist_col1, dist_col2 = st.columns([1, 2])
        
        with dist_col1:
            if total_trainings > 0:
                dept_scores = filtered_df.groupby('Department')['Score_%'].mean().reset_index().sort_values(by='Score_%', ascending=False)
                st.dataframe(
                    dept_scores.style.format({'Score_%': '{:.1f}%'}).background_gradient(cmap='Blues'),
                    hide_index=True,
                    use_container_width=True
                )

        with dist_col2:
            if total_trainings > 0:
                fig_hist = px.histogram(
                    filtered_df, 
                    x='Score_%', 
                    nbins=15,
                    color_discrete_sequence=['#3B82F6'],
                    labels={'Score_%': 'الدرجة الكلية للموظف (%)', 'count': 'التكرار (عدد الموظفين)'}
                )
                fig_hist.update_layout(template='plotly_white', margin=dict(l=20, r=20, t=10, b=20), barmode='overlay')
                st.plotly_chart(fig_hist, use_container_width=True)

        # 8. Clean Preview Block
        st.markdown("---")
        with st.expander("🔍 استعراض وفحص قاعدة البيانات بعد التصفية (Filtered Raw Data)"):
            st.dataframe(filtered_df, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ بنية الملف المرفوع لا تتطابق مع الأعمدة المحددة في الكود الرئيسي: {e}")
else:
    # Premium Landing Notice for Client
    st.markdown("""
        <div style="background-color: #eff6ff; border-left: 6px solid #2563eb; padding: 25px; border-radius: 8px; margin-top: 20px;">
            <h4 style="color: #1e40af; margin-top:0;">👋 مرحباً بك في النظام الذكي لتحليل البيانات!</h4>
            <p style="color: #1e3a8a; margin-bottom:0;">لتشغيل لوحة التحكم وعرض التحليلات التفاعلية والرسوم البيانية لعملائك، يرجى سحب وإفلات ملف البيانات الخاص بك (Excel أو CSV) في الخانة المخصصة بالأعلى.</p>
        </div>
    """, unsafe_allow_html=True)
