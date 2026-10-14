# Verificación ejecutada · 2026-10-14

## Entorno de esta entrega

- Linux x86_64.
- Python 3.13.16.
- Node 20.20.2 para construir React (no necesario al ejecutar el bundle).
- Dependencias de Python fijadas en `requirements.lock.txt`.
- Dependencias frontend fijadas en `frontend/package-lock.json`.

## Resultados

### Pruebas automatizadas

**45 tests pasaron.** Evidencia de salida en `resultado-tests.txt` y cobertura por archivo/línea en `coverage.json`.

- Backend total: ~88 % de líneas.
- Dominio SQLite (`backend/store.py`): ~95 % de líneas.
- Backend + hook adapter: ~89 % de líneas.
- Umbral aplicado por `pilot.py test`: 80 % backend.

Casos: deduplicación JSON/protobuf, aislamiento por sesión/fuente, snapshots no sumados, eventos y hooks tardíos, bind futuro e histórico, Stop anterior a Submit, privacidad de almacenamiento, costos desconocidos, alias, herramientas, errores, límites gzip, validación, protección Host/Origin, CSV, conciliación, cola de hooks, backups, restore seguro y rollback de instalación parcial.

Hay **una advertencia no bloqueante** del TestClient de Starlette sobre deprecación del cliente httpx. No es un error de la aplicación; debe revisarse al actualizar dependencias. No se silenció en la evidencia.

### Navegador

Playwright / Chromium headless completó `tests/browser_smoke.py`:

- Demo explícita y ledger visible.
- Detalle de solicitud.
- Asociación de HU y fase, scope histórico y auditoría.
- Conciliación y resultados.
- Descarga CSV con fuente demo.
- Cambio a fuente real.
- Diálogo de configuración.
- Viewport móvil de 390 × 844 sin overflow horizontal global.
- Sin errores JavaScript capturados.

Screenshots: `dashboard.png` y `mobile.png`. Son **datos sintéticos**, no capturas del proveedor.

### Comandos de usuario

Se ejecutaron:

```bash
python pilot.py setup
python pilot.py test
python pilot.py run --port 4320
```

- Setup creó un entorno aislado e instaló dependencias.
- Run inició Uvicorn con bind `127.0.0.1`, frontend compilado y health correcto.
- Ingesta sintética HTTP de un evento repetido produjo una sola solicitud.
- El proceso de prueba local fue detenido correctamente.

También se compiló React con `npm run build` y se revisaron imports Python con Ruff.

## Lo que NO se ha validado

- Exportación de una extensión auténtica de Claude Code con la suscripción del usuario.
- Contadores de todas las llamadas auxiliares, retries o subagentes del entorno real.
- Conciliación con un resumen real de Claude Code.
- Políticas administradas de la compañía.
- Windows/macOS o escenarios WSL/Remote SSH/dev containers.
- CI remoto (workflow preparado, no ejecutado en una plataforma remota).
- Validador CLI de OpenSpec (artefactos authored, pendiente validar versión/perfil).
- Evaluación de seguridad empresarial o prueba de estrés de larga duración.

**Conclusión:** el producto local, los contratos sintéticos y las acciones de UI son funcionales. La confiabilidad del dato de TU proveedor/entorno debe establecerse con `PILOTO.md` antes de utilizar métricas para decisiones corporativas. No se modificaron los settings reales del usuario ni se extrajeron conversaciones.
