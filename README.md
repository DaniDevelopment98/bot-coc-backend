# 🤖 Clash of Clans WhatsApp Bot

Bot de Clash of Clans integrado con WhatsApp para consultar información del clan, jugadores, guerras y más.

## 🚀 Características

- ✅ Consulta información de clanes
- ✅ Datos de jugadores
- ✅ Info de guerras de clan
- ✅ Notificaciones en tiempo real
- ✅ Integración con WhatsApp
- ✅ Comandos personalizables

## 📋 Requisitos previos

- Node.js v16+
- npm o yarn
- API Key de Clash of Clans (obtén la tuya en https://developer.clashofclans.com/)
- WhatsApp (para usar el bot)

## 🔧 Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/DaniDevelopment98/coc-whatsapp-bot.git
cd coc-whatsapp-bot
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
# Edita .env y añade tu API Key de CoC
```

4. **Iniciar el bot**
```bash
npm run dev
```

## 📱 Comandos disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/clan` | Info del clan | `/clan #2P8Y8P2YQ` |
| `/player` | Info del jugador | `/player #2P8Y8P2YQ` |
| `/war` | Info de guerra | `/war #2P8Y8P2YQ` |
| `/members` | Miembros del clan | `/members #2P8Y8P2YQ` |
| `/help` | Mostrar ayuda | `/help` |

## 🏗️ Estructura del proyecto

```
src/
├── services/
│   ├── coc-api.js          # Llamadas a API de CoC
│   ├── whatsapp.js         # Manejo de WhatsApp
│   └── database.js         # Operaciones de BD
├── commands/
│   ├── clan.js
│   ├── player.js
│   ├── war.js
│   ├── members.js
│   └── help.js
├── handlers/
│   └── commandHandler.js   # Procesador de comandos
├── utils/
│   ├── logger.js           # Logging
│   ├── validators.js       # Validaciones
│   └── formatters.js       # Formateo de mensajes
└── index.js                # Punto de entrada
```

## 🔐 Variables de entorno

Ver `.env.example` para la lista completa.

## 📝 Licencia

MIT

## 👥 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes, abre un issue primero.
