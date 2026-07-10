# Blindspot Audit

[English](./README.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [简体中文](./README.zh.md) | [Español](./README.es.md)

![Imagen principal de Blindspot Audit](./docs/assets/readme/en/hero.png)

Blindspot Audit es una skill portátil para agentes de IA que ayuda a encontrar lo que la persona dueña de un proyecto
todavía no sabe que está pasando por alto: unknown unknowns, riesgos ocultos, decisiones pendientes, supuestos viejos
y preguntas que nadie pensó hacer. Deja el resultado en `BLINDSPOT_LEDGER.md`.

Funciona con cualquier tipo de proyecto: software, juegos, novelas y escritura creativa, investigación, contenido o planes
de negocio. Puede usarse en Claude Code, Codex, OpenCode, la app de escritorio de Claude y chats normales. El núcleo de la
auditoría es el mismo; cada host solo adapta cómo pregunta y cómo guarda los resultados.

## Instalación en 60 segundos

| Qué usas | Una línea |
| --- | --- |
| Cualquier agente de programación — Claude Code, Codex, OpenCode, Cursor, ~70 hosts | `npx skills add MJL-ren/blindspot-audit` |
| Claude Code, con actualizaciones gestionadas | `/plugin marketplace add MJL-ren/blindspot-audit` y luego `/plugin install blindspot-audit@blindspot-audit` |
| App de escritorio de Claude / Cowork — sin terminal | Descarga [blindspot-audit.skill](https://github.com/MJL-ren/blindspot-audit/releases/latest/download/blindspot-audit.skill), adjúntalo en el chat y pulsa **Save skill** |

Después prueba tu primer prompt:

```text
Run a blindspot audit on this project. What am I missing that I don't even know to ask about?
```

La ruta `npx` usa [vercel-labs/skills](https://github.com/vercel-labs/skills):
instala la carpeta completa de la skill y envía telemetría anónima de
instalación (se desactiva con `DISABLE_TELEMETRY=1`). La skill en sí nunca
toca la red por su cuenta — ver [SECURITY.md](./SECURITY.md). El resto de
rutas — instalación por proyecto, marketplace de Codex, scripts sin conexión,
dejar que tu agente lo haga — están en [Instalación](#instalación).

## Qué hace

![Marco de los cuatro tipos de desconocimiento](./docs/assets/readme/en/four-unknowns.png)

- Perfila el proyecto: tipo, etapa, experiencia de la persona dueña, si es hobby o comercial. Primero lee los documentos que el
  proyecto ya usa para seguirse a sí mismo, como TODOs, checklists y roadmaps. **Todo lo que ya esté rastreado se filtra y no se
  reporta como un nuevo descubrimiento.**
- En la primera ejecución recopila el contexto mínimo que cambia la auditoría (intención pública o comercial, audiencia y regiones,
  etapa, fortalezas de la persona dueña; toda pregunta se puede omitir) y lo guarda en la sección `Project Context` del ledger,
  para que las siguientes ejecuciones lo lean en vez de volver a preguntar.
- Revisa el proyecto con lentes específicos para su arquetipo. Registra evidencia tanto de lo que falta como de lo que ya está bien cubierto.
- Hace un escaneo web con mirada fresca para detectar cambios recientes externos: regulación, políticas de plataformas, cambios de mercado
  o de género. Muchas veces los hallazgos de más impacto vienen de ahí.
- Reporta entre 3 y 7 hallazgos priorizados, no una lista infinita. Siempre incluye dos secciones de confianza: «qué está bien cubierto»
  y «qué se puede omitir por ahora», con señales para volver a revisar.
- Entrevista a la persona dueña sobre qué hallazgos ya conocía. Una brecha conocida necesita una línea accionable, no una explicación larga.
- Se enfoca cuando hace falta: una ejecución `focus: ux-ui` carga un paquete de sondas profundas para ese dominio,
  y la auditoría completa no pasa en silencio por las superficies de los dominios débiles del dueño
  (la UI de un ingeniero, las operaciones de un diseñador): lo reporta como hallazgo. Habrá más paquetes con el tiempo.
- Mantiene un `BLINDSPOT_LEDGER.md` duradero (el cuaderno que la auditoría deja en tu proyecto). Las siguientes ejecuciones comparan contra ese archivo y reportan solo lo nuevo o cambiado.
  Y cuando nada cambió, la ejecución desciende un nivel (paquetes sin ejecutar, revisión de la lista de vigilancia,
  el subsistema menos inspeccionado) en vez de volver con las manos vacías.

![Flujo de auditoría de Blindspot Audit](./docs/assets/readme/en/audit-flow.png)

## Cómo se ve un hallazgo

Una auditoría débil dice «Falta el aviso de privacidad del artículo 13 del
RGPD». Esta skill está construida para decirlo de forma que puedas
reconocerlo y actuar:

```markdown
1. The site collects email addresses but never tells people what happens
   to them
   - In plain terms: when a site stores personal data like emails, most
     regions require a short public note (a "privacy policy") saying what
     is collected and how to get it deleted. It is a page, not a lawsuit -
     but its absence can become one.
   - Why it matters: the signup form is live and EU visitors can reach it;
     this is the kind of gap that is cheap now and expensive after launch.
   - Cheapest check: read one privacy-policy generator's output (10 min)
     and confirm with a professional before launch - this audit is a
     scout, not a lawyer.
```

Hay cinco reportes sintéticos completos en
[examples/sample-reports/](./examples/sample-reports/) — empieza por
[weak-vs-strong.md](./examples/sample-reports/weak-vs-strong.md), que
muestra los mismos tres hallazgos escritos para fallar y para pasar. Los
reportes reales se escriben en el idioma en el que trabajas; solo los ID y
los valores de status quedan en inglés.

## Tu primera auditoría

1. Pídela con tus palabras (hay prompts en [Uso](#uso)).
2. En la primera ejecución hace 1–2 preguntas breves de contexto — todas
   se pueden omitir.
3. Recibes de 3 a 7 hallazgos priorizados, más lo que ya está bien
   cubierto y lo que puedes omitir por ahora.
4. Te pregunta qué hallazgos ya conocías — una brecha conocida recibe una
   línea accionable en vez de una lección.
5. Deja UN archivo: `BLINDSPOT_LEDGER.md`, el cuaderno de la auditoría en
   tu proyecto. Las siguientes ejecuciones lo leen y reportan solo lo que
   cambió. El archivo es tuyo — haz commit o añádelo a `.gitignore`.

## ¿Por qué no basta con preguntar «qué me falta»?

Un prompt suelto parte de cero cada vez: vuelve a «descubrir» lo que ya
rastreas, da lecciones donde bastaría una línea accionable y lo olvida todo
en la siguiente sesión. Esta skill filtra tus propios documentos de
seguimiento fuera de los hallazgos, te entrevista para tratar distinto las
brechas conocidas y los puntos ciegos reales, y compara contra el ledger
para que cada repetición reporte progreso en vez de repetirse.

Cómo saber que funciona: una repetición reporta deltas, no la misma lista
dos veces; cada hallazgo trae una consecuencia concreta y la comprobación
más barata, nunca una buena práctica genérica; y cada versión se califica
con ejecuciones reales — ver [evals/RUNS.md](./evals/RUNS.md).

## Focus: UX/UI

![Enfoque UX/UI de Blindspot Audit](./docs/assets/readme/en/ux-ui-focus.png)

`focus: ux-ui` sirve para proyectos con pantallas reales para usuarios, donde una auditoría amplia solo miraría la
interfaz por encima. Recorre pantallas, flujos, estados, entradas, accesibilidad y feedback como preguntas de punto ciego:
qué nunca se decidió, dónde puede quedarse bloqueado el usuario y qué comprobación barata haría visible la brecha.

Úsalo cuando una auditoría completa marque UX/UI como deuda de cobertura, o cuando la persona dueña sea fuerte en otras áreas
y quiera una pasada más profunda sobre la superficie de usuario.

No es una checklist genérica de calidad. La pregunta que responde es:

> Dado este proyecto específico, ¿qué es probable que todavía no estemos viendo?

## Ledger Triage

`mode: ledger-triage` sirve para proyectos que ya tienen un
`BLINDSPOT_LEDGER.md` cargado. No ejecuta una auditoría nueva. Lee el ledger
existente y agrupa filas abiertas en limpieza rápida, aceptaciones seguras,
decisiones agrupadas, preguntas que necesitan detalle de la persona dueña,
confirmaciones externas y elementos que necesitan una explicación más simple.

En hosts sin una UI de selección estructurada, los lotes grandes pueden usar
un HTML decision board temporal y autocontenido dentro de `.blindspot-tmp/`.
La persona dueña elige en el navegador, el agente valida el response JSON,
aplica solo las actualizaciones elegidas del ledger y después borra el board
temporal. Las recomendaciones del board no se aplican hasta que la persona
dueña las elige.

## Estructura del repositorio

```text
blindspot-audit/
  .agents/
    plugins/marketplace.json     # marketplace de plugins de Codex
  .claude-plugin/
    marketplace.json / plugin.json  # marketplace de plugins de Claude Code
  AGENTS.md
  CHANGELOG.md
  README.md
  README.ko.md
  README.ja.md
  README.zh.md
  README.es.md
  LICENSE
  dist/
    blindspot-audit.skill        # instalación de un clic para la app de escritorio de Claude
  evals/
    fixtures/                    # fixtures de regresión de comportamiento (con criterios EXPECTED)
  examples/
    prompts.md
    sample-reports/              # reportes sintéticos que muestran la forma de salida esperada
  scripts/
    build-skill-package.py / .ps1 / .sh
    install-claude-user.ps1 / .sh
    install-claude-project.ps1 / .sh
    install-codex.ps1 / .sh
    sync-codex-plugin.py / .ps1 / .sh
    verify-codex-plugin.py
  plugins/
    blindspot-audit/
      .codex-plugin/plugin.json  # manifest del plugin de Codex
      skills/blindspot-audit/
  skills/
    blindspot-audit/
      SKILL.md
      references/
      scripts/
      templates/
```

## Instalación

Las tres rutas recomendadas están arriba, en
[Instalación en 60 segundos](#instalación-en-60-segundos). Lo de abajo es el
menú completo — ninguna ruta necesita a las demás.

### Cualquier agente de programación — una línea (npx)

[vercel-labs/skills](https://github.com/vercel-labs/skills) detecta los
agentes instalados (Claude Code, Codex, OpenCode, Cursor y ~70 más) e
instala la carpeta completa de la skill para cada uno:

```bash
npx skills add MJL-ren/blindspot-audit
```

La telemetría anónima de instalación se desactiva con `DISABLE_TELEMETRY=1`.

### Deja que tu agente lo instale

Copia este prompt en Codex, Claude Code, OpenCode u otro agente de programación. El agente leerá este repositorio e instalará
la skill para el host o proyecto actual.

```text
Install and configure Blindspot Audit for this agent environment:
https://github.com/MJL-ren/blindspot-audit

Read the repository README.md and AGENTS.md first, then install using the documented skill route that fits this host and scope: the installer script, the Claude desktop .skill, or a safe manual copy. If a permission or safety guard blocks writing the skill into the agent's config directory, don't silently stop - ask me to approve the permission, or offer the plugin marketplace route as a managed fallback.

Do not modify unrelated project files. After installation, tell me which route you used, the installed path or plugin name, how to update it later, and the exact prompt I can use to run a deep blindspot audit.
```

### Claude Code — marketplace de plugins (una línea, con actualizaciones)

Dentro de Claude Code ejecuta:

```text
/plugin marketplace add MJL-ren/blindspot-audit
/plugin install blindspot-audit@blindspot-audit
```

No hace falta clonar el repositorio, y recibes actualizaciones con `/plugin marketplace update blindspot-audit`.
(`blindspot-audit@blindspot-audit` se lee como `<plugin>@<marketplace>` —
aquí ambos comparten nombre por casualidad; no es una errata.)

### Codex — marketplace de plugins

Dentro de Codex, añade el Git marketplace e instala el plugin:

```bash
codex plugin marketplace add MJL-ren/blindspot-audit --ref main
codex plugin add blindspot-audit@blindspot-audit
```

En la app de escritorio de ChatGPT, abre `Codex > Plugins > Installed` para
revisar o gestionar el plugin instalado. Si usas la CLI o quieres forzar la
actualización del marketplace, ejecuta:

```bash
codex plugin marketplace upgrade blindspot-audit
codex plugin add blindspot-audit@blindspot-audit
```

Después de instalar o actualizar, abre una nueva tarea de Codex para que se carguen las skills del plugin.

### Instalación con scripts (requiere clonar)

Las rutas de script de abajo necesitan un clon local. Todos los instaladores
tienen versiones PowerShell (`.ps1`) y Bash (`.sh`). En macOS/Linux usa los
scripts `.sh` (puede que necesites ejecutar `chmod +x scripts/*.sh` una vez).
En Windows usa `.ps1` desde PowerShell, o `.sh` desde Git Bash / WSL.

```bash
git clone https://github.com/MJL-ren/blindspot-audit.git
cd blindspot-audit
```

### Claude Code — instalación personal (recomendada; también cubre OpenCode)

Instala en `~/.claude/skills`, una ruta que leen Claude Code y OpenCode. Una instalación sirve para ambos hosts.

```powershell
.\scripts\install-claude-user.ps1
```

```bash
./scripts/install-claude-user.sh
```

### Claude Code — un solo proyecto

Instala en `<project>/.claude/skills`, que OpenCode también lee dentro de ese proyecto.

```powershell
.\scripts\install-claude-project.ps1 -ProjectRoot "C:\path\to\your-project"
```

```bash
./scripts/install-claude-project.sh /path/to/your-project
```

### Codex — instalación manual de la skill

Instala en el directorio actual de skills personales de Codex,
`~/.agents/skills`. También puedes pasar una ruta personalizada como
argumento. Si encuentra una copia con el mismo nombre en las rutas antiguas
`~/.codex/skills` o `$CODEX_HOME/skills`, avisa pero no la elimina.

```powershell
.\scripts\install-codex.ps1
```

```bash
./scripts/install-codex.sh
```

### App de escritorio de Claude / Cowork

Descarga el paquete más reciente directamente —
[blindspot-audit.skill](https://github.com/MJL-ren/blindspot-audit/releases/latest/download/blindspot-audit.skill)
(o usa `dist/blindspot-audit.skill` desde un clon) — ábrelo en la app de
escritorio de Claude, adjúntalo en el chat y pulsa **Save skill**.
No hace falta usar terminal; es la ruta más fácil para personas no desarrolladoras.

Si en cambio lo instalaste como **plugin** del marketplace dentro de la app de escritorio, reiniciar la app no basta para actualizarlo.
Pulsa **Update** en la pantalla de gestión de plugins, o ejecuta `/plugin marketplace update blindspot-audit` desde Claude Code
u otra CLI de plugins compatible.

### Instalación manual

Copia la carpeta `skills/blindspot-audit` en cualquiera de estas ubicaciones:

```text
~/.claude/skills/blindspot-audit                    # Claude Code personal + OpenCode
<project>/.claude/skills/blindspot-audit            # Claude Code de proyecto + OpenCode
~/.agents/skills/blindspot-audit                    # Codex personal
<project>/.agents/skills/blindspot-audit            # Codex de proyecto
<project>/.opencode/skills/blindspot-audit          # OpenCode nativo (proyecto)
~/.config/opencode/skills/blindspot-audit           # OpenCode nativo (global)
```

La documentación actual de Codex usa `.agents/skills`. Algunas instalaciones
pueden seguir mostrando copias antiguas en `~/.codex/skills` o
`$CODEX_HOME/skills`, pero mantener la misma skill en ambas ubicaciones puede
crear entradas duplicadas.

Luego abre una nueva sesión del agente, o refresca la actual, para que cargue la skill.

## Actualización

Actualiza usando la misma ruta con la que instalaste:

- Marketplace de plugins de Claude Code: ejecuta `/plugin marketplace update
  blindspot-audit` y abre una nueva sesión de Claude Code.
- Marketplace de plugins de Codex en la app de escritorio de ChatGPT: abre
  `Codex > Plugins > Installed` para revisar o gestionar el plugin. Para
  forzar una actualización por CLI, ejecuta `codex plugin marketplace upgrade
  blindspot-audit`, luego `codex plugin add blindspot-audit@blindspot-audit`,
  y abre una nueva tarea de Codex.
- Plugin del marketplace en la app de escritorio de Claude: pulsa **Update**
  en la pantalla de gestión de plugins; reiniciar la app no lo actualiza. La
  ruta CLI compatible es `/plugin marketplace update blindspot-audit`.
- Instalaciones con script: actualiza el repo con `git pull` y vuelve a ejecutar
  el mismo instalador que usaste. Los scripts reemplazan la carpeta instalada
  `blindspot-audit` en vez de mezclar archivos, así que los archivos renombrados
  o eliminados no quedan vivos.
- App de escritorio de Claude `.skill`: consigue el último
  `dist/blindspot-audit.skill` y guárdalo otra vez en la app.
- Instalaciones manuales: reemplaza toda la carpeta `skills/blindspot-audit`.
  No copies solo `SKILL.md`; esta skill también necesita `references/`,
  `scripts/` y `templates/`.

```bash
git pull
./scripts/install-claude-user.sh      # o el instalador que usaste antes
```

```powershell
git pull
.\scripts\install-claude-user.ps1     # o el instalador que usaste antes
```

## Uso

En Claude Code y OpenCode basta con pedirlo de forma natural. La skill se activa por su descripción:

```text
Run a blindspot audit on this project. What am I missing that I don't even know to ask about?
```

En Codex es más fiable mencionar la skill de forma explícita:

```text
Use $blindspot-audit in deep mode on this project. Create or update the BLINDSPOT_LEDGER.md and give me only the highest-signal findings.
```

Hay más ejemplos en [examples/prompts.md](./examples/prompts.md).

![BLINDSPOT_LEDGER y auditorías repetidas](./docs/assets/readme/en/ledger-diff.png)

## Mantenimiento

Después de cambiar `skills/blindspot-audit`, reconstruye el paquete para la app de escritorio de Claude:

```powershell
.\scripts\build-skill-package.ps1
```

```bash
./scripts/build-skill-package.sh
```

Después sincroniza y verifica la copia del plugin de Codex:

```powershell
.\scripts\sync-codex-plugin.ps1
python .\scripts\verify-codex-plugin.py
```

```bash
./scripts/sync-codex-plugin.sh
python3 scripts/verify-codex-plugin.py
```

## Cómo se adapta a cada host

- Hosts con preguntas de selección (Claude Code, OpenCode): hacen una pregunta corta solo cuando la respuesta cambia el trabajo,
  y una pregunta de selección múltiple para confirmar qué hallazgos la persona dueña ya conocía.
- Codex / hosts solo de chat: no se bloquean esperando preguntas. Continúan con una suposición segura y reversible, y dejan un
  `Decision packet` para responder después.
- Host sin acceso web: omite el escaneo de mirada fresca y lo dice claramente, en vez de afirmar conocimiento viejo sobre regulación o plataformas.
- Host con escritura de archivos: crea o actualiza `BLINDSPOT_LEDGER.md` por defecto.
- Host de solo lectura: devuelve un reporte portable con entradas propuestas para el ledger.

## Contribuir

Los reportes de bugs y las notas de ejecuciones reales son bienvenidos —
usa el [formulario de issues](https://github.com/MJL-ren/blindspot-audit/issues/new/choose),
que pide el host, la versión de la skill y el modo desde el principio. Los
PR de nuevas skills, paquetes o funciones grandes en general no se aceptan:
el núcleo de la auditoría se mantiene pequeño y validado en campo. Si crees
que falta algo, abre primero un issue.

## Atribución

Este proyecto se inspiró en el flujo de unknown unknowns descrito en
[A Field Guide to Fable: Finding Your Unknowns](https://x.com/trq212/status/2073100352921215386)
por Thariq (@trq212), del equipo de Claude Code. La implementación, el texto, las plantillas y los scripts de este repositorio
son trabajo original.

La estructura de sondas del paquete de enfoque `ux-ui` se informó con estos proyectos de código abierto,
consultados como clones locales de solo referencia en `external_repos/` (sin seguimiento de git);
todo el texto del paquete es original:

- [mistyhx/frontend-design-audit](https://github.com/mistyhx/frontend-design-audit)
  (MIT) - habilidad de auditoría frontend con 15 heurísticas de usabilidad, patrones de violación a nivel de código
  y un modelo de severidad.
- [raintree-technology/hig-doctor](https://github.com/raintree-technology/hig-doctor)
  (MIT para estructura/herramientas; el texto de las HIG es © Apple y no se copia) - taxonomía de categorías de detección
  para apariencia, accesibilidad y dispositivos.
- [Community-Access/accessibility-agents](https://github.com/Community-Access/accessibility-agents)
  (MIT) - patrones de agentes de auditoría de accesibilidad.

## Seguridad

Qué hacen los scripts, qué no toca la red y cómo reportar problemas de
forma privada: ver [SECURITY.md](./SECURITY.md).

## Licencia

MIT License. Consulta [LICENSE](./LICENSE).
