# DESIGN SYSTEM — MASTER (Fuente de Verdad) · SETI 96

> **Proyecto:** Portal SETI 96 (SF96) — portal de ingeniería de software de SETI.
> **Marca de origen:** identidad SETI (producto interno).
> **Instanciado desde:** `templates/MASTER.ux.template.md` (RF-018). **Fuente de los valores:** `system-design.md` (Frontend Design System SETI, documento corporativo externo que no está versionado en este repositorio) + semilla `frontend/html/Cobertura_SF96.html` + razonamiento de `ui-ux-pro-max` (solo estilo y reglas UX).
> **Actualizado:** 2026-10-05.
> **Regla para el agente (`ui-ux-pro-max`) [FIJO]:** Este archivo es la fuente de verdad. NUNCA generes paletas, tipografías ni estilos nuevos con el motor de razonamiento del skill. Usa EXCLUSIVAMENTE los tokens y reglas de abajo. Si construyes una página específica, revisa PRIMERO `design-system/pages/<pagina>.md`; si existe, PRIMA sobre este Master; si no, usa solo este Master.

Convención: `[FIJO]` = no negociable. `[SETI]` = valor de marca tomado de `system-design.md`. `[AJUSTE]` = valor corregido para cumplir WCAG 2.1 AA (regla §20.4 de `system-design.md`: "si hay conflicto entre énfasis y contraste, prevalece contraste"). `[PROPUESTA]` = valor que `system-design.md` exige pero no define; pendiente de confirmación en la sección **PENDIENTES**.

## CÓMO LO CONSUME `ui-ux-pro-max` [FIJO]

- Ubicación canónica: `design-system/MASTER.md` + `design-system/pages/<pagina>.md`. NUNCA ejecutar `search.py --persist` (crearía `design-system/<slug>/MASTER.md` y dos fuentes de verdad).
- Usar el skill SOLO para: búsquedas `--domain ux|chart|icons` y `--stack html-tailwind|react` (metodología, accesibilidad, implementación). NUNCA `--design-system` para decidir colores, tipografías ni espaciado.
- Equivalencia entre las secciones del MASTER generado por el skill y este archivo:

| Sección del skill (`format_master_md`) | Sección de este archivo |
|---|---|
| Global Rules › Color Palette | TOKENS DE COLOR (+ tabla "Roles del skill → tokens SETI") |
| Global Rules › Typography | TIPOGRAFÍA |
| Global Rules › Spacing Variables / Shadow Depths | ESPACIADO, RADIOS, SOMBRAS, Z-INDEX |
| Component Specs | COMPONENTS |
| Style Guidelines / Key Effects | STYLE / KEY EFFECTS |
| Page Pattern | PATTERN |
| Anti-Patterns | AVOID |
| Pre-Delivery Checklist | PRE-DELIVERY CHECKLIST |

## PATTERN

- Tipo de producto: portal interno de ingeniería (B2B interno): catálogo de prácticas, herramientas (estimación, verificación), catálogo de activos, Experto Digital y aprendizaje. NO es una landing de conversión.
- Shell [FIJO]: Header fijo superior (`--z-header`) con el **menú de módulos** del portal + Sidebar fijo izquierdo (`--z-sidebar`) con las **secciones internas del módulo activo** + Content con scroll independiente. Decisión de RQ-0005 D1 (2026-09-30). El sidebar NUNCA repite los módulos del header.
- Densidad: estándar (dial `density` 7/10 del skill) en catálogos y contenido; alta en dashboards (ver `pages/dashboard.md`).
- Contenedor: `max-width: var(--layout-container-max-width)` (1280px), centrado.

## STYLE

- Estilo base: **Minimalism & Swiss Style** (recomendación del skill para apps enterprise y dashboards). Se aplica SOLO como estilo: limpio, funcional, alto contraste, grilla, sans-serif, espacio en blanco. NUNCA importar paletas ni tipografías del catálogo del skill.
- Modo: light por defecto; dark automático por `prefers-color-scheme` (ver TOKENS › Dark mode).
- Efectos permitidos: hover sutil, sombras cortas, jerarquía tipográfica clara. PROHIBIDO glassmorphism, gradientes decorativos, blur decorativo.

### Identidad y logotipos [FIJO]

| Activo | Archivo | Uso | `alt` |
|---|---|---|---|
| Logo corporativo SETI (esfera roja + arco negro + "SETI") | `frontend/img/logo-seti.svg` (fuente: `Logo SETI.png`, 117×122 px) | Identidad de la compañía: footer, pantalla de acceso, "Acerca de". | `SETI` |
| Logo del producto SETI 96 (escudo rojo + lazo DevOps) | `frontend/img/seti-96.svg` (fuente: `Seti 96.png`, 2048×2048 px, 4,9 MB) | Identidad del portal: header (junto al nombre "SETI 96"), sidebar colapsado (solo el escudo), favicon (derivado). | `SETI 96` |

- NUNCA recolorear, deformar, rotar, recortar ni aplicar sombras o filtros a los logos. Mantener proporción y un área de protección mínima de `var(--spacing-2)` alrededor.
- Logos vectoriales **aprobados el 2026-09-30** (RQ-0005 D10 y D20; cierra UX-07): `frontend/img/seti-96.svg` (logo SETI 96, header) y `frontend/img/logo-seti.svg` (logo SETI, pie). Son los que usa el portal. Los PNG (`Seti 96.png`, `Logo SETI.png`) quedan como fuente y NO se publican. `frontend/img/seti-96-autotrazado.svg` es solo material de comparación.
- El arco negro del logo SETI pierde contraste sobre fondos oscuros: en dark mode el logo SETI (PNG o SVG) SIEMPRE va sobre la placa clara descrita abajo, hasta que Marca defina una variante para fondo oscuro.
- Los colores azul y naranja del lazo DevOps pertenecen al logo SF96, NO a la paleta de UI. PROHIBIDO extraerlos como tokens o usarlos en componentes.
- En dark mode el logo SETI va sobre una placa `background: var(--color-white)`, `border-radius: var(--radius-md)`, `padding: var(--spacing-1)`, hasta contar con su variante para fondo oscuro (ver UX-07).
- Rendimiento [FIJO]: PROHIBIDO servir los PNG de origen (`Seti 96.png` pesa 4,9 MB). El portal usa los SVG aprobados con `width`/`height` declarados; el favicon se deriva del SVG de SETI 96.

## TOKENS DE COLOR

- Definir TODOS como variables CSS del documento y mapearlos en Tailwind v4 en `frontend/src/app/styles/` (ver DISCIPLINA DE TOKENS). NUNCA hex/rgb/hsl "quemado" en componentes → autofix a `var(--token)`:

```diff
- color: #E0352B;
+ color: var(--color-primary);
```

- Toda transparencia DEBE construirse con las variables `-rgb`: `rgba(var(--color-primary-rgb), 0.04)`.
- Acción primaria (rojo SETI) y secundaria (neutro negro SETI) son de familias DISTINTAS. NUNCA del mismo color.
- Semánticos (`success`/`warning`/`info`/`error`) reservados EXCLUSIVAMENTE para feedback. NUNCA usar color de estado como CTA.

### Light (por defecto)

```css
:root {
  /* PRIMARY [SETI] */
  --color-primary: #E0352B;
  --color-primary-hover: #C72E25;
  --color-primary-active: #B0281F;
  --color-primary-light: #FDEAEA;
  --color-primary-disabled: #F2A9A5;
  --color-primary-rgb: 224, 53, 43;

  /* WHITE [SETI] */
  --color-white: #FFFFFF;
  --color-white-rgb: 255, 255, 255;

  /* GRAYS [SETI] + grises de la semilla Cobertura_SF96.html [AJUSTE] */
  --color-gray: #C4C4C4;
  --color-gray-light: #E8E8E8;
  --color-gray-lighter: #F5F5F5;
  --color-gray-dark: #A0A0A0;
  --color-gray-medium: #8A8A8A;   /* [AJUSTE] semilla --none-ink; borde de inputs */
  --color-gray-darker: #6B6B6B;   /* [AJUSTE] semilla --soft; texto terciario */
  --color-gray-rgb: 196, 196, 196;

  /* BLACK [SETI] */
  --color-black: #231F20;
  --color-black-light: #3A3536;
  --color-black-rgb: 35, 31, 32;

  /* SEMANTIC base [SETI] */
  --color-success: #28A745;
  --color-success-light: #D4EDDA;
  --color-success-dark: #1E7E34;
  --color-warning: #FFC107;
  --color-warning-light: #FFF3CD;
  --color-warning-dark: #D39E00;
  --color-error: #E0352B;
  --color-error-light: #FDEAEA;
  --color-error-dark: #B0281F;
  --color-info: #17A2B8;
  --color-info-light: #D1ECF1;
  --color-info-dark: #117A8B;

  /* BACKGROUND / SURFACE [SETI] */
  --color-background: #FFFFFF;
  --color-background-alt: #F5F5F5;
  --color-background-elevated: #FFFFFF;
  --color-surface: #FFFFFF;
  --color-surface-hover: #F5F5F5;
  --color-surface-inverse: var(--color-black);   /* banda oscura: SOLO el hero del Home (UX-08); texto --color-text-inverse, 16.3:1 */
  --color-surface-inverse-raised: var(--color-black-light); /* SOLO sobre --color-surface-inverse: skeleton y hover del botón secundario inverso (US 145671); texto inverso 12.05:1 */

  /* BORDERS [SETI] + input [AJUSTE] */
  --color-border: #E8E8E8;                      /* decorativo: cards, divisores */
  --color-border-strong: #C4C4C4;
  --color-border-input: var(--color-gray-medium); /* [AJUSTE] 3.45:1, WCAG 1.4.11 */
  --color-border-focus: #E0352B;

  /* TEXT [SETI] con [AJUSTE] en terciario, placeholder y link */
  --color-text-primary: #231F20;
  --color-text-secondary: #454041;
  --color-text-tertiary: var(--color-gray-darker);     /* [AJUSTE] antes #A0A0A0 (2.61:1) */
  --color-text-inverse: #FFFFFF;
  --color-text-link: var(--color-primary-hover);       /* [AJUSTE] antes #E0352B (4.46:1) */
  --color-text-link-hover: var(--color-primary-active);/* [AJUSTE] antes #C72E25 */
  --color-text-disabled: #C4C4C4;
  --color-text-placeholder: var(--color-gray-darker);  /* [AJUSTE] antes #A0A0A0 (2.61:1) */

  /* ACCIÓN PRIMARIA (capa de componente) [AJUSTE] */
  --color-action-primary: var(--color-primary-hover);          /* blanco 5.46:1 */
  --color-action-primary-hover: var(--color-primary-active);   /* blanco 6.63:1 */
  --color-action-primary-active: var(--color-primary-active);  /* + scale(0.98) */
  --color-action-primary-text: var(--color-text-inverse);
  --color-action-primary-disabled: var(--color-primary-disabled);
  --color-action-primary-disabled-text: var(--color-text-inverse);

  /* ACCIÓN SECUNDARIA (familia neutra) */
  --color-secondary: var(--color-black);
  --color-secondary-hover: var(--color-black-light);

  /* ESTADOS SEMÁNTICOS: bg / border / icon / text (§20.3) */
  --color-success-bg: var(--color-success-light);
  --color-success-border: var(--color-success-dark);
  --color-success-icon: var(--color-success-dark);
  --color-success-text: var(--color-success-dark);  /* solo texto suelto sobre surface */
  --color-warning-bg: var(--color-warning-light);
  --color-warning-border: var(--color-warning-dark);
  --color-warning-icon: var(--color-text-primary);  /* ningún amarillo llega a 3:1 */
  --color-warning-text: var(--color-text-primary);
  --color-info-bg: var(--color-info-light);
  --color-info-border: var(--color-info-dark);
  --color-info-icon: var(--color-info-dark);
  --color-info-text: var(--color-info-dark);
  --color-error-bg: var(--color-error-light);
  --color-error-border: var(--color-error-dark);
  --color-error-icon: var(--color-error-dark);
  --color-error-text: var(--color-error-dark);

  /* TOOLTIP */
  --color-tooltip-bg: var(--color-black);
  --color-tooltip-text: var(--color-text-inverse);

  /* OVERLAY [SETI] */
  --color-overlay: rgba(var(--color-black-rgb), 0.6);
  --color-overlay-light: rgba(var(--color-black-rgb), 0.3);
  --color-focus-ring: rgba(var(--color-primary-rgb), 0.35);
}
```

### Dark mode (`prefers-color-scheme: dark`) [PROPUESTA]

`system-design.md` §20 exige resolver explícitamente fondo, superficie, bordes, textos, links, overlay y estados semánticos, pero no da valores. Los de abajo salen de la variante dark de la semilla `Cobertura_SF96.html` (`#121212`, `#1C1C1C`, `#2A2A2A`, `#404040`, `#F2F2F2`, `#C2C2C2`, `#9A9A9A`, `#E84A40`, `#3A1B19`) y se completan con valores nuevos verificados (ver tabla de contraste). Solo cambian tokens; la estructura del layout es idéntica (§20.1).

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-primary: #E84A40;            /* semilla --red dark */
    --color-primary-rgb: 232, 74, 64;
    --color-primary-light: #3A1B19;      /* semilla --red-tint dark */

    --color-background: #121212;
    --color-background-alt: #1C1C1C;
    --color-background-elevated: #2A2A2A;
    --color-surface: #1C1C1C;
    --color-surface-hover: #2A2A2A;

    --color-border: #404040;
    --color-border-strong: var(--color-gray-darker);
    --color-border-input: var(--color-gray-medium);
    --color-border-focus: var(--color-primary);

    --color-text-primary: #F2F2F2;
    --color-text-secondary: #C2C2C2;
    --color-text-tertiary: #9A9A9A;
    --color-text-inverse: #FFFFFF;
    --color-text-link: #F0625A;          /* nuevo */
    --color-text-link-hover: #F27A73;    /* nuevo */
    --color-text-disabled: #5C5C5C;
    --color-text-placeholder: #9A9A9A;

    /* la acción primaria conserva #C72E25 / #B0281F (blanco ≥ 5.46:1) */
    --color-action-primary-disabled: var(--color-primary-light);
    --color-action-primary-disabled-text: var(--color-text-disabled);

    --color-secondary: var(--color-text-primary);
    --color-secondary-hover: var(--color-text-secondary);

    --color-success-bg: #16281B;  --color-success-border: var(--color-success);
    --color-success-icon: var(--color-success);  --color-success-text: var(--color-success);
    --color-warning-bg: #2E2610;  --color-warning-border: var(--color-warning);
    --color-warning-icon: var(--color-warning);  --color-warning-text: var(--color-warning);
    --color-info-bg: #12292E;     --color-info-border: var(--color-info);
    --color-info-icon: var(--color-info);        --color-info-text: var(--color-info);
    --color-error-bg: #3A1B19;    --color-error-border: #F0625A;
    --color-error-icon: #F0625A;  --color-error-text: #F0625A;

    --color-tooltip-bg: var(--color-black-light);
    --color-tooltip-text: var(--color-text-inverse);

    --color-overlay: rgba(var(--color-black-rgb), 0.8);
    --color-overlay-light: rgba(var(--color-black-rgb), 0.5);
    --color-focus-ring: rgba(var(--color-primary-rgb), 0.45);
  }
}
```

### Reglas de uso de color [SETI §1.2 + AJUSTE]

| Uso | Token |
|---|---|
| Fondo de página / alterno | `--color-background` / `--color-background-alt` |
| Texto principal / secundario / terciario | `--color-text-primary` / `--color-text-secondary` / `--color-text-tertiary` |
| Placeholder | `--color-text-placeholder` |
| CTA fondo / texto | `--color-action-primary` / `--color-action-primary-text` |
| Marca (acentos, iconos de marca, línea principal de gráficos, indicador activo) | `--color-primary` |
| Bordes decorativos / de inputs / de foco | `--color-border` / `--color-border-input` / `--color-border-focus` |
| Links | `--color-text-link` (+ `-hover`) |
| Bloque de estado (alerta, banner, badge) | `--color-<estado>-bg` + borde `--color-<estado>-border` + icono `--color-<estado>-icon` + texto `--color-text-primary` |
| Mensaje de estado suelto (p. ej. error bajo un campo) | `--color-<estado>-text` + icono |
| Overlay / anillo de foco | `--color-overlay` / `--color-focus-ring` |

- Dentro de un bloque de estado el texto SIEMPRE es `--color-text-primary`; el color semántico va en borde e icono. Ningún estado se comunica solo con color (§20.4): icono + texto ("Error:", "Advertencia:").

### Contraste verificado (WCAG 2.1)

| Par | Light | Dark | Criterio |
|---|---|---|---|
| Texto primario / fondo | 16.30 | 16.73 | ≥ 4.5 ✔ |
| Texto secundario / fondo | 10.18 | 10.52 | ≥ 4.5 ✔ |
| Texto terciario / surface | 5.33 (antes 2.61 ✘) | 6.06 | ≥ 4.5 ✔ |
| Placeholder / surface | 5.33 (antes 2.61 ✘) | 6.06 | ≥ 4.5 ✔ |
| Link / fondo | 5.46 (antes 4.46 ✘) | 5.89 | ≥ 4.5 ✔ |
| Link / elevated | 5.46 | 4.51 | ≥ 4.5 ✔ |
| Texto CTA / acción primaria | 5.46 (`#E0352B` daba 4.46 ✘) | 5.46 | ≥ 4.5 ✔ |
| Borde input / surface | 3.45 (antes 1.74 ✘) | 4.94 (elevated 4.16) | ≥ 3 ✔ |
| Borde de foco / surface | 4.46 | 4.45 | ≥ 3 ✔ |
| Texto de error suelto / surface | 6.63 | 5.36 | ≥ 4.5 ✔ |
| Texto de éxito suelto / surface | 5.14 | 5.44 | ≥ 4.5 ✔ |
| Texto de info suelto / surface | 5.02 | 5.60 | ≥ 4.5 ✔ |
| Texto inverso / surface-inverse (hero del Home) | 16.3 | pendiente (UX-03) | ≥ 4.5 ✔ |
| Texto inverso / surface-inverse-raised (hover del botón del hero) | 12.05 | pendiente (UX-03) | ≥ 4.5 ✔ |
| Borde de foco / surface-inverse (foco sobre el hero) | 3.66 | pendiente (UX-03) | ≥ 3 ✔ |
| Texto secundario / background-alt (badge neutro "Próximamente") | 9.34 | pendiente (UX-03) | ≥ 4.5 ✔ |
| Indicador del ítem activo del menú (`--color-primary`) / surface · / surface-hover | 4.46 · 4.09 | pendiente (UX-03) | ≥ 3 ✔ |
| Texto primario / surface-hover (ítem del menú con hover) | 14.95 | pendiente (UX-03) | ≥ 4.5 ✔ |
| Texto primario / bg de cualquier estado | ≥ 13.14 | ≥ 13.39 | ≥ 4.5 ✔ |
| Icono de estado / bg del estado | ≥ 4.06 (warning usa texto primario) | ≥ 4.89 | ≥ 3 ✔ |
| Texto tooltip / tooltip | 16.30 | 12.05 | ≥ 4.5 ✔ |
| Borde de éxito (`--color-success-border`) / surface (celda "Cubierta", US 145681) | 5.14 | pendiente (UX-03) | ≥ 3 ✔ |
| Borde de advertencia (`--color-warning-border`) / surface | 2.42 ✘ | pendiente (UX-03) | NUNCA como único límite de un control: la celda "A medio cubrir" usa `--color-border-input` |
| Texto secundario / surface (celda atenuada del Home) | 10.18 | pendiente (UX-03) | ≥ 4.5 ✔ |
| Borde input / background (Select sobre la página, US 145683) | 3.45 | pendiente (UX-03) | ≥ 3 ✔ |
| Texto primario / background-alt (código y título de una guía, US 145683) | 14.95 | pendiente (UX-03) | ≥ 4.5 ✔ |
| Borde input / background-alt (Badge de estado de una guía, US 145683) | 3.17 | pendiente (UX-03) | ≥ 3 ✔ |
| Texto primario · secundario / background (adherencia de fase y leyenda, US 145950) | 16.30 · 10.18 | pendiente (UX-03) | ≥ 4.5 ✔ |

- `--color-border` (1.23:1) y `--color-border-strong` (1.74:1) son SOLO decorativos (cards, divisores). NUNCA como único límite de un control.
- `--color-text-disabled` y `--color-action-primary-disabled` están exentos de contraste (WCAG 1.4.3), pero el estado deshabilitado DEBE declararse con `disabled`/`aria-disabled`.
- `--color-surface-inverse-raised` contra `--color-surface-inverse` da 1.35:1: SOLO para bloques decorativos del skeleton (`aria-hidden`, exentos de WCAG 1.4.11) y para el hover del botón secundario inverso, cuyo límite lo da su borde `--color-text-inverse` (16.3:1). NUNCA como único límite de un control.
- Sobre la banda del hero NO se usan los botones `primary` (`--color-action-primary` contra `--color-surface-inverse` da 2.99:1, por debajo de 3:1) ni `secondary` (texto oscuro sobre fondo oscuro): se usa `.btn--secondary-inverse`.

### Roles del skill → tokens SETI

| Rol `ui-ux-pro-max` | Variable del skill | Token SETI |
|---|---|---|
| Primary | `--color-primary` | `--color-primary` (marca) / `--color-action-primary` (CTA) |
| On Primary | `--color-on-primary` | `--color-action-primary-text` |
| Secondary | `--color-secondary` | `--color-secondary` |
| Accent/CTA | `--color-accent` | `--color-action-primary` |
| Background | `--color-background` | `--color-background` |
| Foreground | `--color-foreground` | `--color-text-primary` |
| Card / Card Foreground | `--color-card` / `--color-card-foreground` | `--color-surface` / `--color-text-primary` |
| Muted / Muted Foreground | `--color-muted` / `--color-muted-foreground` | `--color-background-alt` / `--color-text-secondary` |
| Border | `--color-border` | `--color-border` |
| Destructive / On Destructive | `--color-destructive` / `--color-on-destructive` | `--color-error-text` / `--color-text-inverse` (ver UX-04) |
| Ring | `--color-ring` | `--color-border-focus` + `--color-focus-ring` |

NUNCA crear las variables del skill (`--color-accent`, `--color-foreground`, etc.) en código: usar el token SETI de la columna derecha.

## TIPOGRAFÍA

```css
:root {
  --font-family-base: "Nunito Sans", sans-serif;
  --font-family-mono: "JetBrains Mono", "Fira Code", Consolas, monospace;

  --font-size-xs: 0.75rem;   --font-size-sm: 0.875rem;  --font-size-base: 1rem;
  --font-size-md: 1.125rem;  --font-size-lg: 1.25rem;   --font-size-xl: 1.5rem;
  --font-size-2xl: 1.875rem; --font-size-3xl: 2.25rem;  --font-size-4xl: 3rem;

  --line-height-tight: 1.2;  --line-height-snug: 1.35;
  --line-height-normal: 1.5; --line-height-relaxed: 1.65;

  --letter-spacing-tight: -0.025em; --letter-spacing-wide: 0.025em;
  --letter-spacing-wider: 0.05em;   --letter-spacing-widest: 0.1em;

  --font-weight-regular: 400; --font-weight-semibold: 600; --font-weight-bold: 700;
}
html { font-size: 100%; } /* 16px [FIJO] */
```

**Carga (máx. 2 familias [FIJO]):**

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
```

- Escala en `rem`; NUNCA `px` en `font-size`. Texto de cuerpo mínimo `--font-size-base` en mobile (evita el zoom de iOS en inputs).
- `line-height` de cuerpo `--line-height-normal`; párrafos largos `--line-height-relaxed`, medida 60–75 caracteres (`max-width: 70ch`).
- Números en tablas, KPIs y temporizadores: `font-variant-numeric: tabular-nums`.
- `--letter-spacing-wide`/`-wider` SOLO en etiquetas en mayúsculas; NUNCA tracking negativo en cuerpo.

**Jerarquía de encabezados** (h1 [SETI §23.8]; h2–h6 [PROPUESTA]). Un solo `h1` por vista. NUNCA saltar niveles:

| Nivel | base | md (≥ 768) | lg (≥ 992) | Peso / interlineado |
|---|---|---|---|---|
| h1 | `--font-size-2xl` | `--font-size-3xl` | `--font-size-4xl` | bold / tight |
| h2 | `--font-size-xl` | `--font-size-2xl` | `--font-size-2xl` | bold / snug |
| h3 | `--font-size-lg` | `--font-size-xl` | `--font-size-xl` | semibold / snug |
| h4 | `--font-size-md` | `--font-size-lg` | `--font-size-lg` | semibold / snug |
| h5–h6 | `--font-size-base` | `--font-size-base` | `--font-size-md` | semibold / normal |
| Cuerpo | `--font-size-base` | | | regular / normal |
| Etiqueta / ayuda | `--font-size-sm` | | | semibold o regular / normal |
| Badge / caption | `--font-size-xs` | | | semibold / tight |

## ESPACIADO, RADIOS, SOMBRAS, Z-INDEX

```css
:root {
  /* Espaciado [SETI] — escala 4px; --spacing-0 para top-0, inset-x-0, p-0 y gap-0 (US 145669) */
  --spacing-0: 0px;
  --spacing-1: 4px;  --spacing-2: 8px;   --spacing-3: 12px;  --spacing-4: 16px;
  --spacing-5: 20px; --spacing-6: 24px;  --spacing-8: 32px;  --spacing-10: 40px;
  --spacing-12: 48px; --spacing-16: 64px; --spacing-20: 80px; --spacing-24: 96px;
  --spacing-32: 128px;

  /* Layout [SETI] */
  --layout-container-max-width: 1280px;
  --layout-sidebar-width: 260px;
  --layout-sidebar-collapsed-width: 72px;
  --layout-header-height: 64px;
  --layout-measure: 70ch;  /* medida de lectura de párrafos (TIPOGRAFÍA: 60–75 caracteres; US 145670) */

  /* Bordes y radios [SETI] */
  --border-thin: 1px; --border-medium: 2px; --border-thick: 3px;
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px;
  --radius-2xl: 24px; --radius-full: 9999px;

  /* Sombras [SETI offsets + color PROPUESTA] */
  --shadow-xs: 0 1px 2px rgba(var(--color-black-rgb), 0.05);
  --shadow-sm: 0 1px 3px rgba(var(--color-black-rgb), 0.08);
  --shadow-md: 0 4px 6px rgba(var(--color-black-rgb), 0.10);
  --shadow-lg: 0 10px 15px rgba(var(--color-black-rgb), 0.12);
  --shadow-xl: 0 20px 25px rgba(var(--color-black-rgb), 0.15);
  --shadow-2xl: 0 25px 50px rgba(var(--color-black-rgb), 0.25);

  /* Z-index [SETI] — content < sidebar < header < overlay < modal */
  --z-dropdown: 100; --z-sticky: 200; --z-fixed: 300; --z-sidebar: 400;
  --z-header: 500; --z-overlay: 900; --z-modal: 1000; --z-tooltip: 1100; --z-toast: 1200;

  /* Anchos de modal [PROPUESTA dentro del rango 400–900px de §9] */
  --modal-width-sm: 400px; --modal-width-md: 640px; --modal-width-lg: 900px;
}
```

- En dark mode las sombras se ven poco: la elevación se expresa con `--color-background-elevated` + `--color-border`, no con sombras más fuertes.
- NUNCA `z-index` numérico en componentes; SIEMPRE `var(--z-*)`. El drawer del sidebar en mobile usa `--z-modal` sobre un backdrop `--z-overlay`.
- Equivalencia con la escala del skill (`--space-*`): xs=`--spacing-1`, sm=`--spacing-2`, md=`--spacing-4`, lg=`--spacing-6`, xl=`--spacing-8`, 2xl=`--spacing-12`, 3xl=`--spacing-16`. Usar SOLO los nombres SETI.

## KEY EFFECTS

```css
:root {
  --transition-fast: 150ms;    /* hover de botones y links */
  --transition-base: 250ms;    /* resto de elementos interactivos */
  --transition-slow: 350ms;    /* entrada de modales y drawers */
  --transition-slower: 500ms;
}
```

- TODO elemento interactivo tiene transición en hover/focus. Declarar las propiedades explícitas (`color`, `background-color`, `border-color`, `box-shadow`, `opacity`, `transform`), NUNCA `transition: all` (ver UX-11).
- Movimiento SOLO con `opacity` y `transform`; NUNCA animar `width`, `height`, `top`, `left`.
- La salida de modales/drawers es más rápida que la entrada: entrada `--transition-slow`, salida `--transition-base`.
- Estado activo de botones: `transform: scale(0.98)`.
- `prefers-reduced-motion: reduce` [FIJO]: sin desplazamientos ni escalas; solo cambios de color/opacidad en `--transition-fast` o instantáneos. Los gráficos se muestran en su estado final.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 1ms;
    animation-iteration-count: 1;
    transition-duration: 1ms;
    scroll-behavior: auto;
  }
}
```

- En la SPA este bloque vive en `base.css` **fuera** de `@layer base` (change `portal-site-footer-a11y`, HU 8.1.3): los estilos sin capa ganan a las utilidades de Tailwind (`duration-fast`, `transition-colors`) sin `!important`. Dentro de una capa perdería contra ellas.

## LAYOUT / RESPONSIVE

- Mobile-First OBLIGATORIO: estilos base = mobile; en orden base → `sm` → `md` → `lg` → `xl`. NUNCA saltar a `xl:` sin los intermedios.
- NUNCA `display:none` como estrategia responsive; recomponer el layout. El sidebar mobile es un drawer fuera de pantalla (`transform: translateX(-100%)` + `inert` mientras está cerrado).
- Breakpoints [SETI]: `sm` 576px · `md` 768px · `lg` 992px · `xl` 1200px · `2xl` 1440px.

| Componente | base (< 768) | md (768–991) | lg (≥ 992) |
|---|---|---|---|
| Sidebar (secciones del módulo) | Oculto; el drawer del header lo incluye | Colapsado, solo iconos (`--layout-sidebar-collapsed-width`) | Expandido (`--layout-sidebar-width`) |
| Header | Compacto: botón de menú + logo SF96 + título reducido; el botón abre un drawer con los módulos y, debajo, las secciones del módulo activo | Botón de menú + logo SF96 + "SETI 96"; el drawer muestra solo los módulos | `lg`: igual que `md`. `xl`+: menú de módulos horizontal completo. Verificar con las etiquetas reales; si no caben, el menú horizontal empieza en `2xl`. El breakpoint vigente es `MODULE_MENU_BREAKPOINT` de `frontend/src/shared/config/breakpoints.ts`, verificado por la e2e `module-menu.spec.ts` (US 145674) |
| Grid principal | 1 columna | 2 columnas | 3–4 columnas según contexto (`xl`: 4) |
| Tablas | Card-view OBLIGATORIO (label: valor) | `overflow-x-auto` | Tabla completa |
| Modales | Fullscreen, sin radio | Centrado, 90% de ancho | Centrado, `--modal-width-*`, `max-height: 85vh` |
| Formularios | 1 columna | Máx. 2 columnas solo si el diseño lo requiere | Igual que md |
| Padding de página | `--spacing-4` | `--spacing-6` | `--spacing-8` |
| Gap de grillas | `--spacing-4` | `--spacing-6` | `--spacing-8` |

- `<meta name="viewport" content="width=device-width, initial-scale=1">`; NUNCA deshabilitar zoom. Usar `min-height: 100dvh` en lugar de `100vh`.
- El contenido reserva `padding-top: var(--layout-header-height)` y, desde `md`, `padding-left` igual al ancho del sidebar: nada queda oculto bajo el shell fijo.
- Imágenes `max-width:100%; height:auto`, con `width`/`height` declarados, `loading="lazy"` bajo el pliegue y formato WebP.
- Touch targets ≥ 44×44px en mobile (WCAG 2.5.5), separación mínima `--spacing-2`.
- Sin scroll horizontal en ninguna vista (verificar a 375px).

## COMPONENTS

Todos los componentes usan BEM, solo tokens, sin `id` en CSS, sin `!important`, máx. 3 niveles de anidación. Arquitectura: Atoms → Molecules → Organisms → Templates. Toda pantalla de datos implementa los estados `loading` (skeleton) / `empty` (mensaje + acción) / `success` / `error` (causa + reintentar).

### Botones

Tipos: `primary`, `secondary`, `tertiary`, `danger`, `ghost`. Estados: hover, focus-visible, active, disabled, loading. Máximo 1 `primary` visible por vista.

```css
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: var(--spacing-2);
  min-height: 44px;
  padding: var(--spacing-3) var(--spacing-6);
  border: var(--border-medium) solid transparent;
  border-radius: var(--radius-md);
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
  cursor: pointer;
  touch-action: manipulation;
  transition: background-color var(--transition-fast), border-color var(--transition-fast),
              color var(--transition-fast), box-shadow var(--transition-fast), transform var(--transition-fast);
}
.btn:focus-visible {
  outline: var(--border-medium) solid var(--color-border-focus);
  outline-offset: var(--border-medium);
  box-shadow: 0 0 0 var(--spacing-1) var(--color-focus-ring);
}
.btn:active { transform: scale(0.98); }
.btn:disabled, .btn[aria-disabled="true"] { cursor: not-allowed; transform: none; }

.btn--primary { background: var(--color-action-primary); color: var(--color-action-primary-text); }
.btn--primary:hover { background: var(--color-action-primary-hover); }
.btn--primary:disabled { background: var(--color-action-primary-disabled); color: var(--color-action-primary-disabled-text); }

.btn--secondary { background: transparent; color: var(--color-text-primary); border-color: var(--color-secondary); }
.btn--secondary:hover { background: var(--color-surface-hover); border-color: var(--color-secondary-hover); }

.btn--tertiary { background: transparent; color: var(--color-text-link); padding-inline: var(--spacing-2); }
.btn--tertiary:hover { color: var(--color-text-link-hover); text-decoration: underline; }

.btn--ghost { background: transparent; color: var(--color-text-secondary); }
.btn--ghost:hover { background: var(--color-surface-hover); color: var(--color-text-primary); }

.btn--danger { background: transparent; color: var(--color-error-text); border-color: var(--color-error-border); }
.btn--danger:hover { background: var(--color-error-bg); }

/* SOLO sobre --color-surface-inverse (hero del Home; US 145671) */
.btn--secondary-inverse { background: transparent; color: var(--color-text-inverse); border-color: var(--color-text-inverse); }
.btn--secondary-inverse:hover { background: var(--color-surface-inverse-raised); }
```

- `loading`: `aria-busy="true"` + `disabled`, spinner SVG a la izquierda, se conserva el ancho (sin salto de layout).
- `danger` SIEMPRE con icono y verbo explícito ("Eliminar proyecto") y SIEMPRE tras un diálogo de confirmación. En ese diálogo la confirmación es el único `primary` (ver UX-04).
- Separación entre botones ≥ `--spacing-2`. Botón de solo icono: `aria-label` obligatorio.

### Inputs

```css
.field { display: flex; flex-direction: column; gap: var(--spacing-1); }
.field__label { font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); color: var(--color-text-primary); }
.field__input {
  min-height: 44px;
  padding: 0 var(--spacing-4);
  background: var(--color-surface);
  color: var(--color-text-primary);
  border: var(--border-thin) solid var(--color-border-input);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
}
.field__input::placeholder { color: var(--color-text-placeholder); }
.field__input:focus-visible {
  outline: none;
  border-color: var(--color-border-focus);
  box-shadow: 0 0 0 var(--spacing-1) var(--color-focus-ring);
}
.field__input[aria-invalid="true"] { border-color: var(--color-error-border); }
.field__help { font-size: var(--font-size-sm); color: var(--color-text-secondary); }
.field__error { font-size: var(--font-size-sm); color: var(--color-error-text); display: flex; gap: var(--spacing-1); }
```

- Label visible OBLIGATORIO (`<label for>`); placeholder NUNCA reemplaza al label. Requeridos marcados con `*` + texto accesible.
- Validación en `blur` y en `submit`, NUNCA por tecla. Error debajo del campo con icono, conectado por `aria-describedby`; tras un submit fallido con varios errores, foco al resumen de errores enlazado.
- Tipos semánticos (`email`, `tel`, `number`, `url`, `search`, `date`) y `autocomplete` correctos. Solo lectura ≠ deshabilitado (visual y semánticamente).

### Select (US 145683, HU 8.4.3)

Primitiva de `shared/ui` (`frontend/src/shared/ui/select/`): un `<select>` **nativo**, el selector más accesible en móvil. Es el `.field` de Inputs con su `.field__input`, más estas reglas:

- **Etiqueta:** visible encima del campo, asociada con `for`/`id` (`.field__label`). NUNCA solo un placeholder ni una opción vacía como etiqueta.
- **Campo:** borde `--border-thin` `--color-border-input` (3,45:1 sobre surface y background), fondo `--color-surface`, `--radius-md`, alto `touch-target` (≥ 44 px), `focus-ring` y `w-full` en base. Usa `appearance: none` para pintar su propia marca y deja `padding-right` libre para ella.
- **Marca:** `chevron-down` en `icon-sm`, `aria-hidden`, en un contenedor `relative` con `pointer-events: none` para que el clic llegue al `<select>`. Sin `z-index` numérico.
- **Opciones:** las da quien la usa (`{ value, label }`). La primitiva no tiene lógica de negocio ni variantes booleanas.
- **Teclado y lectores:** los del `<select>` nativo; NUNCA se reemplaza por un listbox propio.

### Cards [SETI §8, §24.2]

```css
.card {
  width: 100%;
  background: var(--color-surface);
  border: var(--border-thin) solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-sm);
}
.card--interactive { cursor: pointer; transition: box-shadow var(--transition-base), border-color var(--transition-base); }
.card--interactive:hover { box-shadow: var(--shadow-md); border-color: var(--color-border-strong); }
.card--interactive:focus-visible { outline: var(--border-medium) solid var(--color-border-focus); outline-offset: var(--border-medium); }
```

- Cards homogéneas dentro de la grilla; el texto largo usa scroll interno o truncado con texto completo accesible, NUNCA deforma la grilla. Sin `translateY` en hover.

### Modales [SETI §9]

```css
.modal__overlay { position: fixed; inset: 0; background: var(--color-overlay); z-index: var(--z-overlay); }
.modal {
  position: fixed; inset: 0; z-index: var(--z-modal);
  background: var(--color-background-elevated);
  padding: var(--spacing-6);
  overflow-y: auto;
}
@media (min-width: 768px) {
  .modal { inset: auto; top: 50%; left: 50%; transform: translate(-50%, -50%);
           width: 90%; max-height: 85vh; border-radius: var(--radius-xl);
           padding: var(--spacing-8); box-shadow: var(--shadow-xl); }
}
@media (min-width: 992px) {
  .modal--sm { max-width: var(--modal-width-sm); }
  .modal--md { max-width: var(--modal-width-md); }
  .modal--lg { max-width: var(--modal-width-lg); }
}
```

- Overlay obligatorio; `Escape` cierra; focus trap; el foco vuelve al disparador al cerrar; botón de cerrar visible con `aria-label`. `role="dialog"` + `aria-modal="true"` + `aria-labelledby`.
- Confirmar antes de cerrar un modal con cambios sin guardar. NUNCA usar modales para la navegación principal.

### Tablas [SETI §10, §24.1]

- SIEMPRE dentro de `<div class="table-wrapper">` con `overflow-x: auto; width: 100%`.
- Header `background: var(--color-background-alt)`; hover de fila `background: var(--color-surface-hover)`; divisores `--color-border`.
- Mobile (< 768): card-view, cada fila es una card con pares `label: valor` (`<dl>`); NUNCA tabla horizontal sin overflow.
- Columnas ordenables con `aria-sort`; números alineados a la derecha con `tabular-nums`; más de 50 filas → paginación o virtualización.

### Badges [SETI §11]

- `font-size: var(--font-size-xs)`, `border-radius: var(--radius-full)`, `padding: 0 var(--spacing-2)`, `min-height: 20px`.
- Variantes de estado: `background: var(--color-<estado>-bg)`, `color: var(--color-text-primary)`, `border: var(--border-thin) solid var(--color-<estado>-border)`. Neutro: `--color-background-alt` + `--color-text-secondary`.
- Marca: `--color-primary-light` + texto `--color-error-text` (light 5.72:1, dark 4.89:1). NUNCA texto blanco sobre `--color-primary`.
- En la SPA, la variante neutra es la utilidad `badge-neutral` (DISCIPLINA DE TOKENS): el alto mínimo de 20px no tiene token y Tailwind no lo genera (US 145674, badge "Próximamente" del menú de módulos).

### Tooltips [SETI §12]

- `background: var(--color-tooltip-bg)`, `color: var(--color-tooltip-text)`, `font-size: var(--font-size-sm)`, `border-radius: var(--radius-sm)`, `z-index: var(--z-tooltip)`, retardo 300ms.
- Se abren con hover Y con foco de teclado; `Escape` los cierra; NUNCA contienen información exclusiva ni acciones.

### Toasts [SETI §13]

- Arriba a la derecha (`z-index: var(--z-toast)`), 5 s, máximo 3 apilados; pausa al hover/foco.
- `aria-live="polite"` (errores críticos: `role="alert"`); NUNCA roban el foco. Estilo = bloque de estado (bg/border/icon + texto primario). Acciones destructivas ofrecen "Deshacer".

### Breadcrumbs [SETI §14]

- `<nav aria-label="Ruta de navegación">` + `<ol>`; separador `/` o `›` con `aria-hidden="true"`; el último ítem no es enlace y lleva `aria-current="page"`. Obligatorio desde 3 niveles de profundidad.

### Paginación [SETI §15]

- Máximo 7 ítems visibles (con `…`); mobile simplificado: "Anterior · Página N de M · Siguiente". `aria-current="page"` en la actual; targets ≥ 44px.

### Filtros [SETI §28]

- Desktop (`md`+): dropdown multiselección. Mobile (base/`sm`): drawer bottom-sheet multiselección.
- Trigger único; opciones con checkbox; acciones `Aplicar` y `Limpiar`; `Escape` cierra en desktop, botón de cierre explícito en mobile.
- Resumen: chips + contador; máximo 5 chips visibles y el excedente como `+N` operable (abre la lista completa).
- Abrir/cerrar filtros NO genera layout shift ni empuja contenido crítico fuera del viewport. Teclado completo, foco visible, selección indicada por texto/estructura (check + `aria-checked`), no solo por color.

### Header y sidebar

- Header: `height: var(--layout-header-height)`, `position: fixed`, `z-index: var(--z-header)`, `background: var(--color-surface)` (claro, UX-08 resuelto), borde inferior `--color-border`. Contiene: botón de menú (hasta `lg`), logo SF96 + "SETI 96" (enlace al Home), menú de módulos (desde `xl`), búsqueda y menú de usuario cuando exista autenticación.
- **Menú de módulos** (RQ-0005, sección "Menú de módulos"):
  - `<nav aria-label="Módulos">` con un ítem por módulo; etiquetas cortas (Prácticas, Aprendizaje, Activos, Verificación, Arquitecturas, Experto, Estimación) y el nombre completo en el `h1` de cada página.
  - Orden, etiquetas y estado salen de los datos (`modules`), nunca escritos en el componente. Orden fijo: 1, 7, 4, 5, 3, 6, 2.
  - Ítem activo: indicador inferior `--color-primary` de `--border-medium` + `--font-weight-semibold` + `aria-current="page"`. Hover: `--color-surface-hover`.
  - Módulo no construido: badge "Próximamente" (texto, no solo color). NUNCA deshabilitado ni oculto. Su destino depende de si tiene maqueta declarada (ADR-0028 §4, HU 8.8.1):
    - con maqueta: su ruta, donde vive la maqueta (ver Franja de maqueta);
    - sin maqueta: la página en construcción (`/en-construccion/modulos/<id>`).
  - Ítems con icono (ver ICONOGRAFÍA) + texto; touch target ≥ 44×44px.
  - Detalle (US 145674, HU 8.2.1):
    - Un solo `<nav aria-label="Módulos">` a la vez: desde el breakpoint del menú horizontal (ver LAYOUT / RESPONSIVE), en el header a continuación del logo; por debajo, dentro del drawer de módulos. NUNCA las dos variantes en el DOM.
    - **Horizontal:** ítems en fila separados `--spacing-1`. Cada ítem es una columna centrada: línea 1 con el icono `--icon-size-md` y la etiqueta `--font-size-sm` (separación `--spacing-1`); línea 2, el badge si lo hay. Padding `--spacing-1` × `--spacing-2`, `--radius-md`, `touch-target`. Indicador del activo: borde inferior `--border-medium` `--color-primary`.
    - **Drawer:** una fila por módulo, ancho completo del panel: icono (sin encogerse) + una columna con la etiqueta `--font-size-base` y, debajo, el badge (con la etiqueta y el badge en la misma línea, "Arquitecturas" no cabe en `--layout-sidebar-width`); padding `--spacing-2` × `--spacing-3`, separación `--spacing-1`, `touch-target`. Indicador del activo: borde izquierdo `--border-medium` `--color-primary`. Ningún ítem desborda el panel (lo verifica `module-menu.spec.ts`).
    - Badge "Próximamente": variante neutra de Badges (`badge-neutral`).
    - Estados: `loading` = el `nav` con `aria-busy="true"` y su alto reservado; `error` = "No fue posible cargar el menú." como alerta y un botón "Reintentar" (`touch-target`, `focus-ring`); `empty` no aplica (el esquema exige al menos un módulo).
- **Drawer de módulos** (US 145674, HU 8.2.1): por debajo del breakpoint del menú horizontal, el header muestra primero un botón de solo icono (`menu`, `aria-label="Abrir el menú de módulos"`, `aria-expanded`, `aria-controls`) y después el logo.
  - Es un `<dialog>` modal (`showModal()`): el navegador contiene el foco, deja inerte el resto de la página y lo pone en el top layer, por encima del header y del skip link. Por eso no usa `--z-overlay` ni `--z-modal` (que siguen rigiendo para el drawer del sidebar).
  - Panel izquierdo de ancho `--layout-sidebar-width` (`w-sidebar`) y alto `100dvh`; fondo `--color-surface`, borde derecho `--border-thin` `--color-border`, padding `--spacing-4`. `::backdrop` = `--color-overlay`.
  - Primer elemento: el botón de cerrar (`x`, `aria-label="Cerrar el menú de módulos"`), arriba a la derecha; después, el `nav` "Módulos".
  - Se cierra con Escape, con el botón de cerrar, con un clic en el backdrop y al navegar. Al cerrarse sin navegar, el foco vuelve al botón de menú.
  - Entrada con `transform` (desde `-100%` en X) en `--transition-fast`; sin movimiento con `prefers-reduced-motion` (bloque de KEY EFFECTS).
- Sidebar: `position: fixed`, `z-index: var(--z-sidebar)`, `background: var(--color-surface)`, borde derecho `--color-border`. Contiene SOLO las secciones internas del módulo activo; un módulo sin secciones no muestra sidebar y el content ocupa el ancho. Ítems con icono + texto (en colapsado, texto en tooltip y `aria-label`); ítem activo con indicador `--color-primary` + peso semibold + `aria-current="page"`.
- **Hero del Home:** banda `background: var(--color-surface-inverse)`, texto `--color-text-inverse`, bajo el header y solo en el Home (ver `pages/home.md`). Es la única superficie oscura en light mode. Detalle (US 145671, HU 8.1.4):
  - Composición: `<section>` de ancho completo, primer bloque del content; contenedor `--layout-container-max-width` centrado, con el padding horizontal del header (base `--spacing-4`, `md` `--spacing-6`, `lg` `--spacing-8`) y vertical `--spacing-12` (base) / `--spacing-16` (desde `md`); elementos en columna separados `--spacing-4`.
  - Tipografía: nombre del portal = el único `h1` de la vista (tabla de jerarquía: `--font-size-2xl` → `--font-size-3xl` en `md` → `--font-size-4xl` en `lg`, bold, `--line-height-tight`); frase de propósito `--font-size-md` (base) / `--font-size-lg` (desde `md`), `--line-height-relaxed`, medida `--layout-measure`; versión y fecha `--font-size-sm` con `tabular-nums`. Todo el texto en `--color-text-inverse`.
  - Contenido: nombre, frase, versión y fecha salen de los datos (`catalog`), nunca escritos en el componente; la fecha va en `<time datetime="AAAA-MM-DD">` con formato largo es-CO.
  - `loading`: la misma banda con `aria-busy="true"`, un texto solo para lector de pantalla ("Cargando la presentación del portal") y bloques `aria-hidden` en `--color-surface-inverse-raised` con `--radius-sm`, de la altura de cada línea del estado final (sin layout shift). Sin animación.
  - `error`: la misma banda con la causa como alerta (`role="alert"`, `--color-text-inverse`) y el botón "Reintentar" en `.btn--secondary-inverse`.
  - `empty` no aplica: el esquema del catálogo exige todos los campos.

### Pie del sitio

- `<footer>` (landmark `contentinfo`) único, montado una vez en el shell, después del content y NUNCA dentro de `main`. Ancho completo, borde superior `--border-thin` `--color-border`, fondo `--color-background`.
- Contenedor `--layout-container-max-width` centrado, con el padding horizontal del header (base `--spacing-4`, `md` `--spacing-6`, `lg` `--spacing-8`) y vertical `--spacing-8`; elementos separados `--spacing-4`.
- Logo corporativo SETI (`frontend/img/logo-seti.svg`, `alt="SETI"`, ver Identidad y logotipos) a 40 × 40 px (`viewBox` cuadrado), con área de protección `--spacing-2`. No es un enlace. El arco negro exige fondo claro.
- Nota metodológica (solo en el Home, `pages/home.md`): `--font-size-sm`, `--line-height-relaxed`, `--color-text-secondary`; cada párrafo abre con un rótulo en `--font-weight-semibold` `--color-text-primary`; párrafos con medida `--layout-measure` y separación `--spacing-2`. Sin encabezados `h*`: el pie no altera la jerarquía de la página.

### Skip link [FIJO]

- Primer elemento enfocable: "Saltar al contenido" → `#main` (el `id` es para el ancla, nunca como selector CSS); visible al recibir foco.
- Sin foco: oculto a la vista con un recorte (patrón `sr-only`), nunca con `display: none` ni `visibility: hidden`, para que siga en el árbol de accesibilidad.
- Con foco (`:focus`): fijo arriba a la izquierda (`--spacing-2`), en la capa `--z-modal` (por encima del header), fondo `--color-surface`, texto `--color-text-link`, `--radius-md`, padding `--spacing-3` × `--spacing-4` (área ≥ 44 × 44px) y el anillo de `focus-ring`.
- Al activarlo, el foco pasa al `main` (`tabindex="-1"`) sin cambiar la ruta ni el hash de la URL.

### Página en construcción (US 145674, HU 8.2.1)

- Destino de todo enlace a algo que todavía no existe (RQ-0004 D5); NUNCA un 404. La variante de módulo vive en `/en-construccion/modulos/<id>`; las de guía y activo las agrega la HU 9.4.1.
- Contenedor `--layout-container-max-width` centrado con el padding de página (base `--spacing-4`, `md` `--spacing-6`, `lg` `--spacing-8`) y vertical `--spacing-12`; elementos en columna separados `--spacing-4`.
- `h1` = el nombre de lo que se espera (por ejemplo, el nombre completo del módulo), con la tabla de jerarquía de TIPOGRAFÍA. Es el único `h1` de la vista.
- Texto explicativo `--font-size-base`, `--line-height-relaxed`, `--color-text-secondary`, medida `--layout-measure`.
- Enlace al Home `--color-text-link`, subrayado, con `focus-ring` y área ≥ 44×44px (`touch-target`).
- El título del documento es "<nombre> · Portal SETI 96". Estados `loading` (`aria-busy="true"` + texto solo para lector de pantalla) y `error` (alerta + "Reintentar").

### Franja de maqueta (ADR-0028 §1, HU 8.8.1)

- Toda maqueta declarada (`frontend/src/pages/maqueta-*`) usa el layout de `shared/ui/mockup` (`MockupPage`), que pone la franja como PRIMER contenido de la página, antes del `h1`.
- Texto exacto: "Datos de ejemplo: esta pantalla no es funcional". NUNCA se puede cerrar, ocultar ni cambiar por página.
- Estilo de bloque de estado de advertencia: fondo `--color-warning-bg`, borde `--border-thin` `--color-warning-border`, `--radius-md`, padding `--spacing-3` × `--spacing-4`, texto `--font-size-base` en `--color-text-primary` (contraste AA sobre `--color-warning-bg`) e icono `alert-triangle` de `--icon-size-md` en `--color-warning-icon`, decorativo (`aria-hidden`), separado `--spacing-2`.
- Semántica: `role="note"` con `aria-label="Aviso de maqueta"`. NO es alerta dinámica (sin `role="alert"` ni `aria-live`) y NUNCA mueve el foco.
- Debajo: el nombre completo del módulo como único `h1` (tabla de jerarquía de TIPOGRAFÍA) y el contenido de la maqueta, con datos fijos y ficticios. El título del documento es "<nombre> · Portal SETI 96".
- Contenedor `--layout-container-max-width` centrado con el padding de página (base `--spacing-4`, `md` `--spacing-6`, `lg` `--spacing-8`) y vertical `--spacing-8`; elementos separados `--spacing-6`.

## ICONOGRAFÍA

- Un ÚNICO set SVG para todo el portal: **Feather** (licencia MIT, outline, trazo 2). UX-06 resuelto (RQ-0005 D4). El paquete que lo implementa en la SPA se incorpora como dependencia nueva según `frontend-standards.md`.
- PROHIBIDO emojis, PNG inline, mezclar sets o iconos custom sin documentar.
- Tamaños como tokens: `--icon-size-sm: 16px`, `--icon-size-md: 20px`, `--icon-size-lg: 24px`. `color="currentColor"`, trazo uniforme en la misma capa, un solo estilo (outline o solid) por nivel de jerarquía.
- Icono decorativo junto a texto → `aria-hidden="true"`. Icono con significado propio → texto alternativo. Botón de solo icono → `aria-label` + estado (`aria-pressed`/`aria-expanded`) si aplica.
- Mapeo de iconos por módulo (aprobado el 2026-10-02, US 145674): Prácticas `grid` · Aprendizaje `book-open` · Activos `package` · Verificación `check-square` · Arquitecturas `layers` · Experto `message-circle` · Estimación `bar-chart-2`. Menú `menu`, cerrar `x`, búsqueda `search` [PROPUESTA, sin uso todavía].
- Marcas de estado de cobertura de la matriz del Home (aprobadas el 2026-10-05, US 145681): cubierta `check` · a medio cubrir `minus` · sin cubrir `circle`, en `icon-sm` y `--color-text-primary`, siempre junto al estado en texto del nombre accesible (`pages/home.md`). `check` también marca el chip elegido del filtro por dominio.
- Riesgo crítico de adherencia (US 145950): `alert-triangle` en `icon-sm`, `aria-hidden` y `--color-text-primary`. Marca la adherencia MAMP por debajo de 50 % en la columna de cada fase y en la tarjeta global del Home, SIEMPRE junto al texto "Riesgo crítico" o al veredicto (visible o en el nombre accesible); nunca comunica el riesgo sola ni con color (`pages/home.md`).
- Despliegue (US 145683): `chevron-down` en `icon-sm`, `aria-hidden`. Lo usan el Select y el botón que despliega las guías de una fase (gira 180° cuando está desplegado, con `transition` explícita de `transform` y sin giro con `prefers-reduced-motion`).
- Implementación en la SPA (decisión del usuario del 2026-10-02, sin dependencia nueva): los iconos que se usan se copian de Feather 4.29.2 como nodos JSX en `frontend/src/shared/ui/icon/`, con el aviso MIT de Feather en `FEATHER-LICENSE.txt`. NUNCA `innerHTML` ni cadenas SVG. Un icono nuevo se agrega ahí, copiado del mismo set. Tamaño con las utilidades `icon-sm`, `icon-md` e `icon-lg` (DISCIPLINA DE TOKENS).
- Mapeo por tipo de activo del módulo 4 [PROPUESTA]: skill `zap` · prompt `terminal` · plantilla `file-text` · servidor MCP `server` · herramienta `tool` · extensión `box`.

## NAVEGACIÓN [FIJO]

- Toda HU con pantalla se entrega con su punto de acceso: ruta registrada + enlace (ítem de menú o acción en página existente). Pantalla huérfana = INCOMPLETA.
- Navegación interna SOLO con la primitiva de routing (`Link`/`NavLink`); NUNCA `<a href>` interno (recarga la app y borra el JWT en memoria → logout).
- Navegación principal = menú de módulos del header; navegación secundaria = sidebar del módulo activo. Toda ruta de un módulo no construido lleva a su maqueta declarada (ADR-0028 §4) o, si no tiene, a la página en construcción; nunca a un 404.
- Tras un cambio de ruta, el foco va al `h1` o a la región principal. Volver atrás restaura scroll, filtros y entradas. Ubicación de la navegación idéntica en todas las vistas.
- Acciones peligrosas (cerrar sesión, eliminar) separadas visual y espacialmente de la navegación normal.

## ACCESIBILIDAD [FIJO]

- WCAG 2.1 AA mínimo; contraste ≥ 4.5:1 en texto y ≥ 3:1 en límites de controles, iconos con significado y foco.
- Teclado completo; orden de tabulación = orden visual; foco visible (`:focus-visible`, nunca `outline: none` sin reemplazo); elementos fijos o superpuestos NUNCA tapan el control enfocado.
- `alt` en imágenes con significado; `alt=""` en decorativas. Skip link. Regiones `aria-live` para resultados y estados asíncronos.
- Jerarquía `h1`→`h6` sin saltos. Nunca comunicar estado solo con color u opacidad.
- Touch targets ≥ 44×44px en mobile; objetivos de puntero web ≥ 24×24px.
- Soporta escalado de texto del navegador hasta 200% sin pérdida de contenido.

## AVOID (Anti-patterns)

- NUNCA generar paletas/tipografías/estilos nuevos; solo tokens de este archivo.
- NUNCA hex/rgb/hsl "quemado" si existe token; NUNCA `px` en `font-size`; NUNCA espaciado fuera de `--spacing-*`; NUNCA `z-index` manual.
- NUNCA acción primaria y secundaria del mismo color; NUNCA color de marca como estado; NUNCA texto blanco sobre `--color-primary` (`#E0352B`).
- NUNCA saltar niveles de encabezado; NUNCA `display:none` como estrategia responsive; NUNCA gráficos de ancho fijo (`width:100%` + colores por variable).
- NUNCA emojis como iconos; NUNCA `<a href>` interno; NUNCA pantalla sin navegación.
- NUNCA `!important`, selectores por `id`, más de 3 niveles de anidación ni más de 2 familias tipográficas.
- NUNCA `transition: all`; NUNCA animar propiedades de layout; NUNCA hovers que desplacen el layout.
- Del skill (estilo Minimalism enterprise): NUNCA diseño lúdico, gradientes morado/rosa "IA", glassmorphism ni blur decorativo.
- Del proyecto: NUNCA usar el azul/naranja del logo SF96 como color de UI; NUNCA servir los PNG de origen; NUNCA mostrar los logos sin placa clara en dark mode.

Regla final [SETI §22]: todo componente que no use tokens, rompa el layout, ignore responsive o accesibilidad, use hex directos, `px` en `font-size`, espaciado libre, `z-index` manual, `!important`, `id` en CSS, más de 2 fuentes o salte encabezados se DETECTA, RECHAZA, AUTOCORRIGE y REVALIDA antes de entregarse.

## DISCIPLINA DE TOKENS Y MAPEO TAILWIND [FIJO]

- La SPA usa Tailwind CSS v4, que se configura en CSS y no con `tailwind.config`. El mapeo vive en `frontend/src/app/styles/` (decisión del change `portal-tokens-design-system`, HU 8.1.1):

| Archivo | Contenido |
|---|---|
| `tokens.css` | `:root` con los tokens de este Master que NO tienen namespace de tema en Tailwind: `--color-*-rgb`, `--font-family-*`, `--font-size-*`, `--line-height-*`, `--letter-spacing-*`, `--layout-*`, `--border-*`, `--z-*`, `--transition-*`, `--icon-size-*`, `--modal-width-*`. |
| `theme.css` | `@theme static`: reinicia la paleta, las escalas y los breakpoints por defecto de Tailwind y declara, con su nombre y valor de este Master, los tokens cuyo prefijo ya es un namespace de Tailwind (`--color-*` salvo `-rgb`, `--spacing-*`, `--radius-*`, `--shadow-*`, `--font-weight-*`) y los breakpoints SETI. `@theme inline`: alias con el nombre que espera Tailwind hacia `tokens.css` (`--text-*`, `--font-base`, `--font-mono`, `--leading-*`, `--tracking-*`, `--z-index-*`, `--transition-duration-*`, `--default-font-family`) y los alias del shell (`--spacing-header` → `--layout-header-height`, `--container-page` → `--layout-container-max-width`; change `portal-site-header`, HU 8.1.2) y de la medida de lectura (`--container-measure` → `--layout-measure`; change `portal-site-footer-a11y`, HU 8.1.3) y del ancho del drawer de módulos (`--container-sidebar` → `--layout-sidebar-width`; change `portal-module-menu`, HU 8.2.1). |
| `base.css` | `@layer base`: RESET CSS de este Master, `color-scheme: light` y `scroll-padding-top` igual al alto del header en `html`. Fuera de capas: el bloque `prefers-reduced-motion` de KEY EFFECTS. |
| `utilities.css` | `@utility focus-ring`: el foco visible de este Master (COMPONENTS › Botones) con tokens exactos, solo en `:focus-visible`. `@utility skip-link`: el Skip link de COMPONENTS (oculto sin foco; visible y fijo con foco). `@utility btn-secondary-inverse`: `.btn` + `.btn--secondary-inverse` de COMPONENTS › Botones con tokens exactos (Tailwind no tiene token para el ancho de borde ni para el alto mínimo de 44 px; change `portal-home-hero`, HU 8.1.4). `@utility icon-sm`, `icon-md`, `icon-lg`: ancho y alto de un icono = `--icon-size-*` (no tienen namespace de Tailwind). `@utility touch-target`: ancho y alto mínimos de 44 px (Touch targets de LAYOUT / RESPONSIVE). `@utility badge-neutral`: la variante neutra de Badges con su alto mínimo de 20 px. `@utility indicator-bottom` / `indicator-start`: borde inferior / izquierdo de `--border-medium` transparente que reserva el indicador del ítem del menú de módulos y toma `--color-primary` en el ítem con `aria-current="page"` (Tailwind no tiene token para el ancho de borde; change `portal-module-menu`, HU 8.2.1). `@utility pressable-frame`: borde sólido constante de `--border-medium` (el color lo da una clase `border-*`) que, con `aria-pressed="true"`, toma `--color-text-primary` y `--font-weight-bold`, sin cambiar el tamaño del control; la usan los chips del filtro por dominio y las celdas de la matriz del Home (change `portal-coverage-matrix`, HU 8.4.1). `@utility pressed-glow`: con `aria-pressed="true"`, halo difuso `0 0 --spacing-3 --spacing-1 rgba(--color-primary-rgb, 0.6)` y `position: relative` para pintarlo sobre las vecinas; solo la celda seleccionada de la matriz del Home (`pages/home.md`). |
| `index.css` | Orden de carga: `tailwindcss` → `tokens.css` → `theme.css` → `base.css` → `utilities.css`. |

- Cada token de color, spacing, fontSize y zIndex DEBE existir en el documento con el mismo nombre y valor de este Master y estar mapeado en `theme.css`. Si un token no está mapeado, NO se usa en clases. NUNCA se declara el mismo nombre en `tokens.css` y en `theme.css` (referencia circular).
- Una clase que no sale de un token NO genera CSS (`bg-red-500`, `p-7`, `rounded-3xl`, `min-h-11`): la paleta y las escalas de Tailwind están reiniciadas. Para agregar un valor, se extiende PRIMERO este Master (así entraron `--spacing-0` y `--layout-measure`).
- Excepción conocida: `max-w-prose` SÍ genera CSS (`65ch` literal, utilidad estática de Tailwind). PROHIBIDO usarla; la medida de lectura es `max-w-measure`.
- Los alias del shell generan todas las utilidades de espaciado y de ancho (también `m-header` o `gap-header`), pero se usan SOLO para el header y para reservar su alto en el contenido. NUNCA `h-16`/`pt-16` en su lugar: hoy valen 64 px por coincidencia con `--layout-header-height`.
- Usar clases semánticas, NUNCA valores arbitrarios (`bg-[#...]`, `p-[13px]`), el atajo de variable (`bg-(--color-primary)`), el modificador de opacidad sobre un color (`bg-primary/10`) ni el de importancia (`!p-4`, `p-4!`). Las transparencias se construyen con los tokens `-rgb` o con los tokens compuestos (`--color-overlay`, `--color-focus-ring`).

| Token | Clase de ejemplo |
|---|---|
| `--color-action-primary` / `--color-text-primary` / `--color-border-input` | `bg-action-primary` / `text-text-primary` / `border-border-input` |
| `--spacing-4` | `p-4`, `m-4`, `gap-4` |
| `--font-size-base` / `--font-family-base` / `--font-weight-semibold` | `text-base` / `font-base` / `font-semibold` |
| `--line-height-normal` / `--letter-spacing-wide` | `leading-normal` / `tracking-wide` |
| `--radius-md` / `--shadow-sm` | `rounded-md` / `shadow-sm` |
| `--z-header` / `--transition-fast` | `z-header` / `duration-fast` |
| `--spacing-0` | `top-0`, `inset-x-0`, `p-0`, `gap-0` |
| `--layout-header-height` / `--layout-container-max-width` | `h-header`, `pt-header`, `scroll-pt-header` / `max-w-page` |
| `--border-medium` + `--color-border-focus` + `--spacing-1` + `--color-focus-ring` | `focus-ring` (solo en `:focus-visible`) |
| `--layout-measure` | `max-w-measure` |
| Skip link (`--spacing-2`, `--spacing-3`, `--spacing-4`, `--z-modal`, `--color-surface`, `--color-text-link`, `--radius-md`) | `skip-link` (visible solo en `:focus`) |
| `--color-surface-inverse-raised` | `bg-surface-inverse-raised` (SOLO sobre el hero) |
| Botón secundario inverso (`.btn` + `.btn--secondary-inverse`) | `btn-secondary-inverse` (SOLO sobre el hero; el foco lo da `focus-ring`) |
| `--icon-size-sm` / `--icon-size-md` / `--icon-size-lg` | `icon-sm` / `icon-md` / `icon-lg` (ancho y alto del `svg`) |
| Touch target ≥ 44×44px (LAYOUT / RESPONSIVE) | `touch-target` (`min-width` y `min-height` de 44 px) |
| Badge neutro (`--font-size-xs`, `--radius-full`, `--spacing-2`, `--color-background-alt`, `--color-text-secondary`) | `badge-neutral` |
| `--layout-sidebar-width` | `w-sidebar` (SOLO el panel del drawer de módulos y, más adelante, el sidebar) |
| `--border-medium` + `--color-text-primary` + `--font-weight-bold` (control con `aria-pressed`) | `pressable-frame` (chips del filtro y celdas de la matriz del Home) |
| Halo `--color-primary` de la celda seleccionada (control con `aria-pressed`) | `pressed-glow` (solo celdas de la matriz del Home) |
| Indicador del ítem activo (`--border-medium` + `--color-primary`) | `indicator-bottom` (horizontal) / `indicator-start` (drawer); el color se aplica solo con `aria-current="page"` |

- Breakpoints de Tailwind redefinidos a los de SETI (los de Tailwind por defecto son distintos):

```css
@theme static {
  --breakpoint-*: initial;
  --breakpoint-sm: 576px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 992px;
  --breakpoint-xl: 1200px;
  --breakpoint-2xl: 1440px;
}
```

- Verificación automática en `frontend/`: `pnpm test:integration` compara cada token de este Master con el CSS que genera el build y comprueba las clases que se generan y las que no; `pnpm lint` rechaza en los componentes colores literales, valores arbitrarios, `!important`, opacidades sobre colores y la variante `dark:`.

- En SVG y gráficos (Tailwind no aplica) los colores van por variable en props o `style`: `stroke="var(--color-border)"`, ``fill={`rgba(var(--color-primary-rgb), 0.04)`}``. PROHIBIDO `stroke="#E8E8E8"`.

## RESET CSS [SETI §21]

```css
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: var(--font-family-base); font-size: var(--font-size-base);
       line-height: var(--line-height-normal); color: var(--color-text-primary); background: var(--color-background); }
img, svg, video { max-width: 100%; height: auto; display: block; }
table { width: 100%; border-collapse: collapse; }
button, input, select, textarea { font: inherit; color: inherit; }
button { background: none; border: 0; padding: 0; cursor: pointer; }
```

## VALIDACIÓN A RUNTIME [FIJO]

- Antes de cerrar un cambio visual, validar con `getComputedStyle()` que los estilos materializados coinciden con los tokens definidos (colores de shell, `z-index` por capa, overlay opaco, contraste ≥ 4.5:1 en áreas críticas), en light Y en dark.
- Si un token no materializa: revisar build de CSS/Tailwind y definición en `:root`.

## GATE DE APROBACIÓN (5 pasos, en orden) [FIJO]

1. Conformidad de tokens (solo clases semánticas; sin hex directo; mapeo en `frontend/src/app/styles/theme.css`).
2. Estructura del shell (sidebar/header/content, z-index y colores correctos).
3. Composición canónica de la vista (orden y jerarquía definidos en `pages/<pagina>.md`).
4. Iconografía (set único, sin emojis, tamaños consistentes, `aria-label`).
5. Validación runtime (paridad de estilos, capas, contraste, overlay).

- Falla cualquiera → RECHAZAR y pedir corrección. Todas las vistas comparten el mismo shell; una variación estética accidental se rechaza.

## PRE-DELIVERY CHECKLIST [FIJO]

- [ ] Solo tokens de este Master (sin colores/fuentes generados ni "quemados")
- [ ] Acción primaria (`--color-action-primary`) y secundaria (neutra) diferenciadas; máx. 1 primary por vista
- [ ] Tarjetas homogéneas; estados `loading/empty/success/error` explícitos
- [ ] Pantalla alcanzable: ruta + enlace (navegación SPA con `Link`/`NavLink`)
- [ ] WCAG 2.1 AA: contraste ≥ 4.5:1 en light y dark, teclado, focus visible, skip link
- [ ] Touch targets ≥ 44×44px en mobile
- [ ] Responsive verificado en 375, 576, 768, 992, 1200 y 1440px; sin scroll horizontal
- [ ] Iconos SVG del set único (no emojis), `cursor: pointer` en clicables
- [ ] `prefers-reduced-motion` respetado; sin `transition: all`
- [ ] Nada oculto bajo el header o el sidebar fijos
- [ ] Logos oficiales sin alterar, en SVG aprobado y con placa clara en dark mode

## PENDIENTES (decisiones abiertas)

| ID | Tema | Estado en este Master | Decisión requerida |
|---|---|---|---|
| UX-01 | Blanco sobre `#E0352B` da 4.46:1 (< 4.5). | CTA y links usan `#C72E25`/`#B0281F`; `#E0352B` queda para marca, foco y gráficos. | Confirmar el ajuste o definir otra variante de rojo para acciones. |
| UX-02 | Terciario/placeholder `#A0A0A0` (2.61:1) y bordes de input `#C4C4C4` (1.74:1) no cumplen. | Terciario y placeholder → `#6B6B6B`; borde de input → `#8A8A8A` (ambos de la semilla). | Confirmar. |
| UX-03 | `system-design.md` exige dark mode pero no da valores. | Valores de la semilla + 5 nuevos verificados (`#F0625A`, `#F27A73`, `#16281B`, `#2E2610`, `#12292E`). La primera entrega del portal sale solo en light (RQ-0005 D19); falta el valor dark de `--color-surface-inverse`. | Aprobar la paleta dark. |
| UX-04 | El rojo de marca es idéntico al rojo de error (`--color-error: #E0352B`). | `danger` se distingue por contorno, icono, verbo y confirmación, no por color. | Confirmar, o definir un rojo de error distinto al de marca. |
| UX-05 | Tipografía: `system-design.md` dice Nunito Sans; la semilla `Cobertura_SF96.html` usa Montserrat. | Se usa Nunito Sans. | Confirmar y migrar la semilla. |
| UX-06 | Set de iconos. | **Resuelto 2026-09-30:** Feather (RQ-0005 D4). Mapeo por módulo aprobado e implementado el 2026-10-02 (US 145674): copias de Feather en `frontend/src/shared/ui/icon/`. | Ninguna. |
| UX-07 | Logos. | **Resuelto 2026-09-30:** SVG aprobados (`seti-96.svg`, `logo-seti.svg`); los PNG no se publican (RQ-0005 D10 y D20). | Definir la variante del logo SETI para fondo oscuro (el arco negro pierde contraste). |
| UX-08 | Colores de header y sidebar. | **Resuelto 2026-09-30:** header y sidebar `--color-surface` + borde; banda oscura `--color-surface-inverse` solo en el hero del Home (RQ-0005 D9). | Ninguna. |
| UX-09 | Series de gráficos más allá de la principal no definidas. | Ver `pages/dashboard.md`. | Definir la paleta categórica. |
| UX-10 | Escala de h2–h6 no definida (solo h1). | Tabla propuesta en TIPOGRAFÍA. | Confirmar. |
| UX-11 | §5 pide `transition: all`, pero también "SOLO opacity/transform" y el skill lo prohíbe. | Propiedades explícitas; movimiento solo con opacity/transform. | Confirmar la interpretación. |
