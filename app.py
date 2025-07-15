import streamlit as st
import pandas as pd
from processor import process_files

st.set_page_config(page_title="Shopping Group Creator")

from PIL import Image

# Show company logo (adjust filename as needed)
logo = Image.open("logo.png")
st.image(logo, width=400)  # Adjust width as needed


st.title("🛍️ Shopping Group Creator")
st.markdown("""
Upload your **Product Coding** and **Shopping Data** files below.  
Then choose how you'd like to group the results — by any attribute available in the product file (e.g., Category, Subcategory, Brand).
""")

st.markdown("### 📁 Need example files?")
col1, col2 = st.columns(2)

with col1:
    with open("sample_files/product coding sample.xlsx", "rb") as f:
        st.download_button(
            label="📦 Download Product Coding Sample",
            data=f,
            file_name="product_coding_sample.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with col2:
    with open("sample_files/person level purchases sample.xlsx", "rb") as f:
        st.download_button(
            label="🧾 Download Purchase Data Sample",
            data=f,
            file_name="person_level_purchases_sample.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# Upload product coding file first
product_file = st.file_uploader("📦 Upload Product Coding File (.xlsx)", type="xlsx")

group_option = None
product_df = None

if product_file:
    product_df = pd.read_excel(product_file)

    # Dynamically find valid groupable columns
    groupable_columns = product_df.select_dtypes(include='object').columns.tolist()
    exclude_cols = ['UNITSVARIABLE', 'DOLLARSVARIABLE', 'Product Name']
    groupable_columns = [col for col in groupable_columns if col not in exclude_cols]

    if groupable_columns:
        group_option = st.selectbox("🔀 Group products by:", options=groupable_columns)
    else:
        st.warning("⚠️ No valid columns found to group by.")

# Upload purchase data
purchase_file = st.file_uploader("🧾 Upload Purchase Data File (.xlsx)", type="xlsx")

# Run processing if both files and a grouping option are set
if product_file and purchase_file and group_option:
    try:
        purchase_df = pd.read_excel(purchase_file)

        result = process_files(product_df, purchase_df, group_field=group_option)

        st.success("✅ Processing complete!")
        st.dataframe(result, use_container_width=True)

        # Download as CSV
        csv = result.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download CSV",
            csv,
            file_name=f"shopping_summary_{group_option}.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")
