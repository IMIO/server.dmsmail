#!/usr/bin/make
#
# plone-path is added when "vhost_path: mount/site" is defined in puppet
plone=$(shell grep plone-path port.cfg|cut -c 14-)
hostname=$(shell hostname)
instance1_port=$(shell grep instance1-http port.cfg|cut -c 18-)
disable=1
copydata=1
instance=instance-debug
profile=imio.dms.mail:singles

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
	if ! test -f bin/soffice.sh;then cd bin; ln -s ../src/collective.documentgenerator/bin/soffice.sh soffice.sh;fi

.PHONY: upgrade
upgrade:
	@if ! test -f bin/instance1;then make buildout;fi
	@echo "plone: $(plone)"
	@echo "host: $(hostname)"
	@echo "port: $(instance1_port)"
	@echo "disable: $(disable)"
	@# copy-data is generated by puppet when data_source is found
	if [ $(copydata) = 1 ]; then (if [ $(disable) = 1 ]; then ./copy-data.sh --disable-auth=1; else ./copy-data.sh; fi); fi
#	./bin/upgrade-portals --username admin -A -G profile-imio.dms.mail:default $(plone)
	./bin/upgrade-portals --username admin -A $(plone)
	@$ echo "Upgrade done for instance $(plone), check http://$(hostname):$(instance1_port)/manage_main" | mail -s "Make upgrade finished for $(plone)" stephan.geulette@imio.be

.PHONY: standard-config
standard-config:
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout -vt 5 -c standard-config.cfg

.PHONY: run
run:
	if ! test -f bin/instance1;then make buildout;fi
	bin/instance1 fg

.PHONY: step-script
step-script:
# create templates: step=imiodmsmail-create-templates
# update templates: step=imiodmsmail-update-templates
# override templates: step=imiodmsmail-override-templates
# all steps: profile=collective.iconifieddocumentactions:default step=_all_
	@echo "plone: $(plone)"
	@echo "profile: $(profile)"
	@echo "step: $(step)"
	bin/$(instance) -O$(plone) run run-scripts.py 1 $(profile) $(step)

.PHONY: migrate-script
migrate-script:
# profile=collective.documentgenerator:default
# all profiles: profile=_all_
	@echo "plone: $(plone)"
	@echo "profile: $(profile)"
	bin/$(instance) -O$(plone) run run-scripts.py 2 $(profile)

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

.PHONY: robot-server
robot-server:
	bin/robot-server -v imio.dms.mail.testing.DMSMAIL_ROBOT_TESTING

.PHONY: doc
doc:
	# can be run by example with: make doc opt='-t "Contacts *"'
	bin/robot $(opt) src/imio.dms.mail/imio/dms/mail/tests/robot/doc.robot

.PHONY: coverage
coverage:
	bin/coverage
	bin/coverageme

.PHONY: cleanall
cleanall:
	rm -fr lib bin/buildout develop-eggs downloads eggs parts .installed.cfg
