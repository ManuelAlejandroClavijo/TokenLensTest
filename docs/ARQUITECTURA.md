# Arquitectura y ADRs · TokenLens 0.1

Fecha: 2026-10-14. Alcance: una persona, una máquina, piloto corto. Estas son decisiones de diseño propias; las capacidades del proveedor se referencian al final.

## Flujo implementado

```text
Claude Code / VS Code
 ├─ OTel logs y metrics → HTTP/protobuf o HTTP/JSON + bearer local
 │                        → FastAPI /v1/logs y /v1/metrics
 │                        → allowlist de atributos → ledger SQLite
 └─ hooks de comandos → Python stdlib
                         → saneamiento → outbox persistente
                         → POST /hooks → snapshot por prompt

SQLite WAL → REST /api/dashboard + notificaciones SSE → React compilado
```

No hay conexión API a Claude, proxy de tráfico, exportación externa ni lectura de transcripts. El proceso Uvicorn sirve estáticos React y API. El puerto 4318 se usa también para OTLP HTTP; no se abre un segundo puerto.

## Contratos

| Endpoint | Propósito |
|---|---|
| POST `/v1/logs` | ExportLogsServiceRequest OTLP JSON/protobuf; requiere credencial local |
| POST `/v1/metrics` | ExportMetricsServiceRequest; solo snapshots token.usage |
| POST `/hooks` | Hook saneado y versionado; requiere credencial local |
| GET `/api/dashboard?source=real\|demo` | Ledger y metadatos de la fuente seleccionada |
| GET `/api/events` | Cambios de revisión, no contenido de conversación |
| PUT `/api/sessions/{id}/binding` | HU, cambio, fase, alias y alcance de corrección |
| POST `/api/reconcile` | Referencia manual y diferencias de una sesión |
| GET `/api/export.csv` | Exportación con filtros y fuente explícita |
| POST / DELETE `/api/demo` | Generar / borrar exclusivamente fixture demo |
| GET `/api/health` | Liveness del servicio local; no cobertura de Claude |

OpenAPI local: `/docs`. JSON OTLP usa nombres camelCase del protocolo protobuf. Los registros de error no guardan el texto de error (puede contener información sensible).

OTLP soportado: logs y métricas HTTP, JSON/protobuf y gzip. **No implementado:** gRPC, traces, Prometheus, compresión alternativa, toda la semántica de todos los instrumentos OTel. El piloto es un adaptador específico, no un Collector de propósito general.

## Modelo

- **Fuente**: real o demo, incluido en claves únicas.
- **Sesión**: ID de Claude + contexto elegido para próximas peticiones.
- **Petición/prompt**: `(source, session_id, prompt_id)` y snapshot HU/cambio/fase/alias.
- **Solicitud**: registro de consumo por llamada del modelo.
- **Herramienta**: evento correlacionado al prompt; no se le atribuyen tokens causales.
- **Métrica**: punto recibido, identidad y temporalidad; no se suma al ledger.
- **Receipt**: conteos aceptados/duplicados/ignorados/inválidos, sin payload.
- **Audit**: cambios de atribución y su alcance.
- **Conciliación**: observado/referencia/diferencias y nota de alcance.

IDs son locales/observados. HU es texto introducido por el usuario: no hay validación contra Azure. Un mismo ID de HU se interpreta dentro de este piloto; si usas varias organizaciones Azure con números iguales, introduce un identificador prefijado, por ejemplo `org-proyecto:1842`.

## ADR 01 · Local-first / un único proceso

**Decisión:** loopback por defecto y assets servidos por FastAPI.

**Beneficio:** no requiere infraestructura corporativa ni frontend dev server; funciona sin Node en ejecución.

**Costo/riesgo:** sin SSO ni garantías multiusuario; no exponible en red. SSE tiene revisión en memoria: usar un solo worker Uvicorn. Tras reiniciar se recarga el ledger, pero no se reproducen notificaciones anteriores.

## ADR 02 · OTLP adapter dentro del backend, no Collector obligatorio

**Decisión:** decodificar ExportLogsServiceRequest/ExportMetricsServiceRequest con `opentelemetry-proto`, además del JSON equivalente.

**Beneficio:** instalación mínima y un solo puerto.

**Costo/riesgo:** soporte limitado y sin cola durable OTel antes de ingresar al servicio. No sustituye un Collector corporativo. El body tiene límite de 8 MB; un lote mayor se rechaza y debe investigarse. Campos no admitidos se descartan. Conformidad integral OTLP no evaluada.

**Reevaluación:** si se necesita tolerancia a receptor caído o captura extensa, agregar Collector con persistent queue. OTel documenta sus garantías y límites [6].

## ADR 03 · Eventos como ledger; métricas solo para contraste

**Decisión:** `api_request` aporta las categorías reportadas; métricas no incrementan ese ledger.

**Beneficio:** evita doble conteo y permite granularidad por prompt [1].

**Costo/riesgo:** solo conocemos eventos recibidos; faltantes no son cero. La deduplicación es sólida con `request_id`; un fallback por metadatos/tiempo no puede prometer equivalencia perfecta. Campos de contador ausentes se marcan parciales. El adaptador sigue contratos documentados, no un contrato inviolable del proveedor.

Error `api_error` se registra sin asumir consumo completo de todos los intentos. El costo ausente es NULL. Los totales no son facturación [4].

## ADR 04 · No almacenar conversaciones

**Decisión:** allowlist de IDs, categorías, modelo, duración, tool_name, tamaños y estado. No guardar prompt, respuesta, parámetros, rutas completas, email o API body.

**Beneficio:** minimización de datos y no dependencia del transcript privado [1,3].

**Costo/riesgo:** no podemos detectar relecturas exactas de archivos, razonar semánticamente sobre necesidad, ni reconstruir pérdidas. Nombres de herramientas/repositorios/HUs también pueden ser sensibles. Los settings de backup son excepción operacional: copias exactas bajo permisos privados, pueden contener secretos preexistentes.

## ADR 05 · Identificadores y asignación explícita

**Decisión:** `prompt.id` de OTel / `prompt_id` del hook enlazan el turno [1,3]. Guardar atribución en el prompt y luego en cada request. Un request sin prompt/hook no hereda ciegamente la sesión actual.

**Beneficio:** sesiones paralelas y eventos tardíos no mezclan tareas.

**Costo/riesgo:** versiones o entornos sin IDs tienen atribución incompleta. No se adivina mediante intervalos. Las HU se asignan manualmente; un error humano sigue siendo posible.

Los hooks tardíos consultan la línea de tiempo de cambios de sesión por fecha de emisión, no su fecha de llegada. Una corrección retrospectiva explícita prevalece sobre esa línea de tiempo y queda auditada. Se supone reloj local consistente: alterar la hora del sistema puede afectar esta lógica.

## ADR 06 · Inferencia coarse + override

**Decisión:** solo comandos slash reconocidos. `propose`/`ff`/`continue` → planning compartido. Fase explícita prevalece.

**Beneficio:** no atribuye arbitrariamente tokens a artefactos generados conjuntamente [5].

**Costo/riesgo:** skills/model-driven y comandos personalizados requieren asignación manual. No hay instrumentación automática de cada artefacto.

## ADR 07 · SQLite WAL

**Decisión:** conexiones cerradas por contexto, transacciones y write lock del proceso.

**Beneficio:** persistencia local, sin servicio de base de datos, deduplicación por UNIQUE.

**Costo/riesgo:** no cifra datos; no tiene cuotas ni retención automática; usar un único proceso. El dashboard recupera el ledger completo: diseñado para piloto pequeño, no para meses de millones de eventos. Herramientas/receipts/audit/métricas mostrados tienen límites de 1000/100/50/500 respectivamente; el ledger de requests y CSV no truncados.

## ADR 08 · Hooks durables, observabilidad fail-open

**Decisión:** script stdlib almacena metadatos saneados en outbox; manda con timeout; backend intenta reenviar cada 5 s.

**Beneficio:** desarrollo no depende de que TokenLens esté disponible. UUID de evento permite reintento idempotente.

**Costo/riesgo:** no garantiza entrega ante disco lleno, cierre abrupto del hook o límite de timeout. Cola sin límite automático: piloto corto y monitoreo de disco. No equivale a durabilidad para eventos OTel. Stop recibido antes de Submit se conserva y resuelve al llegar el inicio.

## ADR 09 · Guardas locales, no seguridad empresarial

**Decisión:** ingesta bearer, Host/Origin same-origin, límite body, CSV anti-fórmulas, permisos POSIX donde disponibles; no CORS.

**Beneficio:** reduce exposición accidental y peticiones browser-origin externas.

**Costo/riesgo:** procesos locales o malware del mismo usuario pueden leer credencial y datos. No hay autenticación en UI ni atestación de origen; no usar como prueba de compliance. Paths/hook commands provienen de configuración de confianza. Revisión corporativa pendiente.

## ADR 10 · Heurísticas transparentes

**Decisión:** mostrar caché, atribución, contadores incompletos y salidas >50 KB como señales.

**Beneficio:** ofrece puntos investigables sin otra llamada al LLM ni captura de conversaciones.

**Costo/riesgo:** no hay inferencia causal ni medición automática de calidad. Comparar tareas equivalentes y resultados humanos antes de decidir cambiar el flujo. El umbral 50 KB es propio del piloto.

## Fuentes

- [1](https://code.claude.com/docs/en/monitoring-usage)
- [2](https://code.claude.com/docs/en/vs-code)
- [3](https://code.claude.com/docs/en/hooks)
- [4](https://code.claude.com/docs/en/costs)
- [5](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md)
- [6](https://opentelemetry.io/docs/collector/resiliency/)
