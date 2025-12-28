import streamlit as st
import pandas as pd

# تهيئة الصفحة
st.set_page_config(
    page_title="تحليل مبيعات/مخزون الموديلات",
    layout="wide"
)

# 1. تحميل ومعالجة البيانات (يفترض أن ملف processed_sales_summary.csv موجود)
# للحصول على هذا الملف، يجب تشغيل كود تحليل البيانات الذي قدمته لك في البداية وحفظ الناتج.
@st.cache_data
def load_data():
    try:
        # قراءة ملف البيانات المُعالَج
        df = pd.read_csv("processed_sales_summary.csv")
        # التأكد من تحويل عمود العدد الكلي إلى عدد صحيح
        df['العدد الكلي'] = df['العدد الكلي'].astype(int)
        return df
    except FileNotFoundError:
        st.error("لم يتم العثور على ملف 'processed_sales_summary.csv'. يرجى التأكد من رفعه في نفس المجلد.")
        return pd.DataFrame()

df_summary = load_data()

# التأكد من أن DataFrame ليس فارغًا قبل المتابعة
if not df_summary.empty:
    
    # 2. إنشاء القائمة المنسدلة (Dropdown/Selectbox)
    
    # استخراج قائمة الموديلات الفريدة لملء القائمة المنسدلة
    model_list = sorted(df_summary['الموديل'].unique().tolist())
    
    # عنوان التطبيق
    st.title("تحليل إجمالي الألوان لكل موديل")
    
    # اختيار الموديل من القائمة المنسدلة
    selected_model = st.selectbox(
        "اختر الموديل لعرض التفاصيل:",
        options=model_list
    )
    
    # 3. عرض الجدول والعدد الكلي
    if selected_model:
        # تصفية البيانات للموديل المختار
        df_model = df_summary[df_summary['الموديل'] == selected_model].copy()
        
        # حساب العدد الكلي للموديل
        total_quantity = df_model['العدد الكلي'].sum()
        
        st.header(f"نتائج الموديل: {selected_model}")
        
        # عرض الجدول (يحتوي على اللون والعدد الكلي)
        st.subheader("جدول عدد كل لون")
        
        # إظهار الأعمدة المطلوبة فقط (اللون والعدد الكلي)
        df_display = df_model[['اللون', 'العدد الكلي']].sort_values(by='العدد الكلي', ascending=False)
        st.dataframe(df_display, use_container_width=True)
        
        # عرض العدد الكلي للموديل
        st.markdown(f"**العدد الكلي لموديل {selected_model} بجميع ألوانه:** **<span style='color:green; font-size: 24px;'>{total_quantity:,}</span>**", unsafe_allow_html=True)
        
        # (اختياري) عرض مخطط دائري (Pie Chart) لتوزيع الألوان
        st.subheader("توزيع الألوان في الموديل")
        
        # إنشاء المخطط الدائري باستخدام Streamlit
        # لا نحتاج إلى Altair هنا، يمكن لـ Streamlit إنشاء المخطط مباشرة
        st.bar_chart(df_display.set_index('اللون'))
        
        st.caption("ملاحظة: التمثيل البياني هو لشريط يعرض الكميات. يمكنك استخدام مكتبات مثل Plotly لإنشاء مخطط دائري أكثر تفصيلاً.")

# إذا كان DataFrame فارغًا
else:
    st.info("الرجاء التأكد من تحميل البيانات بشكل صحيح لبدء التحليل.")
