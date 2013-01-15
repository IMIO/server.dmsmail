#!/usr/bin/make
#
all: run

.PHONY: bootstrap
bootstrap:
	virtualenv-2.7 --no-site-packages .
	./bin/python bootstrap.py

.PHONY: buildout
buildout:
	if ! test -f bin/buildout;then make bootstrap;fi
	if ! test -f var/filestorage/Data.fs;then make standard-config; else bin/buildout -v;fi

.PHONY: standard-config
standard-config:
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout -vt 5 -c standard-config.cfg

.PHONY: run
run:
	if ! test -f bin/instance1;then make buildout;fi
	bin/instance1 fg

.PHONY: cleanall
cleanall:
	rm -fr develop-eggs downloads eggs parts .installed.cfg
