docker run -p 6379:6379 redis
celery -A app.core.celery_app worker -l info -P solo
uvicorn app.main:app --reload    