#!/usr/bin/make
#
# plone-path is added when "vhost_path: mount/site" is defined in puppet
plone=$(shell grep plone-path port.cfg|cut -c 14-)
hostname=$(shell hostname)
instance1_port=$(shell grep instance1-http port.cfg|cut -c 18-)
copydata=1
instance=instance-debug
profile=imio.dms.mail:singles
commit=0

all: run

.PHONY: bootstrap
bootstrap:
	virtualenv-2.7 .
	./bin/python bootstrap.py

.PHONY: setup
setup:
	virtualenv-2.7 .
	./bin/pip install --upgrade pip
	./bin/pip install -r requirements.txt

.PHONY: buildout
buildout:
	if ! test -f bin/buildout;then make setup;fi
	if ! test -f var/filestorage/Data.fs;then make standard-config; else bin/buildout -v;fi
	git checkout .gitignore

.PHONY: copy
copy:
	@# copy-data is generated by puppet when data_source is found
	if [ $(copydata) = 1 ] && [ -f copy-data.sh ]; then ./copy-data.sh; fi
	@$ echo "copy-data finished for instance $(plone), check http://$(hostname):$(instance1_port)/manage_main" | mail -s "copy-data finished" stephan.geulette@imio.be

.PHONY: upgrade
upgrade:
	@if ! test -f bin/instance1;then make buildout;fi
	@echo "plone: $(plone)"
	./bin/$(instance) -O$(plone) run bin/run-portal-upgrades --username admin -A $(plone)
	@#./bin/upgrade-portals --username admin -A $(plone)  this script is not working anymore
	@#./bin/upgrade-portals --username admin -A -G profile-imio.dms.mail:default $(plone)

.PHONY: standard-config
standard-config:
	if ! test -f bin/buildout;then make setup;fi
	bin/buildout -vt 5 -c standard-config.cfg
	git checkout .gitignore

.PHONY: run
run:
	if ! test -f bin/instance1;then make buildout;fi
	bin/instance1 fg

.PHONY: ports
ports:
	@echo "plone: $(plone)"
	bin/$(instance) -O$(plone) run run-scripts.py 1

.PHONY: dv_clean
dv_clean:
# Clean old document viewer images
	@echo "plone: $(plone)"
	bin/$(instance) -O$(plone) run run-scripts.py 2

.PHONY: test-message-script
test-message-script:
# Activate test site message
	@echo "plone: $(plone)"
	bin/$(instance) -O$(plone) run run-scripts.py 3

.PHONY: various-script
various-script:
# Run various script
	@echo "plone: $(plone)"
	bin/$(instance) -O$(plone) run run-scripts.py 4

.PHONY: pipeline
pipeline:
	@echo "plone: $(plone)"
	@echo "commit: $(commit)"
	if ! test -f pipeline-run.cfg; then mv pipeline.cfg pipeline-run.cfg; fi
	bin/$(instance) run parts/omelette/collective/contact/importexport/scripts/execute_pipeline.py pipeline-run.cfg $(plone) $(commit)

.PHONY: robot-server
robot-server:
	env ZSERVER_HOST=localhost ZSERVER_PORT=55001 bin/robot-server -v imio.dms.mail.testing.DMSMAIL_ROBOT_TESTING

.PHONY: doc
doc:
	# can be run by example with: make doc opt='-t "Contacts *"'
	env ZSERVER_HOST=localhost ZSERVER_PORT=55001 bin/robot -l NONE -r NONE $(opt) src/imio.dms.mail/imio/dms/mail/tests/robot/doc.robot
	rm geckodriver*.log

.PHONY: coverage
coverage:
	bin/coverage
	bin/coverageme

.PHONY: cleanall
cleanall:
	rm -fr bin include lib local share develop-eggs downloads eggs parts .installed.cfg
	git checkout bin

.PHONY: vc
vc:
	bin/versioncheck -rbo checkversion.html
