FROM node:18-alpine

WORKDIR /workspace

# Install http-server globally
RUN npm install -g http-server

COPY . .

EXPOSE 8080

CMD ["http-server", ".", "-p", "8080", "-c-1"]
