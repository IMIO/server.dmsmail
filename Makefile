#!/usr/bin/make
#
all: run

.PHONY: bootstrap
bootstrap:
	virtualenv-2.7 --no-setuptools .
	bin/python ez_setup.py 
	./bin/python bootstrap.py -v 2.2.0

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

.PHONY: coverage
run:
	bin/coverage
	bin/coverageme

.PHONY: cleanall
cleanall:
	rm -fr lib bin/buildout develop-eggs downloads eggs parts .installed.cfg
