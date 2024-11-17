import pandas as pd
import streamlit as st
import plotly.express as px
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Scraper Tokopedia
def scrape_tokopedia(query):
    url = f"https://www.tokopedia.com/search?st=product&q={query}"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(url)
    products = []
    items = driver.find_elements(By.CSS_SELECTOR, ".css-12sieg3")
    
    for item in items:
        try:
            name = item.find_element(By.CSS_SELECTOR, ".css-1bjwylw").text
            price = item.find_element(By.CSS_SELECTOR, ".css-o5uqvq").text.replace("Rp", "").replace(".", "").strip()
            link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
            products.append({"name": name, "price": int(price), "site": "Tokopedia", "link": link})
        except Exception as e:
            print(f"Error: {e}")
    
    driver.quit()
    return products

# Scraper Shopee
def scrape_shopee(query):
    url = f"https://shopee.co.id/api/v4/search/search_items?keyword={query}&limit=10"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": f"https://shopee.co.id/search?keyword={query}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return []
    
    data = response.json()
    products = []
    for item in data.get("items", []):
        name = item["item_basic"]["name"]
        price = item["item_basic"]["price"] // 100000
        link = f"https://shopee.co.id/product/{item['shopid']}/{item['itemid']}"
        products.append({"name": name, "price": price, "site": "Shopee", "link": link})
    
    return products

# Streamlit App
st.title("Dashboard Harga dan Stok Barang Toko Online")
st.write("Cari produk dari berbagai situs e-commerce dan bandingkan harga.")

# Input pengguna
query = st.text_input("Masukkan barang yang ingin dicari:", "laptop")  # Kata kunci default
sites = st.multiselect("Pilih situs e-commerce:", ["Tokopedia", "Shopee"], default=["Tokopedia", "Shopee"])

# Tombol cari
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

    # Tampilkan hasil
    if all_products:
        df = pd.DataFrame(all_products)
        st.dataframe(df)

        # Visualisasi data
        fig = px.box(df, x="site", y="price", color="site", title="Perbandingan Harga per Situs")
        st.plotly_chart(fig)

        # Tampilkan link untuk produk termurah
        cheapest_product = df.loc[df["price"].idxmin()]
        st.success(f"Produk termurah: {cheapest_product['name']} (Rp{cheapest_product['price']})")
        st.markdown(f"[Buka produk]({cheapest_product['link']})")
    else:
        st.warning("Tidak ada data ditemukan. Coba ubah kata kunci atau pilih situs lain.")
