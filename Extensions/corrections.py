
def correct_ref(self, change=''):
    """
        Correct empty ref number in dmsmail 0.1
    """
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
    pc = self.portal_catalog
    brains = pc(portal_type='dmsincomingmail', sort_on='created')
    out = []
    for brain in brains:
        obj = brain.getObject()
        if obj.sender.isBroken():
            out.append("<a href='%s'>%s</a>" % (obj.absolute_url(), obj.Title()))
    return '\n<br />'.join(out)


def list_relations(self):
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
        if i > limit:
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
