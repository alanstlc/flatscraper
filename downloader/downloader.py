import psycopg2
import selenium
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

insert_sql = "INSERT INTO sreality(id, title, image_url) VALUES (%s, %s, %s)"

insert_id = 1  # manual due to unwanted increment if failed insert


def postgres_connect():
    conn = psycopg2.connect(
        database="sreality",
        user="postgres",
        password="1234",
        host="flatscraper-storage-1",
        port="5432",
    )
    return conn


def postgres_truncate():
    conn = postgres_connect()
    cur = conn.cursor()
    cur.execute("TRUNCATE sreality")
    conn.commit()
    cur.close()
    conn.close()


def postgres_insert(flats):
    conn = postgres_connect()
    cur = conn.cursor()

    global insert_id
    init_insert_id = insert_id
    for flat in flats:
        try:
            cur.execute(insert_sql, (insert_id, flat[0], flat[1]))
            conn.commit()
            insert_id += 1
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            continue
    inserted = insert_id - init_insert_id
    print(f"Inserted {inserted} flats in postgres")
    cur.close()
    conn.close()
    return inserted


if __name__ == '__main__':
    print("Let's do this!")

    postgres_truncate()

    opts = FirefoxOptions()
    opts.add_argument("--headless")
    element_present = EC.presence_of_element_located((By.CLASS_NAME, 'dir-property-list'))
    img_element_present = EC.presence_of_element_located((By.CLASS_NAME, 'img'))
    firefox_service = FirefoxService(GeckoDriverManager().install())

    scraped_flats_counter = 0
    page_num = 1

    while scraped_flats_counter < 500:
        url = f"https://www.sreality.cz/hledani/prodej/byty?strana={page_num}"
        print(f"Scraping: {url}")
        try:
            driver = webdriver.Firefox(service=firefox_service, options=opts)
            driver.get(url)
            WebDriverWait(driver, 5).until(element_present)
            properties_div = driver.find_element(By.CLASS_NAME, 'dir-property-list')
            properties = properties_div.find_elements(By.TAG_NAME, 'div')
        except selenium.common.exceptions.TimeoutException:
            print(f"Timeout when scraping page: {url}")
            driver.close()
            continue
        except Exception as exc:
            print(f"Got some issues with page {page_num}: {exc}")
            driver.close()
            continue
        flats = []
        for p in properties:
            try:
                title = p.find_element(By.CLASS_NAME, 'title')
                text = title.text
                img = p.find_elements(By.TAG_NAME, 'img')
                img_url = img[1].get_dom_attribute("src")
            except Exception as exc:
                continue
            flats.append((text, img_url))
        if flats:
            if inserted_flats := postgres_insert(flats):
                scraped_flats_counter += inserted_flats
                page_num += 1
        print(f"Scraped {scraped_flats_counter} flats so far")
        driver.close()
