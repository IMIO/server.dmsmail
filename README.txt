This buildout relates the configuration of the application zope instance of the CommunesPlone central server.

The main config file is buildout.cfg.
Is is in development mode by default (dev.cfg).
It's necessary to call in it a subconfig file name: dev.cfg, prod.cfg, ...

The included external products are listed in cfg file:
    - section [productdistros] (release form)
    - section [svnproducts] (svn form)
    - subsection eggs

The directory 'parts/omelette' contains (as links) all the used products. 

Outside zeo mode (dev.cfg, base.cgf), a "zope_add.conf" extends the generated zope.conf to add mount_points definition. 
In zeo mode (prod.cfg), a "zope_add_zeo.conf" and "zeo_add.conf" extend the generated zope.conf and zeo.conf to add mount_points definition. 

The install process is described in the file : INSTALL.txt

Upgrade steps
-------------

Each imio.dms.mail version has its migration module in imio/dms/mail/migrations/migrate_to_X_Y_Z.py (based on imio.migrator),
registered as an upgrade step of the imio.dms.mail:default profile in migrations/upgrades.zcml.

The 3.0 -> 3.1 migration (migrate_to_3_1.py) is split into parts named by a letter and described in comments in the file
(e.g. x: clear solr, y: sync solr). Two environment variables drive it:
    - FUNC_PART: the part to run
    - BATCH: the maximum number of items handled in one run. A batched part resumes where it stopped, thanks to a .pkl file.

Upgrade steps are run with imio.updates (https://github.com/IMIO/imio.updates), which sets these variables:
    - -f upgrade imio.dms.mail:default [destination]: runs the upgrade steps
    - -v FUNC_PARTS=<letters>: runs the given parts one after another
    - -v BATCH=<n> and -v BATCH_TOTALS=<part>:<total>: split the parts into batches
    - -d: applies the changes (nothing is applied without it)

Example, syncing solr in batches of 5000 items:
    bin/update_instances -p <buildout> -i instance1 -f upgrade imio.dms.mail:default 3.1 -v FUNC_PARTS=y -v BATCH_TOTALS=y:<total> -v BATCH=5000 -d
