# -*- coding: utf-8 -*-

from datetime import datetime
from DateTime import DateTime
from datetime import timedelta
from plone.app.uuid.utils import uuidToObject
from Products.CPUtils.Extensions.utils import check_zope_admin
from Products.CPUtils.Extensions.utils import fileSize
from Products.CPUtils.Extensions.utils import log_list
from Products.CPUtils.Extensions.utils import object_link
from Products.ZCatalog.ProgressHandler import ZLogHandler
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


def list_relations(self):
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    from zope.component import queryUtility
    from zc.relation.interfaces import ICatalog
    catalog = queryUtility(ICatalog)
    out = []
    rels = list(catalog.findRelations())
    for rel in rels:
        out.append(str(rel.__dict__))
    return '\n<br />'.join(out)


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


def do_transition(self, typ='dmsincomingmail', transition='close_manager', criteria="{}", limit=10000, change=''):
    """ Apply a transition to many objects """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    from Products.CMFCore.WorkflowCore import WorkflowException
    from DateTime import DateTime
    pc = self.portal_catalog
    pw = self.portal_workflow
    ret = []
    ret.append('Parameters:')
    ret.append("typ= '%s'" % typ)
    ret.append("transition: '%s'" % transition)
    ret.append("criteria: '%s'" % criteria)
    ret.append("limit: '%s'" % limit)
    ret.append("change: '%s'\n" % change)
    try:
        crit_dic = eval(criteria)
    except Exception, msg:
        ret.append("Problem evaluating criteria: %s" % (msg))
        return '\n'.join(ret)
    if not isinstance(crit_dic, dict):
        ret.append("Cannot eval criteria as dict")
        return '\n'.join(ret)
    criterias = {'review_state': {'not': ['closed']}}
    start = DateTime('2017-09-22 00:00:01')  # noqa
    end = DateTime('2017-10-08 23:59:59')  # noqa
    # criterias.update({'created': {'query': (start, end,), 'range': 'min:max'}})
    criterias.update(crit_dic)
    ret.append("criterias=%s\n" % criterias)
    brains = pc(portal_type=typ, **criterias)
    tot = len(brains)
    changed = 0
    for i, brain in enumerate(brains):
        if i >= int(limit):
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


def dv_clean(self, days_back='365', date_back=None, batch='3000'):
    """
        Remove document viewer annotation on old mails.
        days_back: default behavior: we take closed items not modified from this range
        date_back: if present, we take items not modified from this date (whatever the state)
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    start = datetime.now()
    out = ["call the script followed by needed parameters:",
           "-> days_back=nb of days to keep (default '365') (not used if date_back is used)",
           "-> date_back=fixed date to consider (default None) (format YYYYMMDD)",
           "-> batch=batch number to commit each nth (default '3000')"]
    pghandler = ZLogHandler(steps=int(batch))
    log_list(out, "Starting dv_clean at {}".format(start), pghandler)
    from collective.documentviewer.convert import saveFileToBlob
    from BTrees.OOBTree import OOBTree  # noqa
    from Products.CPUtils.Extensions.utils import dv_images_size
    current_dir = os.path.dirname(__file__)
    normal_blob = saveFileToBlob(os.path.join(current_dir, 'previsualisation_supprimee_normal.jpg'))
    blobs = {'large': normal_blob, 'normal': normal_blob,
             'small': saveFileToBlob(os.path.join(current_dir, 'previsualisation_supprimee_small.jpg'))}
    criterias = [
        {'portal_type': ['dmsincomingmail', 'dmsincoming_email']},
        {'portal_type': ['dmsoutgoingmail', 'dmsoutgoing_email']},
    ]
    state_criterias = [
        {'review_state': 'closed'},
        {'review_state': 'sent'},
    ]
    if date_back:
        if len(date_back) != 8:
            log_list(out, "Bad date_back length '{}'".format(date_back), pghandler)
            return
        mod_date = datetime.strptime(date_back, '%Y%m%d')
        # mod_date = add_timezone(mod_date, force=True)
    else:
        mod_date = start - timedelta(days=int(days_back))
    already_done = DateTime('2010/01/01').ISO8601()
    total = {'obj': 0, 'pages': 0, 'files': 0, 'size': 0}
    pc = self.portal_catalog
    for j, criteria in enumerate(criterias):
        if not date_back:
            criteria.update(state_criterias[j])  # noqa
        criteria.update({'modified': {'query': mod_date, 'range': 'max'}})  # noqa
        brains = pc(**criteria)
        bl = len(brains)
        pghandler.init(criteria['portal_type'][0], bl)
        total['obj'] += bl
        for i, brain in enumerate(brains, 1):
            mail = brain.getObject()
            for fid in mail.objectIds(ordered=False):
                fobj = mail[fid]
                if fobj.portal_type not in ['dmsmainfile', 'dmsommainfile', 'dmsappendixfile']:
                    continue
                annot = IAnnotations(fobj).get('collective.documentviewer', '')
                if not annot or not annot.get('successfully_converted'):
                    continue
                if annot['last_updated'] == already_done:
                    continue
                total['files'] += 1
                sizes = dv_images_size(fobj)
                total['pages'] += sizes['pages']
                total['size'] += (sizes['large'] + sizes['normal'] + sizes['small'] + sizes['text'])
                # clean annotation
                files = OOBTree()
                for name in ['large', 'normal', 'small']:
                    files['{}/dump_1.jpg'.format(name)] = blobs[name]
                annot['blob_files'] = files
                annot['num_pages'] = 1
                annot['pdf_image_format'] = 'jpg'
                annot['last_updated'] = already_done
            pghandler.report(i)
        pghandler.finish()

    end = datetime.now()
    delta = end - start
    log_list(out, "Finishing dv_clean, duration {}".format(delta), pghandler)
    total['deleted'] = total['pages'] * 4
    total['size'] = fileSize(total['size'])
    log_list(out,
             "Objects: '{obj}', Files: '{files}', Pages: '{pages}', Deleted: '{deleted}', Size: '{size}'".format(**total),
             pghandler)
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
