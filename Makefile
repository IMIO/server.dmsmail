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

help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: bootstrap
bootstrap:
	virtualenv-2.7 .
	./bin/python bootstrap.py

.PHONY: setup
setup:  ## Setups environment
	# if command -v python2 >/dev/null && command -v virtualenv; then virtualenv -p python2 . ; elif command -v virtualenv-2.7; then virtualenv-2.7 . ;fi
	if command -v virtualenv-2.7; then virtualenv-2.7 . ; elif command -v python2 >/dev/null && command -v virtualenv; then virtualenv -p python2 . ; fi
	./bin/pip install --upgrade pip
	./bin/pip install -r requirements.txt

.PHONY: buildout
buildout:  ## Runs setup and buildout
	rm -f .installed.cfg .mr.developer.cfg
	if ! test -f bin/buildout;then make setup;fi
	if ! test -f var/filestorage/Data.fs;then make standard-config; else bin/buildout -v;fi
	git checkout .gitignore

.PHONY: copy
copy: copy-data.sh  ## Runs `copy-data.sh`
	@# copy-data is generated by puppet when data_source is found
	if ! grep -q 30_config.dic copy-data.sh; then echo '\nrsync -e "ssh -o $StrictHostKeyChecking=no" -ah --info=stats1 "$${SOURCE_HOST}:$${SOURCE_PATH}/30_config.dic" $${TARGET_PATH}/ --delete' >> copy-data.sh ; fi
	if [ $(copydata) = 1 ]; then ./copy-data.sh; fi
	# if [ $(copydata) = 1 ] && [ -f bin/solr-start ]; then ./copy-solr.sh; fi
	@$ echo "copy-data finished for instance $(plone), check http://$(hostname):$(instance1_port)/manage_main" | mail -s "copy-data finished" stephan.geulette@imio.be

.PHONY: upgrade
upgrade:  ## Runs `run-portal-upgrades` plone script (plone upgrade only)
	@if ! test -f bin/instance1;then make buildout;fi
	@echo "plone: $(plone)"
	./bin/$(instance) -O$(plone) run bin/run-portal-upgrades --username admin -A $(plone)
	@#./bin/upgrade-portals --username admin -A $(plone)  this script is not working anymore
	@#./bin/upgrade-portals --username admin -A -G profile-imio.dms.mail:default $(plone)

.PHONY: standard-config
standard-config:  ## Creates a standard plone site
	if ! test -f bin/buildout;then make setup;fi
	bin/buildout -vt 5 -c standard-config.cfg
	git checkout .gitignore

.PHONY: run
run:  ## Runs `bin/instance1 fg`
	if ! test -f bin/instance1;then make buildout;fi
	bin/instance1 fg

.PHONY: ports
ports:  ## Updates libreoffice and solr ports
	@echo "plone: $(plone)"
	bin/$(instance) -O$(plone) run run-scripts.py 1

.PHONY: dv_clean
dv_clean:  ## Cleans old dv files
# Clean old document viewer images
	@echo "plone: $(plone)"
	bin/$(instance) -O$(plone) run run-scripts.py 2

.PHONY: solr-sync
solr-sync:  ## Solr synchronization (clear + sync)
	@echo "plone: $(plone)"
	bin/$(instance) -O$(plone) run run-scripts.py 3

.PHONY: various-script
various-script:  ## Runs `run-scripts.py` 4 plone script that does various things
# Run various script
	@echo "plone: $(plone)"
	bin/$(instance) -O$(plone) run run-scripts.py 4

.PHONY: cputils
cputils:  ## run cputils_install
	@echo "plone: $(plone)"
	bin/$(instance) -O$(plone) run standard-config.py

.PHONY: contact-import
contact-import:  ## Runs contact import `pipeline-run.cfg`
	@echo "plone: $(plone)"
	@echo "commit: $(commit)"
	if ! test -f pipeline-run.cfg; then mv pipeline.cfg pipeline-run.cfg; fi
	bin/$(instance) run parts/omelette/collective/contact/importexport/scripts/execute_pipeline.py pipeline-run.cfg $(plone) $(commit)

.PHONY: robot-server
robot-server:  ## Starts robot server
	env ZSERVER_HOST=localhost ZSERVER_PORT=55001 bin/robot-server -v imio.dms.mail.testing.DMSMAIL_ROBOT_TESTING

.PHONY: doc
doc:  ## Runs `doc.robot`
	# can be run by example with: make doc opt='-t "Contacts *"' or make doc opt='-i "RUN1"'  (or -e to exclude)
	# env ZSERVER_HOST=localhost ZSERVER_PORT=55001 bin/robot -l NONE -r NONE $(opt) src/imio.dms.mail/imio/dms/mail/tests/robot/doc.robot
	env ZSERVER_HOST=localhost ZSERVER_PORT=55001 bin/robot -r NONE $(opt) src/imio.dms.mail/imio/dms/mail/tests/robot/doc.robot
	rm geckodriver*.log

.PHONY: video-doc
video-doc:  ## Runs `video-doc.robot`
	# can be run by example with: make video-doc opt='-t "Contacts *"' or opt='-i "RUN1"'
	env ZSERVER_HOST=localhost ZSERVER_PORT=55001 bin/robot -r NONE $(opt) src/imio.dms.mail/imio/dms/mail/tests/robot/video-doc.robot
	rm geckodriver*.log

.PHONY: perf-test
perf-test:  ## Runs performance tests
	# can be run by example with: make perf-test opt='-t test_'
	bin/testme --test-file-pattern=ptest_ ${opt}

.PHONY: coverage
coverage:  ## Runs tests coverage
	bin/coverage
	bin/coverageme

.PHONY: cleanall
cleanall:  ## Cleans all installed buildout files
	rm -fr bin include lib local share develop-eggs downloads eggs parts .installed.cfg
	git checkout bin

.PHONY: vcr
vcr:  ## Shows requirements in checkversion-r.html
	# show requirements
	bin/versioncheck -rbo checkversion-r.html

.PHONY: vcn
vcn:  ## Shows newer packages in checkversion-n.html
	# show only newer
	bin/versioncheck -npbo checkversion-n.html

.PHONY: techdoc
techdoc:  ## Builds technical docs
	bin/sphinxbuilder

.PHONY: instance-patch
instance-patch:  ## Patches instance interpreter to run scripts (needed when front-page is not anonymously accessible)
	bin/python helper.py -f=patch_instance -i=$(instance)
