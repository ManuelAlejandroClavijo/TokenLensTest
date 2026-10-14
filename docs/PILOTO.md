# Protocolo de piloto en tu equipo

## Objetivo

Medir consumo observado de una HU completa a través de varios prompts/chats, sin guardar conversaciones, y evaluar si el dato es suficientemente confiable para comparar versiones del flujo OpenSpec.

No convertir métricas en evaluación individual de productividad ni inferir una factura a partir del costo equivalente.

## Registro del entorno (completar)

- Fecha y persona:
- Sistema operativo / Python:
- Versión de VS Code:
- Nombre exacto y versión de extensión Claude Code:
- Versión de OpenSpec / perfil de comandos:
- Plan real y método de autenticación (sin credenciales):
- Local / WSL / container / Remote SSH:
- Políticas administradas / variables OTel previas:
- HU Azure (organización/proyecto si aplica):
- Cambio OpenSpec:
- Modelo(s):

## Secuencia

1. Revisar la guía de seguridad; mantener aplicación fuera del repo de trabajo.
2. Levantar `pilot.py run` y confirmar health, Datos reales vacío, SSE conectado.
3. Ejecutar init con autorización y guardar ubicación del backup.
4. Reiniciar VS Code. Enviar prompt mínimo. Confirmar sesión y categorías de tokens.
5. Asignar HU/cambio antes del segundo prompt; corregir explícitamente el primero si corresponde.
6. Marcar `discovery` antes de consultar HU con MCP Azure.
7. Marcar `enrichment` antes del enriquecimiento con skill.
8. Marcar `planning` antes del comando que genera artefactos conjuntamente.
9. Marcar `apply` antes de implementar.
10. Marcar `verify` antes de revisión asistida/pruebas; revisión humana sin IA no consume tokens.
11. Marcar `close` antes del cierre asistido por MCP.
12. Abrir otra sesión asociada a la misma HU y comprobar agregación.
13. Realizar conciliación de cada sesión y registrar alcance, diferencias y explicación.
14. Exportar CSV real. No entregar screenshots demo como evidencia.
15. Restaurar settings y comprobar manualmente archivos; reiniciar VS Code.

## Casos adicionales

| Caso | Resultado esperado | Resultado real / evidencia |
|---|---|---|
| Dos HUs en paralelo | No hay cruces de atribución | |
| Cambio de fase entre prompts | El pasado se conserva | |
| Request previo al hook | Inicialmente desconocido; se resuelve por prompt ID | |
| Hook emitido antes de bind pero recibido después | Usa la línea de tiempo, no el contexto actual | |
| Solicitud de subagente | Observar y verificar alcance de tokens reportados | |
| Cancelación / API error | Estado y límites documentados; no inventar uso faltante | |
| Receptor apagado | Hooks en cola; OTel puede perder datos | |
| Reinicio backend | Ledger persistente; UI recarga | |
| CSV | Coincide con filtros y fuente | |
| Restore con settings modificados | Rechaza sobrescribir cambios posteriores | |

## Criterio de decisión

**Continuar:** los IDs y categorías permiten atribución estable y las discrepancias de conciliación quedan explicadas en una muestra suficiente de HUs.

**Continuar condicionado:** falta parte del alcance (por ejemplo ciertas solicitudes auxiliares), pero puede excluirse/declararse consistentemente sin inducir a error.

**No usar para conclusiones de consumo por petición:** faltan contadores/IDs esenciales o existen pérdidas inexplicadas. Actualizar/configurar el entorno o introducir instrumentación más resiliente antes de evaluar eficiencia.

No fijamos ±2 % arbitrario. Primero medir variación y comparar exactamente el mismo alcance. No exigir sumas idénticas a una herramienta con alcance distinto.

## Comparación de mejoras de OpenSpec

Evaluar varias HUs de complejidad comparable. Registrar versión de skills, modelos, tamaño del cambio, aceptación humana, pruebas, tiempo y retrabajo. Comparar distribuciones de tokens, no una sola tarea. El piloto no captura esos resultados humanos automáticamente: anotarlos por separado.

Propuesta de tabla:

| HU | Versión flujo | Complejidad | Tokens observados | Equiv. USD (no factura) | Calidad / pruebas | Tiempo | Retrabajo | Cobertura / límites |
|---|---|---|---:|---:|---|---|---|---|
| | | | | | | | | |

Primero validar datos; después optimizar. Un ahorro que reduce calidad no es una mejora.
