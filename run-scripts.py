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
        ret = obj.portal_setup.runImportStepFromProfile(profile, step)

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
    mig.upgradeProfile(profile)
    verbose('Running "%s" upgrade on %s' % (profile, obj.absolute_url_path()))
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
