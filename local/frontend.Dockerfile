# Imagen de desarrollo del frontend. El contexto de build es la raiz del repositorio.
FROM node:20-alpine

WORKDIR /workspace/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

EXPOSE 5173
