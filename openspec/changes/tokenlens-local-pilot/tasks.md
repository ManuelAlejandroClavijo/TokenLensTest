# Implementation tasks

## 1. Local application
- [x] Python/FastAPI/Uvicorn y esquema SQLite WAL.
- [x] React compilado servido por el backend.
- [x] Arranque loopback mediante pilot.py, sin Node en runtime.

## 2. Capture and accounting
- [x] OTLP HTTP JSON/protobuf, gzip y límite de payload.
- [x] Metadata allowlist y autenticación local de ingesta.
- [x] Ledger con cuatro categorías de tokens y costo nullable.
- [x] Deduplicación por ID estable y fallback marcado.
- [x] Métricas como snapshots separados, sin doble conteo.

## 3. Attribution and hooks
- [x] Adapter de hooks sin persistir texto de prompt.
- [x] Outbox persistente y retry automático.
- [x] HU/cambio/fase y snapshot por petición.
- [x] Línea de tiempo para hooks tardíos.
- [x] Overrides históricos explícitos y auditados.
- [x] Stop anterior a Submit resuelto sin perder terminal state.

## 4. UI and pilot ergonomics
- [x] Vista general, sesiones, HUs, fases, optimización y diagnósticos.
- [x] Detalle de solicitud/petición y herramientas correlacionadas.
- [x] Top peticiones por tokens/costo equivalente.
- [x] Conciliación manual y CSV con filtros.
- [x] Real/demo aislados y advertencias de cobertura.
- [x] Settings backup/install/restore sin modificar políticas administradas.

## 5. Verification
- [x] 45 tests automatizados sintéticos.
- [x] Cobertura backend >=80 %, dominio SQLite ~95 % de líneas.
- [x] E2E Chromium de acciones principales y viewport móvil.
- [x] Comando local de instalación/arranque probado en Linux.
- [x] Ingesta sintética por red local y deduplicación verificada.
- [x] Documentación, ADRs y CI preparado.
- [ ] Validar extensión auténtica y suscripción del usuario.
- [ ] Conciliar una HU real completa con varias sesiones/subagentes.
- [ ] Validar instalación en Windows/macOS del usuario.
- [ ] Ejecutar CI en un repositorio remoto (workflow preparado, no ejecutado aquí).
- [ ] Ejecutar validador OpenSpec con versión/perfil de la compañía.

No archivar el cambio como validado con proveedor hasta completar el spike local real.
