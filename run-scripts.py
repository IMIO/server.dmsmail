import os
import sys
from imio.pyutils.system import verbose, error
import transaction
from plone import api

# Parameters check
if len(sys.argv) < 3 or sys.argv[2] != 'run-scripts.py':
    error("Inconsistent or unexpected args len: %s" % sys.argv)
    sys.exit(0)


def script1():
    if len(sys.argv) < 6:
        error("Missing profile and step names in args")
        sys.exit(0)
    profile = sys.argv[4]
    step = sys.argv[5]
    if not profile.startswith('profile-'):
        profile = 'profile-%s' % profile
    if step == '_all_':
        verbose('Running all "%s" steps on %s' % (profile, obj.absolute_url_path()))
        ret = obj.portal_setup.runAllImportStepsFromProfile(profile)
    else:
        verbose('Running "%s#%s" step on %s' % (profile, step, obj.absolute_url_path()))
        ret = obj.portal_setup.runImportStepFromProfile(profile, step, run_dependencies=False)

    if 'messages' in ret:
        for step in ret['messages']:
            verbose("%s:\n%s" % (step, ret['messages'][step]))
    else:
        verbose("No output")
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
    verbose('Activating test site message on %s' % obj.absolute_url_path())
    testmsg = obj.unrestrictedTraverse('messages-config/test-site', default=None)
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
    verbose('Activate versioning, change CMFEditions permissions on %s' % obj.absolute_url_path())
    # versioning
    pdiff = obj.portal_diff
    pdiff.setDiffForPortalType('dmsoutgoingmail', {'any': "Compound Diff for Dexterity types"})
    obj.portal_setup.runImportStepFromProfile('imio.dms.mail:default', 'repositorytool', run_dependencies=False)
    # cmfeditions permissions
    obj.manage_permission('CMFEditions: Access previous versions', ('Manager', 'Site Administrator', 'Contributor',
                          'Editor', 'Member', 'Owner', 'Reviewer'), acquire=0)
    obj.manage_permission('CMFEditions: Save new version', ('Manager', 'Site Administrator', 'Contributor',
                          'Editor', 'Member', 'Owner', 'Reviewer'), acquire=0)
    transaction.commit()

info = ["You can pass following parameters (with the first one always script number):", "1: run profile step",
        "2: run profile upgrade", "3: activate test message", "4: various"]
scripts = {'1': script1, '2': script2, '3': script3, '4': script4}

if len(sys.argv) < 4 or sys.argv[3] not in scripts:
    error("Bad script parameter")
    verbose('\n>> =>'.join(info))
    sys.exit(0)

with api.env.adopt_user(username='admin'):
    scripts[sys.argv[3]]()

### OLD scripts ###


def script4_1():
    verbose('Setting documentgenerator config on %s' % obj.absolute_url_path())
    from collective.documentgenerator.config import set_oo_port, set_uno_path
    set_oo_port()
    set_uno_path()
    transaction.commit()


def script4_2():
    verbose('Change searched types on %s' % obj.absolute_url_path())
    from imio.dms.mail.setuphandlers import changeSearchedTypes
    changeSearchedTypes(obj)
    transaction.commit()


def script4_3():
    verbose('Add transforms on %s' % obj.absolute_url_path())
    from imio.dms.mail.setuphandlers import add_transforms
    add_transforms(obj)
    for brain in obj.portal_catalog(portal_type='dmsommainfile'):
        brain.getObject().reindexObject(idxs=['SearchableText'])
    transaction.commit()


def script4_4():
    verbose('Correct templates odt_file contentType on %s' % obj.absolute_url_path())
    from collective.documentgenerator.content.pod_template import POD_TEMPLATE_TYPES
    import hmac
    from hashlib import sha1 as sha
    from zope.component import getUtility
    from plone.keyring.interfaces import IKeyManager
    manager = getUtility(IKeyManager)
    ring = manager[u"_system"]
    template_types = POD_TEMPLATE_TYPES.keys() + ['DashboardPODTemplate']
    changes = False
    for brain in obj.portal_catalog(portal_type=template_types):
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
    verbose('Set imio.dms.mail parameter on %s' % obj.absolute_url_path())
    from imio.migrator.migrator import Migrator
    mig = Migrator(obj)
    mig.runProfileSteps('imio.dms.mail', steps=['plone.app.registry'])
    mig.upgradeProfile('collective.iconifieddocumentactions:default')
    from imio.dms.mail.browser.settings import IImioDmsMailConfig
    from imio.dms.mail.setuphandlers import _
    api.portal.set_registry_record(name='omail_response_prefix', value=_(u'Response: '),
                                   interface=IImioDmsMailConfig)
    transaction.commit()


def script4_6():
    verbose('Set imio.dms.mail models on %s' % obj.absolute_url_path())
    from plone import api
    from zope.lifecycleevent import modified
    dprint = obj.templates.get('d-print', None)
    if dprint:
        verbose("Moving d-print")
        api.content.move(source=dprint, target=obj.templates.om)
        dprint = obj.templates.om['d-print']
        obj.templates.om.moveObjectToPosition('d-print', 1)
        if not dprint.style_template:
            verbose("Changing style template")
            dprint.style_template = obj.templates.om.style.UID()
            modified(dprint)
        transaction.commit()


def script4_7():
    verbose('Change imio.dms.mail settings on %s' % obj.absolute_url_path())
    from plone import api
    api.portal.set_registry_record('collective.documentgenerator.browser.controlpanel.'
                                   'IDocumentGeneratorControlPanelSchema.raiseOnError_for_non_managers', True)
    template = obj.restrictedTraverse('templates/om/d-print')
    template.enabled = False
    transaction.commit()


def script4_8():
    verbose('Update templates on %s' % obj.absolute_url_path())
    # changing layout
    obj.templates.om.layout = 'dg-templates-listing'
    # defining style_template
    from collective.documentgenerator.content.pod_template import IPODTemplate
    from imio.dms.mail.interfaces import IOMTemplatesFolder
    from zope.interface import alsoProvides
    om_folder = obj.templates.om
    alsoProvides(om_folder, IOMTemplatesFolder)
    style_uid = om_folder.style.UID()
    brains = obj.portal_catalog.unrestrictedSearchResults(object_provides=IPODTemplate.__identifier__)
    for brain in brains:
        tmp = brain.getObject()
        if tmp.style_template is None:
            verbose("Putting style on %s" % tmp)
            tmp.style_template = [style_uid]
    transaction.commit()
    # defining rename_page_styles
    om_folder['d-print'].rename_page_styles = True


def script4_9():
    verbose('Modify d-print on %s' % obj.absolute_url_path())
    import pkg_resources
    from imio.helpers.content import create_NamedBlob
    from zope.lifecycleevent import modified
    dprint = obj.templates.om.get('d-print', None)
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
    from datetime import date, datetime, time
    verbose('Replace outgoing date, reindex organization_type, change sort key on %s' % obj.absolute_url_path())
    default_time = time(10, 0)
    for brain in obj.portal_catalog(portal_type='dmsoutgoingmail'):
        dom = brain.getObject()
        if dom.outgoing_date:
            dt = dom.outgoing_date
            if isinstance(dt, date):
                dom.outgoing_date = datetime.combine(dt, default_time)
        dom.reindexObject()
    for brain in obj.portal_catalog(portal_type='dmsincomingmail'):
        brain.getObject().reindexObject(idxs=['organization_type'])
    from imio.dms.mail.utils import list_wf_states
    collections = ['outgoing-mail/mail-searches/searchfor_scanned']
    for stateo in list_wf_states('', 'dmsincomingmail'):
        collections.append("incoming-mail/mail-searches/searchfor_%s" % stateo.id)
    for path in collections:
        col = obj.restrictedTraverse(path)
        col.sort_on = 'organization_type'
    transaction.commit()


def script4_11():
    verbose('Changing order on all incoming mail collections on %s' % obj.absolute_url_path())
    folder = obj['incoming-mail']['mail-searches']
    crit = {'portal_type': 'DashboardCollection',
            'path': {'query': '/'.join(folder.getPhysicalPath()), 'depth': 1}}
    brains = obj.portal_catalog.searchResults(crit)
    for brain in brains:
        brain.getObject().sort_on = 'organization_type'
    transaction.commit()
