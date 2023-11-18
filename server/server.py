import psycopg2
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

select_sql = "SELECT id, title, image_url from sreality ORDER BY ID"

templates = Jinja2Templates(directory="templates")


def postgre_select():
    conn = psycopg2.connect(
        database="sreality",
        user="postgres",
        password="1234",
        host="flatscraper-storage-1",
        port="5432",
    )
    cur = conn.cursor()
    cur.execute(select_sql)
    res = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    return res


@app.get("/")
async def sreality(request: Request):
    flats = postgre_select()
    return templates.TemplateResponse(
        "sreality.html",
        {
            "request": request,
            "flats": flats[0:19],
            "flats_count": len(flats),
            "page_num": 1
        }
    )


@app.get("/{page_num}")
async def sreality(request: Request, page_num: int):
    flats = postgre_select()
    if not page_num:
        page_num = 1
    max_page = (len(flats) // 20) + 1
    if page_num > max_page:
        page_num = max_page
    id_from = (page_num - 1) * 20
    id_to = page_num * 20
    return templates.TemplateResponse(
        "sreality.html",
        {
            "request": request,
            "flats": flats[id_from:id_to],
            "flats_count": len(flats),
            "page_num": page_num
        }
    )
