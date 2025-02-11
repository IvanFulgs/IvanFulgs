# Используем официальный Python-образ
FROM python:3.9

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# Создаём виртуальное окружение и устанавливаем зависимости
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Указываем переменные среды (если нужно)
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Открываем нужный порт (если у вас веб-приложение)
EXPOSE 8000

# Запускаем приложение (замените на свою команду)
CMD ["python", "app.py"]
