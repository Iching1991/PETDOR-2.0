# PETdor2/frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copia package files
COPY package*.json ./
COPY bun.lockb* ./

# Instala dependências
RUN npm install

# Copia código
COPY . .

# Build
RUN npm run build

# Expõe porta
EXPOSE 3000

# Comando para iniciar
CMD ["npm", "run", "dev"]
