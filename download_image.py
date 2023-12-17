#%%
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import psycopg2
import json
from io import BytesIO
from PIL import Image
#%%
db_connection = psycopg2.connect(
    host="localhost",
    port='5432',
    database="Download_image",
    user="postgres",
    password="1234"
    )
db_cursor = db_connection.cursor()

#%%

driver = webdriver.Chrome()

# Web sayfasını açma
url = 'https://www.asos.com/women/shirts/cat/?cid=15200'
driver.get(url)

wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.TAG_NAME, 'img')))

# Ürün öğelerini bulma
product_elements = driver.find_elements(By.CLASS_NAME, 'gallery-image')

for product_element in product_elements:
    
    #product_page = driver.current_url
    product_element.click()
    
    # Yeni sayfa yüklenene kadar bekleme
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//img[@class='gallery-image']")))
    except TimeoutException:
        print("Beklenen öğeler bulunamadı.")
    
    #if product_page != driver.current_url:
        #continue 
    script4="return window.asos.pdp.config.product.variants[0].colour"
    img_colour= driver.execute_script(script4)
    
    script = "return window.asos.pdp.config.product.id"
    product_id = driver.execute_script(script)
    script2 = "return window.asos.pdp.config.product.gender"
    gender=driver.execute_script(script2)
    script3="return window.asos.pdp.config.product.productType.name"
    product_type=driver.execute_script(script3)
    img_img = driver.find_element(By.XPATH, "//img[@class='gallery-image']")
    
    screenshot = img_img.screenshot_as_png
    
    # Ekran görüntüsünü byte dizisine çevirme
    image = Image.open(BytesIO(screenshot))
    byte_array_img = BytesIO()
    image.save(byte_array_img, format='PNG')
    raw_images = byte_array_img.getvalue()

    # Veritabanına ekleme için JSON oluşturma
    colour_img = img_colour
    product_data = {
        "colour": colour_img,
        "gender":gender ,
        "product_type":product_type
    }
    
    json_data = json.dumps(product_data)
    
    insert_script = "INSERT INTO products (product_id,raw_image, json_field) VALUES (%s, %s,%s)"
    db_cursor.execute(insert_script, (product_id,raw_images, json_data))
    db_connection.commit()
    
    # Önceki sayfaya dönme
    driver.back()
    #driver.refresh()
    # Yeni ürünlerin yüklenmesini beklemek için kısa bir süre bekleme
    time.sleep(2)

# Bağlantıları kapatma
db_cursor.close()
db_connection.close()

# WebDriver'ı kapatma
driver.quit()
    
#%%



