# -*- coding: utf-8 -*-

from collective.contact.plonegroup.utils import get_organizations
from imio.dms.mail import CONTACTS_PART_SUFFIX
from imio.dms.mail import CREATING_GROUP_SUFFIX
from plone.app.uuid.utils import uuidToObject
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.CPUtils.Extensions.utils import check_zope_admin
from Products.CPUtils.Extensions.utils import log_list
from Products.CPUtils.Extensions.utils import object_link
from zope.annotation.interfaces import IAnnotations

import os


def correct_ref(self, change=''):
    """
        Correct empty ref number in dmsmail 0.1
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    pc = self.portal_catalog
    brains = pc(portal_type='dmsincomingmail', sort_on='created')
    prev_ref = ''
    out = []
    for brain in brains:
        if brain.internal_reference_number is not None:
            prev_ref = brain.internal_reference_number
        else:
            obj = brain.getObject()
            # with default config value
            (begin, nb) = prev_ref.split('/')
            new_ref = '%s/%d' % (begin, int(nb)+1)
            # for cpas mons
            # nb = prev_ref
            # new_ref = '%03d' % (int(nb) + 1)
            out.append("<a href='%s'>%s</a>, %s, %s" % (obj.absolute_url(), obj.Title(), prev_ref, new_ref))
            prev_ref = new_ref
            if change == '1':
                obj.internal_reference_no = prev_ref
                obj.reindexObject()
                out[-1] += " => %s" % obj.Title()
    return '\n<br />'.join(out)


def check_sender(self):
    """
        Check the sender
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    pc = self.portal_catalog
    brains = pc(portal_type='dmsincomingmail', sort_on='created')
    out = []
    for brain in brains:
        obj = brain.getObject()
        if obj.sender.isBroken():
            out.append("<a href='%s'>%s</a>" % (obj.absolute_url(), obj.Title()))
    return '\n<br />'.join(out)


def relation_infos(rel):
    return {'br': rel.isBroken(), 'fr_i': rel.from_id, 'fr_o': rel.from_object, 'fr_a': rel.from_attribute,
            'fr_p': rel.from_path, 'to_i': rel.to_id, 'to_o': rel.to_object, 'to_p': rel.to_path}
    # rel.from_interfaces, rel.from_interfaces_flattened, rel.to_interfaces, rel.to_interfaces_flattened


def list_all_relations(self):
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    from zope.component import queryUtility
    from zc.relation.interfaces import ICatalog  # noqa
    catalog = queryUtility(ICatalog)
    out = []
    rels = list(catalog.findRelations())
    for rel in rels:
        out.append(str(relation_infos(rel)))
    return '\n'.join(out)


def check_intids(self, change=''):
    """
        Check relations for missing intids.
        TO ADD: check for all objects if they are in the intids catalog
    """
    """
        relations problems
        see collective.contact.core.upgrades.upgrades.reindex_relations
        see from z3c.relationfield.event import updateRelations
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    from zc.relation.interfaces import ICatalog
    from zope.app.intid.interfaces import IIntIds
    from zope.component import getUtility

    intids = getUtility(IIntIds)
    rels = getUtility(ICatalog)
    out = ['check_intids\n']
    relations = list(rels.findRelations())
    for rel in relations:
        if not rel.from_id or not intids.queryObject(rel.from_id, False):
            log_list(out, "Missing from_id %s" % relation_infos(rel))
        elif not rel.to_id or not intids.queryObject(rel.to_id, False):
            log_list(out, "Missing to_id %s" % relation_infos(rel))
        elif not rel.from_object or not intids.queryId(rel.from_object, False):
            log_list(out, "Missing from_object %s" % relation_infos(rel))
        elif not rel.to_object or not intids.queryId(rel.to_object, False):
            log_list(out, "Missing to_object %s" % relation_infos(rel))
    return '\n'.join(out)


def add_md5(self, change=''):
    """ Add md5 value if none """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    from plone import api
    from imio.dms.mail.setuphandlers import list_templates
    from Products.CMFPlone.utils import base_hasattr
    templates_list = [(tup[1], tup[2]) for tup in list_templates()]
    portal = api.portal.getSite()
    ret = []
    for (ppath, ospath) in templates_list:
        ppath = ppath.strip('/ ')
        obj = portal.unrestrictedTraverse(ppath, default=None)
        if not base_hasattr(obj, 'style_modification_md5'):
            continue
        if obj.style_modification_md5 is None:
            ret.append('%s with empty md5' % ppath)
            if change == '1':
                obj.style_modification_md5 = obj.current_md5
    if not ret:
        return 'Nothing changed'
    return '\n'.join(ret)


def do_transition(self, typ='dmsincomingmail', transition='close_manager', criteria="{}", limit=5000, change=''):
    """ Apply a transition to objects found following criterias.

    :param self: portal is the best
    :param typ: portal_type searched
    :param transition: transition to apply
    :param criteria: criteria string that will be evaluated
    :param limit: maximum objects handled
    :param change: must be to 1 to apply changes
    :return: messages string
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    from Products.CMFCore.WorkflowCore import WorkflowException
    from DateTime import DateTime
    pc = self.portal_catalog
    pw = self.portal_workflow
    ret = ["Can be run like this: \n* script_name?criteria={'created': {'query': (DateTime('2022-04-01 00:00:01'), "
           "DateTime('2022-09-22 00:00:01'),), 'range': 'min:max'}}\n* script_name?criteria={'created': {'query': "
           "(DateTime('2022-04-01 00:00:01'),), 'range': 'max:'}}\n\n",
           'Parameters:', "typ= '%s'" % typ, "transition: '%s'" % transition, "criteria: '%s'" % criteria,
           "limit: '%s'" % limit, "change: '%s'\n" % change]
    try:
        crit_dic = eval(criteria)
    except Exception, msg:
        ret.append("Problem evaluating criteria: %s" % msg)
        return '\n'.join(ret)
    if not isinstance(crit_dic, dict):
        ret.append("Cannot eval criteria as dict")
        return '\n'.join(ret)
    criterias = {'review_state': {'not': ['closed']}}  # must be a parameter
    criterias.update(crit_dic)
    ret.append("criterias=%s\n" % criterias)
    brains = pc(portal_type=typ, **criterias)
    tot = len(brains)
    changed = 0
    for i, brain in enumerate(brains):
        if i >= int(limit):
            ret.append('!! Limit of {} objects reached !! Must run script again\n'.format(limit))
            break
        obj = brain.getObject()
        try:
            if change == '1':
                pw.doActionFor(obj, transition)
                changed += 1
        except WorkflowException:
            ret.append("Cannot do transition on '%s'" % brain.getPath())
    ret.append("Tot=%d" % tot)
    ret.append("Changed=%d" % changed)
    return '\n'.join(ret)


def set_state(self, typ='dmsincomingmail', state='closed', criteria="{}", limit=5000, change=''):
    """Set state on objects found following criterias.

    :param self: portal is the best
    :param typ: portal_type searched
    :param state: destination state
    :param criteria: criteria string that will be evaluated
    :param limit: maximum objects handled
    :param change: must be to 1 to apply changes
    :return: messages string
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    from Products.CMFCore.WorkflowCore import WorkflowException
    from DateTime import DateTime
    pc = self.portal_catalog
    pw = self.portal_workflow
    ret = ["Can be run like this: \n* script_name?criteria={'created': {'query': (DateTime('2022-04-01 00:00:01'), "
           "DateTime('2022-09-22 00:00:01'),), 'range': 'min:max'}}\n* script_name?criteria={'created': {'query': "
           "(DateTime('2022-04-01 00:00:01'),), 'range': 'max:'}}\n\n",
           'Parameters:', "typ= '%s'" % typ, "state: '%s'" % state, "criteria: '%s'" % criteria, "limit: '%s'" % limit,
           "change: '%s'\n" % change]
    try:
        crit_dic = eval(criteria)
    except Exception, msg:
        ret.append("Problem evaluating criteria: %s" % msg)
        return '\n'.join(ret)
    if not isinstance(crit_dic, dict):
        ret.append("Cannot eval criteria as dict")
        return '\n'.join(ret)
    criterias = {'review_state': {'not': [state]}}
    criterias.update(crit_dic)
    ret.append("criterias=%s\n" % criterias)
    brains = pc(portal_type=typ, **criterias)
    ret.append("Tot=%d" % len(brains))
    changed = 0
    workflow_id = ''
    member_id = api.user.get_current().getId()
    for i, brain in enumerate(brains):
        if not workflow_id:
            workflow_id = pw.getChainForPortalType(brain.portal_type)[0]
        if i >= int(limit):
            ret.append('\n!! Limit of {} objects reached !! Must run script again\n'.format(limit))
            break
        obj = brain.getObject()
        mod_time = DateTime()
        if change == '1':
            pw.setStatusOf(workflow_id, obj, {'action': state, 'review_state': state, 'actor': member_id,
                                              'comments': '', 'time': mod_time})
            obj.setModificationDate(mod_time)  # also to update cache...
            obj.reindexObject(['review_state', 'state_group', 'modified'])
            changed += 1
    ret.append("Changed=%d" % changed)
    return '\n'.join(ret)


def users_to_group(self, source='editeur,validateur', dest='encodeur', change=''):
    """ Add editeur and validateur users to encodeur groups """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    ret = ["'source' parameter = '%s'" % source,
           "'dest' parameter = '%s'" % dest,
           "'change' parameter = '%s'" % change]
    try:
        sources = source.split(',')
    except Exception, msg:
        return "Source parameter isn't correct: %s" % (msg)
    ret.append('<h2>Add users to %s groups</h2>' % (dest))
    from plone import api
    from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY
    orgs = api.portal.get_registry_record(ORGANIZATIONS_REGISTRY)
    for org in orgs:
        try:
            enc_group = api.group.get('%s_%s' % (org, dest))
            if not enc_group:
                raise Exception('group is None')
        except Exception, msg:
            ret.append("!! Group '%s_%s' doesn't exist: %s" % (org, dest, msg))
            continue
        enc_users = api.user.get_users(group=enc_group)
        for func in sources:
            gname = '%s_%s' % (org, func)
            try:
                group = api.group.get(gname)
                if not group:
                    raise Exception('group is None')
            except Exception, msg:
                ret.append("!! Group '%s' doesn't exist: %s" % (gname, msg))
                continue
            for user in api.user.get_users(group=group):
                if user not in enc_users:
                    enc_users.append(user)
                    if change == '1':
                        api.group.add_user(group=enc_group, user=user)
                        ret.append("User '%s' is added to '%s'" % (user.id, enc_group.getProperty('title')))
                    else:
                        ret.append("User '%s' will be added to '%s'" % (user.id, enc_group.getProperty('title')))
    return "</br>\n".join(ret)


def correct_internal_reference(self, toreplace='', by='', request="{'portal_type': 'dmsincomingmail'}", change=''):
    """ Replace something in internal reference number"""
    # tubize: {'portal_type': 'dmsincomingmail', 'in_out_date':{'range':'min', 'query':datetime(2018,1,1)}}
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    if not toreplace:
        return "!! toreplace param cannot be empty"
    if not request:
        return "!! request param cannot be empty"
    import re
    from Products.CMFPlone.utils import safe_unicode
    try:
        p_o = re.compile(toreplace)
    except Exception, msg:
        return "!! Cannot compile replace expression '%s': '%s'" % (toreplace, msg)
    try:
        dic = eval(request)
    except Exception, msg:
        return "!! Cannot eval request '%s': '%s'" % (request, msg)
    out = ['request= %s' % dic]
    for brain in self.portal_catalog(**dic):
        m_o = p_o.search(safe_unicode(brain.internal_reference_number))
        if not m_o:
            continue
        res = p_o.sub(safe_unicode(by), safe_unicode(brain.internal_reference_number))
        out.append("'%s': '%s' => '%s'" % (brain.getPath(), safe_unicode(brain.internal_reference_number),
                                           res))
        if change == '1':
            obj = brain.getObject()
            obj.internal_reference_no = res
            obj.reindexObject(idxs=['internal_reference_number', 'sortable_title', 'SearchableText', 'Title'])
    return '\n'.join(out)


def various(self):
    """ various check script """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    pc = self.portal_catalog
    previous = None
    ret = []
    mails = {}
    # find same barcode in multiple outgoing mails
    for brain in pc(portal_type='dmsommainfile', sort_on='scan_id', sort_order='ascending'):
        obj = brain.getObject()
        parent = obj.__parent__
        if parent not in mails:
            mails[parent] = []
        if brain.scan_id not in mails[parent]:
            mails[parent].append(brain.scan_id)
        if not previous:
            previous = obj
            continue
        # check current with previous object
        if brain.scan_id == previous.scan_id and parent != previous.__parent__:
            ret.append(u"Same scan_id '%s' in '%s' and '%s'" % (brain.scan_id, object_link(parent),
                                                                object_link(previous.__parent__)))
        previous = obj
    # find different barcodes in same outgoing mail
    for mail in mails:
        if len(mails[mail]) > 1:
            ret.append(u"Multiple scan_ids in '%s': %s" % (object_link(mail), mails[mail]))
    return "</br>\n".join(ret)


def various2(self):
    """ various check script """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    from imio.dms.mail.interfaces import IActionsPanelFolder
    from collective.querynextprev.interfaces import INextPrevNotNavigable
    from zope.interface import alsoProvides
    portal = self
    pc = portal.portal_catalog
    for fld in (portal['templates']['om'], portal['contacts']['contact-lists-folder']):
        folders = pc(path='/'.join(fld.getPhysicalPath()), portal_type='Folder')
        for brain in folders:
            folder = brain.getObject()
            if folder == fld:
                continue
            print brain.getPath()
            alsoProvides(folder, IActionsPanelFolder)
            alsoProvides(folder, INextPrevNotNavigable)


def various3(self):
    """ various check script """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    from plone import api
    pc = self.portal_catalog
    for brain in pc(portal_type='dmsincoming_email', sort_on='created', sort_order='descending'):
        nb = int(brain.internal_reference_number[1:])
        if nb < 10723:
            break
        # api.content.delete(obj=brain.getObject())
        print(brain.Title)


def dg_doc_info(self):
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    annot = IAnnotations(self)
    dic = annot['documentgenerator']
    ret = []
    ret.append(str(dic))
    if 'context_uid' in dic:
        ret.append("'context_uid': '%s'" % uuidToObject(dic['context_uid']).absolute_url())
    if 'template_uid' in dic:
        ret.append("'template_uid': '%s'" % uuidToObject(dic['template_uid']).absolute_url())
    return '\n'.join(ret)


def clean_catalog(self):
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    out = []
    pc = self.portal_catalog
    catalog = pc._catalog
    uids = catalog.uids  # contains rid by path
    paths = catalog.paths  # contains path by uid
    indexes = catalog.indexes.keys()
    for rid in catalog.data.keys():
        path = paths.get(rid, None)
        if path is None:
            out.append("ERROR: cannot find rid '{}' in paths".format(rid))
            continue
        # 1) we have an rid without object: deleted path
        # 2) the rid is not the one stored in uids
        if path not in uids or uids[path] != rid:
            out.append("CLEANING rid '{}' for path '{}'".format(rid, path))
            for name in indexes:
                x = catalog.getIndex(name)
                if hasattr(x, 'unindex_object'):
                    x.unindex_object(rid)
            del catalog.data[rid]
            del paths[rid]
            catalog._length.change(-1)
    return '\n'.join(out)


def check_personnel_folder(self):
    """ check personnel-folder content to find missing or duplicated information """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    out = []
    if self.id != 'personnel-folder':
        return 'You must be on personnel-folder'
    userids = {}
    for pers in self.objectValues():
        if not pers.userid:
            out.append('empty userid: {}'.format(object_link(pers)))
        elif pers.userid in userids:
            out.append("duplicated userid '{}' : {} and {}".format(pers.userid, object_link(userids[pers.userid]),
                                                                   object_link(pers)))
        else:
            userids[pers.userid] = pers
    return '\n'.join(out)


def set_creating_group(self, types='', uid='', change='', force=''):
    """Set creating_group for existing objects."""
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    if not uid or not types:
        return 'You have to pass types (comma separated) and uid parameters'
    out = []
    ptypes = [typ.strip() for typ in types.split(',')]
    # TODO check if each ptype exists
    # TODO check if creating_group is in schema
    uids = get_organizations(not_empty_suffix=CREATING_GROUP_SUFFIX, only_selected=False, the_objects=False,
                             caching=False)
    uids += get_organizations(not_empty_suffix=CONTACTS_PART_SUFFIX, only_selected=False, the_objects=False,
                              caching=False)
    uid = safe_unicode(uid)
    if uid not in uids:
        return "You cannot set this uid '{}' not in configured uids '{}'".format(uid, uids)
    # search
    pc = self.portal_catalog
    brains = pc(portal_type=ptypes)
    out.append('Found {} objects of types {}'.format(len(brains), ptypes))
    modified = 0
    if change == '1':
        for brain in brains:
            obj = brain.getObject()
            if force == '1' or obj.creating_group is None:
                modified += 1
                obj.creating_group = uid
                obj.reindexObject(['assigned_group'])
    out.append('Modified {} objects'.format(modified))
    return '\n'.join(out)
