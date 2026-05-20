# Galería de Arte — Proyecto Microservicios Docker

## Arquitectura
```
Usuario → Frontend Vue (puerto 5574) → Backend Flask (puerto 5000) → MongoDB (red interna)
```

## Red Docker
- **Subred:** `10.99.88.0/24`
- **Driver:** bridge

## Puertos
| Servicio  | Puerto externo | Puerto interno |
|-----------|---------------|----------------|
| Frontend  | **5574**      | 80 (Nginx)     |
| Backend   | 5000          | 5000           |
| MongoDB   | ninguno       | 27017          |

## Levantar el proyecto
```bash
# 1. Copiar y configurar .env
cp .env .env.local   # editar con tus contraseñas

# 2. Build y arranque
docker-compose up --build

# 3. Verificar
docker ps

# 4. Acceder
#   Frontend: http://localhost:5574
#   API:      http://localhost:5000/api/obras
```

## API REST disponible
| Método | Ruta                  | Descripción                         |
|--------|-----------------------|-------------------------------------|
| GET    | /api/obras            | Listar obras (filtros: categoria, tipo) |
| GET    | /api/obras/:id        | Detalle de una obra                 |
| POST   | /api/obras            | Crear nueva obra                    |
| DELETE | /api/obras/:id        | Eliminar obra                       |
| GET    | /api/categorias       | Listar todas las categorías         |

## Seguridad aplicada
- ✅ `.env` para todas las credenciales
- ✅ MongoDB sin puerto expuesto
- ✅ Red interna con subred `10.99.88.0/24`
- ✅ Imágenes oficiales de Docker Hub
- ✅ Frontend no accede directamente a MongoDB
