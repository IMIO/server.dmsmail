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

## Key Packages

- **imio.dms.mail** (`src/imio.dms.mail/`): Core DMS mail application. This is where most development happens.
- **imio.transmogrifier.iadocs**: used to operate data retrieval. Read `docs/imio.transmogrifier.iadocs.md` when working on this package.

## Important Directories

- `parts/omelette/`: Symlink forest of all installed packages.
  When searching code, it must be done exclusively here. You can search there at any directory level without confirmation.

## Conventions

- imio.dms.mail: skip translation/locale updates (`i18ndude` regeneration is run separately). Other packages: update `.po`/`.pot` with the change, through the package's `update.sh`; in collective.documentgenerator edit them by hand, because its `update.sh` corrupts `setuphandlers.py`
