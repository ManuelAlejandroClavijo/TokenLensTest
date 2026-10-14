# TokenLens: observabilidad local para OpenSpec

## Why

La empresa necesita conocer consumo por HU y fase, incluso con varios chats de Claude Code. Los agregados de organización no contienen la atribución específica del flujo. Un ETL de conversaciones aumenta exposición de código y dependencia del formato interno.

## What Changes

- Aplicación local Python/FastAPI/Uvicorn + React compilado y SQLite.
- Captura OTLP HTTP y hooks saneados, sin lectura de transcripts.
- Ledger por request, snapshot por prompt, asociación explícita HU/cambio/fase.
- Dashboard, exportación, conciliación, auditoría y heurísticas transparentes.
- Instalación y restauración de settings con respaldo.

## Capabilities

### New Capabilities
- `local-consumption-observability`: ingesta, deduplicación, atribución y consulta del consumo observado.

## Impact

Solo máquina del piloto. Configuración OTel de usuario afecta otras sesiones mientras esté activa; hooks limitados al repo. No nueva API key Claude, conexión Azure propia ni servidor externo. Se preserva autenticación existente. No se valida facturación ni productividad.

## Evidence

- [1](https://code.claude.com/docs/en/monitoring-usage): eventos, tokens y correlación.
- [2](https://code.claude.com/docs/en/vs-code): settings compartidos extensión/CLI.
- [3](https://code.claude.com/docs/en/hooks): lifecycle y prompt_id.
- [4](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md): planning multiartefacto.

Diseño detallado y vulnerabilidades en `docs/ARQUITECTURA.md`. Artefactos redactados para el piloto; no se ha ejecutado el validador CLI de OpenSpec aquí. Validación con extensión real pendiente.
