import pandas as pd
import streamlit as st
import plotly.express as px

# Scraper Tokopedia & Shopee
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Masukkan fungsi scraper di sini

st.title("Dashboard Harga dan Stok Barang Toko Online")
st.write("Cari produk dari berbagai situs e-commerce dan bandingkan harga.")

query = st.text_input("Masukkan barang yang ingin dicari:", "laptop")
sites = st.multiselect("Pilih situs e-commerce:", ["Tokopedia", "Shopee"], default=["Tokopedia", "Shopee"])

if st.button("Cari"):
    all_products = []
    with st.spinner("Sedang mengambil data..."):
        if "Tokopedia" in sites:
            try:
                all_products.extend(scrape_tokopedia(query))
            except Exception as e:
                st.error(f"Error saat scraping Tokopedia: {e}")

        if "Shopee" in sites:
            try:
                all_products.extend(scrape_shopee(query))
            except Exception as e:
                st.error(f"Error saat scraping Shopee: {e}")

    if all_products:
        df = pd.DataFrame(all_products)
        st.dataframe(df)
        fig = px.box(df, x="site", y="price", color="site", title="Perbandingan Harga per Situs")
        st.plotly_chart(fig)
        cheapest_product = df.loc[df["price"].idxmin()]
        st.success(f"Produk termurah: {cheapest_product['name']} (Rp{cheapest_product['price']})")
        st.markdown(f"[Buka produk]({cheapest_product['link']})")
    else:
        st.warning("Tidak ada data ditemukan. Coba ubah kata kunci atau pilih situs lain.")
