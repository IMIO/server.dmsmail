# -*- coding: utf-8 -*-

from imio.dms.mail.utils import dv_clean
from imio.helpers.security import setup_logger
from imio.pyutils.system import error
from imio.pyutils.system import verbose
from plone import api

import os
import sys
import transaction


# Parameters check
if len(sys.argv) < 3 or not sys.argv[2].endswith('run-scripts.py'):
    error("Inconsistent or unexpected args len: %s" % sys.argv)
    sys.exit(0)

setup_logger()


def script1():
    portal = obj  # noqa
    verbose('Updating ports on %s' % portal.absolute_url_path())
    from collective.documentgenerator.utils import update_oo_config
    from imio.dms.mail.utils import update_solr_config
    update_solr_config()
    update_oo_config()
    transaction.commit()


def script2():
    portal = obj  # noqa
    params = {
        'days_back': api.portal.get_registry_record('imio.dms.mail.dv_clean_days', default=None),
        'date_back': api.portal.get_registry_record('imio.dms.mail.dv_clean_date', default=None)
    }
    for k, v in params.items():
        if not params[k]:
            del params[k]
    if not params:
        error('No preservation parameters configured')
        return
    verbose('Cleaning dv files with params {} on {}'.format(params, portal.absolute_url_path()))
    try:
        from datetime import datetime
        if params.get('date_back'):
            params['date_back'] = datetime.strftime(params['date_back'], '%Y%m%d')
    except Exception as msg:
        error("Bad date value '{}': '{}'".format(params['date_back'], msg))
        sys.exit(0)
    dv_clean(portal, **params)
    transaction.commit()


def script3():
    """Install solr, set ports, activating it"""
    portal = obj  # noqa
    qi = api.portal.get_tool('portal_quickinstaller')
    qi.installProduct('collective.solr', forceProfile=True)
    from imio.dms.mail.utils import update_solr_config
    update_solr_config()
    api.portal.set_registry_record('collective.solr.active', True)
    transaction.commit()


def script4():
    portal = obj  # noqa
    full_key = 'collective.solr.port'
    configured_port = api.portal.get_registry_record(full_key, default=None)
    if configured_port is None:
        return
    verbose('Syncing solr on %s' % portal.absolute_url_path())
    response = portal.REQUEST.RESPONSE
    original = response.write
    response.write = lambda x: x  # temporarily ignore output
    maintenance = portal.unrestrictedTraverse("@@solr-maintenance")
    if len(sys.argv) > 4 and sys.argv[4] == 'clear':
        maintenance.clear()
    maintenance.sync()
    response.write = original
    # transaction.commit()


def script5():
    portal = obj  # noqa
    verbose('Updating personnel-folder on %s' % portal.absolute_url_path())
    from imio.dms.mail.interfaces import IPersonnelFolder
    from zope.interface import alsoProvides
    pc = portal.portal_catalog
    pf = portal['contacts']['personnel-folder']
    alsoProvides(pf, IPersonnelFolder)
    pf.layout = 'personnel-listing'
    # personnel contacts
    for brain in pc(portal_type=['person'], path='/'.join(pf.getPhysicalPath())):
        api.content.transition(brain.getObject(), to_state='active')
    transaction.commit()


info = ["You can pass following parameters (with the first one always script number):", "1: run ports update",
        "2: clean old dv files", "3: solr install", "4: solr reindex", "5: update"]
scripts = {'1': script1, '2': script2, '3': script3, '4': script4, '5': script5}

if len(sys.argv) < 4 or sys.argv[3] not in scripts:
    error("Bad script parameter")
    verbose('\n>> =>'.join(info))
    sys.exit(0)

with api.env.adopt_user(username='admin'):
    scripts[sys.argv[3]]()

# ## OLD scripts ## #


def script4_1():
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


def script5_1():
    portal = obj  # noqa
    verbose('Setting documentgenerator config on %s' % portal.absolute_url_path())
    from collective.documentgenerator.config import set_oo_port
    from collective.documentgenerator.config import set_uno_path
    set_oo_port()
    set_uno_path()
    transaction.commit()


def script5_2():
    portal = obj  # noqa
    verbose('Change searched types on %s' % portal.absolute_url_path())
    from imio.dms.mail.setuphandlers import changeSearchedTypes
    changeSearchedTypes(portal)
    transaction.commit()


def script5_3():
    portal = obj  # noqa
    verbose('Add transforms on %s' % portal.absolute_url_path())
    from imio.dms.mail.setuphandlers import add_transforms
    add_transforms(portal)
    for brain in portal.portal_catalog(portal_type='dmsommainfile'):
        brain.getObject().reindexObject(idxs=['SearchableText'])
    transaction.commit()


def script5_4():
    portal = obj  # noqa
    verbose('Correct templates odt_file contentType on %s' % portal.absolute_url_path())
    from collective.documentgenerator.content.pod_template import POD_TEMPLATE_TYPES
    from hashlib import sha1 as sha
    from plone.keyring.interfaces import IKeyManager
    from zope.component import getUtility

    import hmac
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


def script5_5():
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


def script5_6():
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


def script5_7():
    portal = obj  # noqa
    verbose('Change imio.dms.mail settings on %s' % portal.absolute_url_path())
    from plone import api
    api.portal.set_registry_record('collective.documentgenerator.browser.controlpanel.'
                                   'IDocumentGeneratorControlPanelSchema.raiseOnError_for_non_managers', True)
    template = portal.restrictedTraverse('templates/om/d-print')
    template.enabled = False
    transaction.commit()


def script5_8():
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


def script5_9():
    portal = obj  # noqa
    verbose('Modify d-print on %s' % portal.absolute_url_path())
    from imio.helpers.content import create_NamedBlob
    from zope.lifecycleevent import modified

    import pkg_resources
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


def script5_10():
    portal = obj  # noqa
    from datetime import date
    from datetime import datetime
    from datetime import time
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


def script5_11():
    portal = obj  # noqa
    verbose('Changing order on all incoming mail collections on %s' % portal.absolute_url_path())
    folder = portal['incoming-mail']['mail-searches']
    crit = {'portal_type': 'DashboardCollection',
            'path': {'query': '/'.join(folder.getPhysicalPath()), 'depth': 1}}
    brains = portal.portal_catalog.searchResults(crit)
    for brain in brains:
        brain.getObject().sort_on = 'organization_type'
    transaction.commit()


def script5_12():
    portal = obj  # noqa
    verbose('Activate versioning, change CMFEditions permissions on %s' % portal.absolute_url_path())
    # versioning
    pdiff = portal.portal_diff
    pdiff.setDiffForPortalType('dmsoutgoingmail', {'any': "Compound Diff for Dexterity types"})
    portal.portal_setup.runImportStepFromProfile('profile-imio.dms.mail:default', 'repositorytool',
                                                 run_dependencies=False)
    # cmfeditions permissions
    portal.manage_permission('CMFEditions: Access previous versions', ('Manager', 'Site Administrator', 'Contributor',
                             'Editor', 'Member', 'Owner', 'Reviewer'), acquire=0)
    portal.manage_permission('CMFEditions: Save new version', ('Manager', 'Site Administrator', 'Contributor',
                             'Editor', 'Member', 'Owner', 'Reviewer'), acquire=0)
    transaction.commit()


def script5_13():
    portal = obj  # noqa
    verbose('Correcting datetime values on %s' % portal.absolute_url_path())
    from datetime import timedelta
    from plone import api
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


def script5_14():
    portal = obj  # noqa
    verbose('Changing personnel-folder interfaces on %s' % portal.absolute_url_path())
    from collective.contact.plonegroup.interfaces import IPloneGroupContact
    from imio.dms.mail.interfaces import IPersonnelContact
    from imio.helpers.cache import invalidate_cachekey_volatile_for
    from zope.interface import alsoProvides
    from zope.interface import noLongerProvides
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


def script5_15():
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
    portal.portal_setup.runImportStepFromProfile('profile-imio.dms.mail:default', 'plone.app.registry',
                                                 run_dependencies=False)
    portal.portal_setup.runImportStepFromProfile('profile-imio.dms.mail:default', 'actions', run_dependencies=False)
    transaction.commit()


def script5_16():
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


def script5_17():
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


def script5_18():
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


def script5_19():
    portal = obj  # noqa
    verbose('Correcting ckeditor skin on %s' % portal.absolute_url_path())
    portal.portal_properties.ckeditor_properties.skin = 'moono-lisa'
    transaction.commit()


def script5_20():
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


def script5_21():
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


def script5_22():
    portal = obj  # noqa
    verbose('Correcting collections on %s' % portal.absolute_url_path())
    # some collections contains in query a list of instances of ZPublisher.HTTPRequest.record. Must be a dict
    brains = portal.portal_catalog(portal_type='DashboardCollection')
    for brain in brains:
        col = brain.getObject()
        new_lst = []
        change = False
        for dic in col.query:
            if not isinstance(dic, dict):
                dic = dict(dic)
                change = True
            new_lst.append(dic)
        if change:
            col.query = new_lst
            verbose('This collection has been corrected {}'.format(brain.getPath()))


def script5_23():
    portal = obj  # noqa
    verbose('Correcting bad steps on %s' % portal.absolute_url_path())
    setup = api.portal.get_tool('portal_setup')
    ir = setup.getImportStepRegistry()
    change = False
    for step in ('task-uninstall', 'urban-postInstall'):
        if step in ir._registered:
            verbose('Removing bad step {}'.format(step))
            del ir._registered[step]
            change = True
    if change:
        setup._p_changed = True
    transaction.commit()


def script5_24():
    portal = obj  # noqa
    verbose('Correcting actionspanel transitions config on %s' % portal.absolute_url_path())
    transaction.commit()
    key = 'imio.actionspanel.browser.registry.IImioActionsPanelConfig.transitions'
    values = api.portal.get_registry_record(key)
    new_values = []
    for val in values:
        if val.startswith('dmsincomingmail.'):
            email_val = val.replace('dmsincomingmail.', 'dmsincoming_email.')
            if email_val not in values:
                new_values.append(email_val)
    if new_values:
        api.portal.set_registry_record(key, list(values) + new_values)
    verbose('Removing ClassificationCategory workflow on %s' % portal.absolute_url_path())
    pw = portal.portal_workflow
    wf = pw.getChainForPortalType('ClassificationCategory')
    if wf == ('active_inactive_workflow',):
        pw.setChainForPortalTypes(['ClassificationCategory'], ())
    transaction.commit()


def script5_25():
    portal = obj  # noqa
    verbose('Correcting bad migration %s' % portal.absolute_url_path())
    for wf_name, method in (('incomingmail_workflow', 'wf_conditions'),
                            ('outgoingmail_workflow', 'wf_conditions')):
        wf = portal.portal_workflow[wf_name]
        for tr_id in wf.transitions:
            tr = wf.transitions[tr_id]
            guard = tr.getGuard()
            cur_expr = guard.getExprText()
            to_replace = "wfconditions"
            if to_replace in cur_expr:
                new_expr = cur_expr.replace(to_replace, '{}'.format(method))
                if guard.changeFromProperties({'guard_expr': new_expr}):
                    tr.guard = guard
    transaction.commit()
