# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **server.dmsmail**, a Plone 4.3-based Document Management System (DMS) built by IMIO for managing documents and email workflows. It runs on **Python 2.7** exclusively.

The build system is **zc.buildout** with **mr.developer** for managing 70+ source packages checked out under `src/`.

## Build & Development Commands

```bash
make setup              # Create Python 2.7 virtualenv and install requirements
make buildout           # Run buildout (creates standard site on first run)
bin/instance1 fg        # Start instance1 in foreground (port 8081)
```

## Testing

```bash
bin/testme                          # Run imio.dms.mail tests (primary test target)
bin/test -s <package.name>          # Run tests for a specific package
bin/test -s imio.dms.mail -t test_name  # Run a single test
```

### Robot / GUI Tests

```bash
make robot-server                   # Start robot test server on port 55001
make doc opt='-i "RUN1"'           # Run doc.robot tests (can filter by tag/name)
make gui-test opt='-t "* response"' # Run dmsmail.robot GUI tests
```

### Linting

Flake8 config: max-line-length=120, ignores E122/E126/E121/E226/E203/E704/W503/W504.

## Architecture

### Buildout Configuration Chain

`buildout.cfg` → `buildout-main.cfg` → extends `base.cfg` + `port.cfg` + `amqp.cfg` + `dev.cfg` + `test.cfg`

- **base.cfg**: Core Zope instance definition, ZCML loading, eggs
- **port.cfg**: All port assignments (instance1=8081, debug=8089, ZEO=8080, LibreOffice=2002, Solr=8983)
- **dev.cfg**: Auto-checkout of all source packages, debug mode, extends `sources-dev.cfg`
- **test.cfg**: Test runners (test, testme, coverage, coverageme, robot)
- **versions-base.cfg** / **versions-dev.cfg**: Pinned package versions

### Key Packages

- **imio.dms.mail** (`src/imio.dms.mail/`): Core DMS mail application — content types, workflows, views, event subscribers. This is where most development happens.
- **imio.dms.policy** (`src/imio.dms.policy/`): Policy/integration layer, ZCML entry point
- **collective.dms.mailcontent**: Mail content type definitions
- **collective.dms.basecontent**: Base DMS content types
- **collective.contact.\***: Contact management subsystem
- **collective.eeafaceted.\***: Faceted navigation/dashboard/batch actions
- **collective.documentgenerator**: Document generation via LibreOffice/appy
- **imio.zamqp.\***: AMQP async processing (RabbitMQ)
- **imio.esign**: E-signature support

### External Services

- **LibreOffice** on port 2002 (document conversion/generation)
- **Solr** on port 8983 (optional search engine)
- **ZEO** on port 8080 (shared ZODB server, optional for dev)
- **Keycloak** for SSO/OIDC authentication
- **RabbitMQ** for AMQP async tasks

### Important Directories

- `src/`: All 70+ source packages managed by mr.developer
- `Extensions/`: Zope external methods (demo.py, corrections.py, imports.py)
- `parts/omelette/`: Symlink forest of all installed packages (useful for navigation)
- `var/filestorage/Data.fs`: ZODB database file
- `var/blobstorage/`: Binary blob storage

### Conventions

- Namespace packages use `imio.*`, `imio.dms.*`, `collective.*` patterns
- Content types use Dexterity (not Archetypes)
- Site configuration via GenericSetup profiles in `profiles/` directories
- Event handling through `subscribers.py` and `setuphandlers.py`
- Data migration uses transmogrifier pipelines

## CI

GitHub Actions (`.github/workflows/main.yml`): runs `bin/testme` on Ubuntu 22.04 with Python 2.7.18 and Plone 4.3. Coverage published to Coveralls (skipped on branch 3.1.X).
