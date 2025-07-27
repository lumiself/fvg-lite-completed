FROM python:3.11

WORKDIR /workspace

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Optionally install developer tools
RUN pip install black ipython

COPY . .

EXPOSE 5000 8765

CMD ["python", "app.py"]
