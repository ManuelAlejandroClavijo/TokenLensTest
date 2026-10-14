# Design

## Goals

- Operar localmente sin infraestrutura remota.
- Medir consumo observado por solicitudes con categorías de caché separadas.
- Conservar atribución a pesar de sesiones paralelas y entrega tardía.
- Evitar almacenar conversaciones y secretos del proveedor.
- Hacer explícitos datos desconocidos, límites y heurísticas.

## Non-goals

Multiusuario/SSO, facturación exacta, integración Admin API/Azure, watcher de JSONL, cuotas duras, certeza de necesidad, conformidad OTLP integral.

## Decisions

1. SQLite WAL y un proceso Uvicorn con assets React incluidos.
2. Receptor específico OTLP HTTP JSON/protobuf en FastAPI para minimizar instalación; no Collector obligatorio.
3. Eventos api_request como ledger; métricas como snapshots no sumables al ledger.
4. Hooks stdlib con outbox persistente e ID estable.
5. Snapshot de HU/cambio/fase por prompt y línea de tiempo de binds para hooks tardíos.
6. Correcciones futuras/históricas explícitas y auditadas.
7. Fases coarse y planning compartido; no repartir tokens arbitrariamente.
8. Metadata-only por allowlist; contenido no se escribe en almacenamiento.
9. SSE para notificaciones; polling de respaldo.
10. Real/demo separados por clave de fuente.

Ver trade-offs, contratos, riesgos y fuentes en `docs/ARQUITECTURA.md`.

## Risks / Trade-offs

- Receptor caído o cierre abrupto de Claude puede perder OTel; no hay recuperación histórica.
- Datos de versiones antiguas/incompletas no dan precisión automática.
- No hay seguridad contra procesos del mismo usuario ni cifrado SQLite.
- Settings administrados/heredados pueden prevalecer sobre el instalador.
- Falta atestación de identidad; alias local no equivale a usuario corporativo.
- Dashboard completo y cola sin retención: piloto corto, no uso masivo.

## Migration / Rollback

Backups exactos de settings antes de instalar. Restore rehúsa sobrescribir cambios posteriores salvo force explícito. Datos se conservan. No hubo cambios en un entorno corporativo real desde Arena.

## Open Questions

- ¿La versión de la extensión exporta todos los campos y subagentes esperados?
- ¿Qué alcance tienen resumen de sesión y métricas de proveedor con esta suscripción?
- ¿Qué discrepancias aparecen en cancelaciones y requests auxiliares?

Se responden con `docs/PILOTO.md`, antes de generalizar a la compañía.
