from Products.CPUtils.Extensions.utils import check_zope_admin, object_link


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
            #nb = prev_ref
            #new_ref = '%03d' % (int(nb) + 1)
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


def list_relations(self):
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    from zope.component import queryUtility
    from zc.relation.interfaces import ICatalog
    catalog = queryUtility(ICatalog)
    out = []
    rels = list(catalog.findRelations())
    for rel in rels:
        out.append(rel.__dict__)
        print rel.__dict__
    return '\n<br />'.join(out)


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
    start = DateTime('2017-09-22 00:00:01')
    end = DateTime('2017-10-08 23:59:59')
    #criterias.update({'created': {'query': (start, end,), 'range': 'min:max'}})
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


def add_encodeur_users(self, change=''):
    """ Add editeur and validateur users to encodeur groups """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    ret = ['<h2>Add users to encodeur groups</h2>']
    from plone import api
    from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY
    orgs = api.portal.get_registry_record(ORGANIZATIONS_REGISTRY)
    for org in orgs:
        try:
            enc_group = api.group.get('%s_encodeur' % org)
        except Exception, msg:
            ret.append("!! Group '%s_encodeur' doesn't exist: %s" % (org, msg))
            continue
        enc_users = api.user.get_users(group=enc_group)
        for func in ('editeur', 'validateur'):
            gname = '%s_%s' % (org, func)
            try:
                group = api.group.get(gname)
            except Exception, msg:
                ret.append("!! Group '%s' doesn't exist: %s" % (gname, msg))
                continue
            for user in api.user.get_users(group=group):
                if user not in enc_users:
                    ret.append("User '%s' will be added to '%s'" % (user.id, enc_group.getProperty('title')))
                    enc_users.append(user)
                    if change == '1':
                        api.group.add_user(group=enc_group, user=user)
    return "</br>\n".join(ret)


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
