import os
import sys
from imio.pyutils.system import verbose, error
import transaction
from plone import api

# Parameters check
if len(sys.argv) < 3 or not sys.argv[2].endswith('run-scripts.py'):
    error("Inconsistent or unexpected args len: %s" % sys.argv)
    sys.exit(0)


def script1():
    portal = obj  # noqa
    verbose('Updating ports on %s' % portal.absolute_url_path())
    from collective.documentgenerator.utils import update_oo_config
    from imio.dms.mail.utils import update_solr_config
    update_solr_config()
    update_oo_config()
    transaction.commit()


def script2():
    if len(sys.argv) < 5:
        error("Missing profile name in args")
        sys.exit(0)
    profile = sys.argv[4]
    from imio.migrator.migrator import Migrator
    # obj is plone site
    mig = Migrator(obj)
    if profile == '_all_':
        verbose('Running all upgrades on %s' % (obj.absolute_url_path()))
        mig.upgradeAll(omit=['imio.dms.mail:default'])
    else:
        verbose('Running "%s" upgrade on %s' % (profile, obj.absolute_url_path()))
        mig.upgradeProfile(profile)
    transaction.commit()


def script3():
    portal = obj  # noqa
    verbose('Activating test site message on %s' % portal.absolute_url_path())
    testmsg = portal.unrestrictedTraverse('messages-config/test-site', default=None)
    if testmsg:
        if api.content.get_state(testmsg) == 'inactive':
            api.content.transition(testmsg, transition='activate')
            transaction.commit()
            verbose("Test site message activated")
        else:
            verbose("WARN: Test site message already activated")
    else:
        error("No test site message found")


def script4():
    portal = obj  # noqa
    verbose('Correcting ftw.labels permissions on %s' % portal.absolute_url_path())
    frontpage = portal['front-page']
    if frontpage.Title() == 'Gestion du courrier 3.0':
        frontpage.setTitle('Gestion du courrier 2.1')
    portal.manage_permission('ftw.labels: Manage Labels Jar', ('Manager', 'Site Administrator'), acquire=0)
    portal.manage_permission('ftw.labels: Change Labels', ('Manager', 'Site Administrator'), acquire=0)
    portal.manage_permission('ftw.labels: Change Personal Labels', ('Manager', 'Site Administrator', 'Member'),
                             acquire=0)

    transaction.commit()


info = ["You can pass following parameters (with the first one always script number):", "1: run ports update",
        "2: run profile upgrade", "3: activate test message", "4: various"]
scripts = {'1': script1, '2': script2, '3': script3, '4': script4}

if len(sys.argv) < 4 or sys.argv[3] not in scripts:
    error("Bad script parameter")
    verbose('\n>> =>'.join(info))
    sys.exit(0)

with api.env.adopt_user(username='admin'):
    scripts[sys.argv[3]]()

# ## OLD scripts ## #


def script4_1():
    portal = obj  # noqa
    verbose('Setting documentgenerator config on %s' % portal.absolute_url_path())
    from collective.documentgenerator.config import set_oo_port, set_uno_path
    set_oo_port()
    set_uno_path()
    transaction.commit()


def script4_2():
    portal = obj  # noqa
    verbose('Change searched types on %s' % portal.absolute_url_path())
    from imio.dms.mail.setuphandlers import changeSearchedTypes
    changeSearchedTypes(portal)
    transaction.commit()


def script4_3():
    portal = obj  # noqa
    verbose('Add transforms on %s' % portal.absolute_url_path())
    from imio.dms.mail.setuphandlers import add_transforms
    add_transforms(portal)
    for brain in portal.portal_catalog(portal_type='dmsommainfile'):
        brain.getObject().reindexObject(idxs=['SearchableText'])
    transaction.commit()


def script4_4():
    portal = obj  # noqa
    verbose('Correct templates odt_file contentType on %s' % portal.absolute_url_path())
    from collective.documentgenerator.content.pod_template import POD_TEMPLATE_TYPES
    import hmac
    from hashlib import sha1 as sha
    from zope.component import getUtility
    from plone.keyring.interfaces import IKeyManager
    manager = getUtility(IKeyManager)
    ring = manager[u"_system"]
    template_types = POD_TEMPLATE_TYPES.keys() + ['DashboardPODTemplate']
    changes = False
    for brain in portal.portal_catalog(portal_type=template_types):
        tmpl = brain.getObject()
        if tmpl.odt_file.contentType == 'applications/odt':
            error("%s has bad content type" % brain.getPath())
            changes = True
            tmpl.odt_file.contentType = 'application/vnd.oasis.opendocument.text'
            tmpl.setLayout('documentviewer')
            view = tmpl.unrestrictedTraverse('@@convert-to-documentviewer')
            view.request.form['form.action.queue'] = 1
            view.request.form['_authenticator'] = hmac.new(ring[0], 'admin', sha).hexdigest()
            view()
            if tmpl.wl_isLocked():
                error("Delocking")
                tmpl.wl_clearLocks()
    if changes:
        transaction.commit()


def script4_5():
    portal = obj  # noqa
    verbose('Set imio.dms.mail parameter on %s' % portal.absolute_url_path())
    from imio.migrator.migrator import Migrator
    mig = Migrator(portal)
    mig.runProfileSteps('imio.dms.mail', steps=['plone.app.registry'])
    mig.upgradeProfile('collective.iconifieddocumentactions:default')
    from imio.dms.mail.browser.settings import IImioDmsMailConfig
    from imio.dms.mail.setuphandlers import _
    api.portal.set_registry_record(name='omail_response_prefix', value=_(u'Response: '),
                                   interface=IImioDmsMailConfig)
    transaction.commit()


def script4_6():
    portal = obj  # noqa
    verbose('Set imio.dms.mail models on %s' % portal.absolute_url_path())
    from plone import api
    from zope.lifecycleevent import modified
    dprint = portal.templates.get('d-print', None)
    if dprint:
        verbose("Moving d-print")
        api.content.move(source=dprint, target=portal.templates.om)
        dprint = portal.templates.om['d-print']
        portal.templates.om.moveObjectToPosition('d-print', 1)
        if not dprint.style_template:
            verbose("Changing style template")
            dprint.style_template = portal.templates.om.style.UID()
            modified(dprint)
        transaction.commit()


def script4_7():
    portal = obj  # noqa
    verbose('Change imio.dms.mail settings on %s' % portal.absolute_url_path())
    from plone import api
    api.portal.set_registry_record('collective.documentgenerator.browser.controlpanel.'
                                   'IDocumentGeneratorControlPanelSchema.raiseOnError_for_non_managers', True)
    template = portal.restrictedTraverse('templates/om/d-print')
    template.enabled = False
    transaction.commit()


def script4_8():
    portal = obj  # noqa
    verbose('Update templates on %s' % portal.absolute_url_path())
    # changing layout
    portal.templates.om.layout = 'dg-templates-listing'
    # defining style_template
    from collective.documentgenerator.content.pod_template import IPODTemplate
    from imio.dms.mail.interfaces import IOMTemplatesFolder
    from zope.interface import alsoProvides
    om_folder = portal.templates.om
    alsoProvides(om_folder, IOMTemplatesFolder)
    style_uid = om_folder.style.UID()
    brains = portal.portal_catalog.unrestrictedSearchResults(object_provides=IPODTemplate.__identifier__)
    for brain in brains:
        tmp = brain.getObject()
        if tmp.style_template is None:
            verbose("Putting style on %s" % tmp)
            tmp.style_template = [style_uid]
    transaction.commit()
    # defining rename_page_styles
    om_folder['d-print'].rename_page_styles = True


def script4_9():
    portal = obj  # noqa
    verbose('Modify d-print on %s' % portal.absolute_url_path())
    import pkg_resources
    from imio.helpers.content import create_NamedBlob
    from zope.lifecycleevent import modified
    dprint = portal.templates.om.get('d-print', None)
    if dprint.has_been_modified():
        error('Beware: d-print has been modified !')
    if not dprint.enabled:
        verbose("Enabling d-print")
        dprint.enabled = True
    dpath = pkg_resources.resource_filename('imio.dms.mail', 'profiles/default/templates')
    dprint.odt_file = create_NamedBlob(os.path.join(dpath, 'd-print.odt'))
    dprint.style_modification_md5 = dprint.current_md5
    modified(dprint)
    transaction.commit()


def script4_10():
    portal = obj  # noqa
    from datetime import date, datetime, time
    verbose('Replace outgoing date, reindex organization_type, change sort key on %s' % portal.absolute_url_path())
    default_time = time(10, 0)
    for brain in portal.portal_catalog(portal_type='dmsoutgoingmail'):
        dom = brain.getObject()
        if dom.outgoing_date:
            dt = dom.outgoing_date
            if isinstance(dt, date):
                dom.outgoing_date = datetime.combine(dt, default_time)
        dom.reindexObject()
    for brain in portal.portal_catalog(portal_type='dmsincomingmail'):
        brain.getObject().reindexObject(idxs=['organization_type'])
    from imio.dms.mail.utils import list_wf_states
    collections = ['outgoing-mail/mail-searches/searchfor_scanned']
    for stateo in list_wf_states('', 'dmsincomingmail'):
        collections.append("incoming-mail/mail-searches/searchfor_%s" % stateo.id)
    for path in collections:
        col = portal.restrictedTraverse(path)
        col.sort_on = 'organization_type'
    transaction.commit()


def script4_11():
    portal = obj  # noqa
    verbose('Changing order on all incoming mail collections on %s' % portal.absolute_url_path())
    folder = portal['incoming-mail']['mail-searches']
    crit = {'portal_type': 'DashboardCollection',
            'path': {'query': '/'.join(folder.getPhysicalPath()), 'depth': 1}}
    brains = portal.portal_catalog.searchResults(crit)
    for brain in brains:
        brain.getObject().sort_on = 'organization_type'
    transaction.commit()


def script4_12():
    portal = obj  # noqa
    verbose('Activate versioning, change CMFEditions permissions on %s' % portal.absolute_url_path())
    # versioning
    pdiff = portal.portal_diff
    pdiff.setDiffForPortalType('dmsoutgoingmail', {'any': "Compound Diff for Dexterity types"})
    portal.portal_setup.runImportStepFromProfile('imio.dms.mail:default', 'repositorytool', run_dependencies=False)
    # cmfeditions permissions
    portal.manage_permission('CMFEditions: Access previous versions', ('Manager', 'Site Administrator', 'Contributor',
                             'Editor', 'Member', 'Owner', 'Reviewer'), acquire=0)
    portal.manage_permission('CMFEditions: Save new version', ('Manager', 'Site Administrator', 'Contributor',
                             'Editor', 'Member', 'Owner', 'Reviewer'), acquire=0)
    transaction.commit()


def script4_13():
    portal = obj  # noqa
    verbose('Correcting datetime values on %s' % portal.absolute_url_path())
    from plone import api
    from datetime import timedelta
    pc = portal.portal_catalog
    # incoming mails
    for typ, attr in (('dmsincomingmail', 'reception_date'), ('dmsoutgoingmail', 'outgoing_date')):
        total = corrected = 0
        for brain in pc(portal_type=typ):
            total += 1
            mail = brain.getObject()
            dt = getattr(mail, attr)
            if dt is not None and not dt.second:
                # verbose("Mail %s: %s" % (mail.absolute_url_path(), dt))
                fbrains = api.content.find(context=mail, portal_type=['dmsmainfile', 'dmsommainfile'],
                                           sort_on='created', sort_order='descending')
                scanned = None
                for fb in fbrains:
                    mfile = fb.getObject()
                    if mfile.scan_date:
                        scanned = mfile.scan_date
                        break
                if scanned and scanned.second:
                    corrected += 1
                    # verbose("NEW date %s" % (dt + timedelta(seconds=scanned.second)))
                    setattr(mail, attr, dt + timedelta(seconds=scanned.second))
                    mail.reindexObject(idxs=['organization_type'])
        verbose("Correcting '%s' type: total=%d, corrected=%d" % (typ, total, corrected))
    transaction.commit()


def script4_14():
    portal = obj  # noqa
    verbose('Changing personnel-folder interfaces on %s' % portal.absolute_url_path())
    from imio.dms.mail.interfaces import IPersonnelContact
    from collective.contact.plonegroup.interfaces import IPloneGroupContact
    from zope.interface import alsoProvides, noLongerProvides
    from imio.helpers.cache import invalidate_cachekey_volatile_for
    pc = portal.portal_catalog
    pf = portal['contacts']['personnel-folder']
    # personnel contacts
    for brain in pc(path={'query': '/'.join(pf.getPhysicalPath()), 'depth': 2}):
        contact = brain.getObject()
        if not IPersonnelContact.providedBy(contact):
            alsoProvides(contact, IPersonnelContact)
        if IPloneGroupContact.providedBy(contact):
            noLongerProvides(contact, IPloneGroupContact)
        contact.reindexObject(idxs=['object_provides'])
    invalidate_cachekey_volatile_for('imio.dms.mail.vocabularies.OMSenderVocabulary')
    transaction.commit()


def script4_15():
    portal = obj  # noqa
    verbose('Updating workflow on %s' % portal.absolute_url_path())
    # Updating workflow
    wf = portal.portal_workflow['outgoingmail_workflow']
    for tr_name in ['set_scanned', 'back_to_agent']:
        tr = wf.transitions.get(tr_name)
        guard = tr.getGuard()
        guard.permissions = ()
        guard.roles = ('Batch importer',)
    # Updating registry
    portal.portal_setup.runImportStepFromProfile('imio.dms.mail:default', 'plone.app.registry', run_dependencies=False)
    portal.portal_setup.runImportStepFromProfile('imio.dms.mail:default', 'actions', run_dependencies=False)
    transaction.commit()


def script4_16():
    portal = obj  # noqa
    verbose('Updating base on %s' % portal.absolute_url_path())
    from plone import api
    # base model
    pc = portal.portal_catalog
    for brain in pc(id='base', portal_type='ConfigurablePODTemplate'):
        model = brain.getObject()
        api.content.rename(obj=model, new_id='main')
        model.odt_file.filename = u'om-main.odt'
    transaction.commit()


def script4_17():
    portal = obj  # noqa
    verbose('Updating dashboards interfaces on %s' % portal.absolute_url_path())
    from imio.dms.mail.interfaces import IIMDashboard
    from imio.dms.mail.interfaces import IIMDashboardBatchActions
    from imio.dms.mail.interfaces import IOMDashboard
    from imio.dms.mail.interfaces import IOMDashboardBatchActions
    from imio.dms.mail.interfaces import ITaskDashboard
    from imio.dms.mail.interfaces import ITaskDashboardBatchActions
    from zope.interface import alsoProvides
    from zope.interface import noLongerProvides
    imf = portal['incoming-mail']['mail-searches']
    noLongerProvides(imf, IIMDashboard)
    alsoProvides(imf, IIMDashboardBatchActions)
    omf = portal['outgoing-mail']['mail-searches']
    noLongerProvides(omf, IOMDashboard)
    alsoProvides(omf, IOMDashboardBatchActions)
    tf = portal['tasks']['task-searches']
    noLongerProvides(tf, ITaskDashboard)
    alsoProvides(tf, ITaskDashboardBatchActions)
    transaction.commit()


def script4_18():
    portal = obj  # noqa
    verbose('Adding mailing on %s' % portal.absolute_url_path())
    folder = portal['templates']['om']
    ml_uid = folder['mailing'].UID()
    brains = api.content.find(context=folder, portal_type=['ConfigurablePODTemplate'])
    for brain in brains:
        ob = brain.getObject()
        if not ob.mailing_loop_template:
            verbose('Adding mailing on {} ({})'.format(brain.getPath(), brain.Title))
            ob.mailing_loop_template = ml_uid
    transaction.commit()


def script4_19():
    portal = obj  # noqa
    verbose('Correcting ckeditor skin on %s' % portal.absolute_url_path())
    portal.portal_properties.ckeditor_properties.skin = 'moono-lisa'
    transaction.commit()


def script4_20():
    portal = obj  # noqa
    verbose('Setting imio.dms.mail configuration annotation on %s' % portal.absolute_url_path())
    from collections import OrderedDict
    from imio.dms.mail.utils import get_dms_config
    from imio.dms.mail.utils import set_dms_config
    try:
        get_dms_config()
        error('Already applied !')
        return
    except KeyError:
        pass
    set_dms_config(['review_levels', 'dmsincomingmail'],
                   OrderedDict([('dir_general', {'st': ['proposed_to_manager']}),
                                ('_validateur', {'st': ['proposed_to_service_chief'], 'org': 'treating_groups'})]))
    set_dms_config(['review_levels', 'task'],
                   OrderedDict([('_validateur', {'st': ['to_assign', 'realized'], 'org': 'assigned_group'})]))
    set_dms_config(['review_levels', 'dmsoutgoingmail'],
                   OrderedDict([('_validateur', {'st': ['proposed_to_service_chief'], 'org': 'treating_groups'})]))
    set_dms_config(['review_states', 'dmsincomingmail'],
                   OrderedDict([('proposed_to_manager', {'group': 'dir_general'}),
                                ('proposed_to_service_chief', {'group': '_validateur', 'org': 'treating_groups'})]))
    set_dms_config(['review_states', 'task'],
                   OrderedDict([('to_assign', {'group': '_validateur', 'org': 'assigned_group'}),
                                ('realized', {'group': '_validateur', 'org': 'assigned_group'})]))
    set_dms_config(['review_states', 'dmsoutgoingmail'],
                   OrderedDict([('proposed_to_service_chief', {'group': '_validateur', 'org': 'treating_groups'})]))
    transaction.commit()
