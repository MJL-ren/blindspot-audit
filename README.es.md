# Blindspot Audit

[English](./README.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [简体中文](./README.zh.md) | [Español](./README.es.md)

Blindspot Audit es una skill portátil para agentes de IA que ayuda a encontrar lo que la persona dueña de un proyecto
todavía no sabe que está pasando por alto: unknown unknowns, riesgos ocultos, decisiones pendientes, supuestos viejos
y preguntas que nadie pensó hacer. Deja el resultado en `BLINDSPOT_LEDGER.md`.

Funciona con cualquier tipo de proyecto: software, juegos, novelas y escritura creativa, investigación, contenido o planes
de negocio. Puede usarse en Claude Code, Codex, OpenCode, la app de escritorio de Claude y chats normales. El núcleo de la
auditoría es el mismo; cada host solo adapta cómo pregunta y cómo guarda los resultados.

## Instalación rápida con IA

Copia este prompt en Codex, Claude Code, OpenCode u otro agente de programación. El agente leerá este repositorio e instalará
la skill para el host o proyecto actual.

```text
Install and configure Blindspot Audit for this agent environment:
https://github.com/MJL-ren/blindspot-audit

Read the repository README.md and AGENTS.md first, then choose the documented install route that fits this host and install scope: marketplace/plugin, Claude desktop .skill, installer script, or safe manual copy.

Do not modify unrelated project files. After installation, tell me which route you used, the installed path or plugin name, how to update it later, and the exact prompt I can use to run a deep blindspot audit.
```

## Qué hace

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
- Mantiene un `BLINDSPOT_LEDGER.md` duradero. Las siguientes ejecuciones comparan contra ese archivo y reportan solo lo nuevo o cambiado.

No es una checklist genérica de calidad. La pregunta que responde es:

> Dado este proyecto específico, ¿qué es probable que todavía no estemos viendo?

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

Todos los instaladores tienen versiones PowerShell (`.ps1`) y Bash (`.sh`). En macOS/Linux usa los scripts `.sh`
(puede que necesites ejecutar `chmod +x scripts/*.sh` una vez). En Windows usa `.ps1` desde PowerShell, o `.sh`
desde Git Bash / WSL.

```bash
git clone https://github.com/MJL-ren/blindspot-audit.git
cd blindspot-audit
```

### Claude Code — marketplace de plugins (una línea, con actualizaciones)

Dentro de Claude Code ejecuta:

```text
/plugin marketplace add MJL-ren/blindspot-audit
/plugin install blindspot-audit@blindspot-audit
```

No hace falta clonar el repositorio, y recibes actualizaciones con `/plugin marketplace update blindspot-audit`.

### Codex — marketplace de plugins

Dentro de Codex, añade el Git marketplace e instala el plugin:

```bash
codex plugin marketplace add MJL-ren/blindspot-audit --ref main
codex plugin add blindspot-audit@blindspot-audit
```

Para actualizar más adelante:

```bash
codex plugin marketplace upgrade blindspot-audit
codex plugin add blindspot-audit@blindspot-audit
```

Después de instalar o actualizar, abre un nuevo hilo de Codex para que se carguen las skills del plugin.

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

Instala en `$CODEX_HOME/skills` si `CODEX_HOME` existe; si no, en `~/.codex/skills`.
También puedes pasar una ruta personalizada como argumento.

```powershell
.\scripts\install-codex.ps1
```

```bash
./scripts/install-codex.sh
```

### App de escritorio de Claude / Cowork

Abre `dist/blindspot-audit.skill` en la app de escritorio de Claude, adjúntalo en el chat y pulsa **Save skill**.
No hace falta usar terminal; es la ruta más fácil para personas no desarrolladoras.

Si en cambio lo instalaste como **plugin** del marketplace dentro de la app de escritorio, las actualizaciones no son automáticas
por defecto: ejecuta la comprobación de actualizaciones desde la pantalla de gestión de plugins, o conecta ahí tu cuenta de GitHub
para activar la sincronización automática con este repositorio.

### Instalación manual

Copia la carpeta `skills/blindspot-audit` en cualquiera de estas ubicaciones:

```text
~/.claude/skills/blindspot-audit                    # Claude Code personal + OpenCode
<project>/.claude/skills/blindspot-audit            # Claude Code de proyecto + OpenCode
~/.codex/skills/blindspot-audit                     # Codex
<project>/.opencode/skills/blindspot-audit          # OpenCode nativo (proyecto)
~/.config/opencode/skills/blindspot-audit           # OpenCode nativo (global)
```

Luego abre una nueva sesión del agente, o refresca la actual, para que cargue la skill.

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

## Atribución

Este proyecto se inspiró en el flujo de unknown unknowns descrito en
[A Field Guide to Fable: Finding Your Unknowns](https://x.com/trq212/status/2073100352921215386)
por Thariq (@trq212), del equipo de Claude Code. La implementación, el texto, las plantillas y los scripts de este repositorio
son trabajo original.

## Licencia

MIT License. Consulta [LICENSE](./LICENSE).
