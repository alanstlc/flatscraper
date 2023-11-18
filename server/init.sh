pip3 install --upgrade pip
pip3 install psycopg2-binary fastapi uvicorn[standard] jinja2
cd /home
uvicorn server:app --host 0.0.0.0 --port 8000 --reload