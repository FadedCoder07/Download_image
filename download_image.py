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
#PostgresSQL veritabanına bağlantının gerçekleştirilmesi
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

#Url'de ki resimlerin doğru bir şekilde yüklenmesi
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.TAG_NAME, 'img')))

# Class ismi 'gallery-image' olan ürünlerin bulunması
product_elements = driver.find_elements(By.CLASS_NAME, 'gallery-image')

for product_element in product_elements:
    
    
    #Tekrar tıklama işleminin doğru bi şekilde yapılabilmesi için ürünlerin yüklenmesi
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//img[@class='gallery-image']")))
    except TimeoutException:
        print("Beklenen öğeler bulunamadı.")
    
    
    product_element.click()
    
    #gerekli özelliklerin çekilmesi
    script_colour="return window.asos.pdp.config.product.variants[0].colour"
    img_colour= driver.execute_script(script_colour)
    
    script_id = "return window.asos.pdp.config.product.id"
    product_id = driver.execute_script(script_id)
    script_gender = "return window.asos.pdp.config.product.gender"
    gender=driver.execute_script(script_gender)
    script_type="return window.asos.pdp.config.product.productType.name"
    product_type=driver.execute_script(script_type)
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
    # Yeni ürünlerin yüklenmesini bekleme
    time.sleep(2)

# Bağlantıları kapatma
db_cursor.close()
db_connection.close()

# WebDriver'ı kapatma
driver.quit()
    
#%%



