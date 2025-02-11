# Используем официальный образ Python
FROM python:3.9

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Открываем порт (если у вас веб-приложение)
EXPOSE 8000

# Запускаем приложение (замените команду на свою)
CMD ["python", "app.py"]
