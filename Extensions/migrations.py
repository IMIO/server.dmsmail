# -*- coding: utf-8 -*-

from Products.CPUtils.Extensions.utils import check_zope_admin, log_list
from collective.contact.plonegroup.interfaces import IPloneGroupContact
from datetime import datetime
from plone import api
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IVocabularyFactory


def migrate_ll(self, keep='city', doit=''):
    """
        Migrate La Louvière: delete incomingmails
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    out = []
    log_list(out, "Starting migrate_ll at %s\n" % datetime(1973, 02, 12).now())
    do_it = False
    if doit not in ('', '0', 'False', 'false'):
        do_it = True
    if keep == 'city':
        city = True
    else:
        city = False

    start = 'CPAS'
    #start = 'Direction générale'
    factory = getUtility(IVocabularyFactory, 'collective.contact.plonegroup.organization_services')
    voc = factory(self)
    kept = {}
    log_list(out, "Parameters: city=%s, doit=%s\n" % (city, do_it))
    for term in voc:
        tit = term.title.encode('utf8')
        if not city:
            if tit.startswith(start):
                kept[term.value] = tit
        elif not tit.startswith(start):
            kept[term.value] = tit
    log_list(out, "Kept list %s\n" % '\n'.join(kept.values()))

    plen = len(self.absolute_url())

    def delete(obj, intid, typ='', more=''):
        path = obj.absolute_url()[plen:]
        prt = "intid:%d, path:%s" % (intid, path)
        if more:
            prt += ', %s' % more.encode('utf8')
        log_list(out, "Deleting %s" % (prt))
        del_intids[typ].append(intid)
        if do_it:
            api.content.delete(obj=obj)

    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    del_intids = {'im': [], 'om': [], 'hp': [], 'pr': [], 'or': []}

    def get_intid(obj, create=True):
        # check that the object has an intid, otherwise there's nothing to be done
        try:
            return intids.getId(obj)
        except KeyError:
            log_list(out, "Missing intid for %s" % obj.absolute_url(), prefix='!! ')
            if create and do_it:
                return intids.register(obj)
        return 1

    # searching outgoing mails
    log_list(out, "\nOutgoing mails:")
    for brain in self.portal_catalog(portal_type='dmsoutgoingmail'):
        obj = brain.getObject()
        if not obj.treating_groups in kept:
            if len(obj.recipients) > 1:
                log_list(out, "Multiple recipients on om %s" % obj.absolute_url(), prefix='!! ')
            delete(obj, get_intid(obj), typ='om', more='recipient:%d' % obj.recipients[0].to_id)

    # searching incoming mails
    log_list(out, "\nIncoming mails:")
    for brain in self.portal_catalog(portal_type='dmsincomingmail'):
        obj = brain.getObject()
        if not obj.treating_groups in kept:
            delete(obj, get_intid(obj), typ='im', more='sender:%d' % obj.sender.to_id)

    def find_relations(contact):
        """
            Parameters:
            - from_attribute: schema attribute string
            - from_interfaces_flattened: Interface class (only one)
        """
        ret = []
        query = {'to_id': get_intid(contact)}
        for relation in catalog.findRelations(query):
            if (relation.from_id in del_intids['im'] or relation.from_id in del_intids['om'] or
                    relation.from_id in del_intids['hp']):
                continue
            ret.append(relation.from_object)
        return ret

    # check held_position
    log_list(out, "\nHeld positions:")
    for brain in self.portal_catalog(portal_type=['held_position']):
        obj = brain.getObject()
        if IPloneGroupContact.providedBy(obj):
            continue
        # check relations with incoming mails
        ret = find_relations(obj)
        #log_list(out, 'Current held_position %s' % obj.absolute_url())
        if not ret:
            delete(obj, get_intid(obj), typ='hp')

    # check person
    log_list(out, "\nPersons:")
    for brain in self.portal_catalog(portal_type=['person']):
        obj = brain.getObject()
        if IPloneGroupContact.providedBy(obj):
            continue
        # check relations with incoming mails
        ret = find_relations(obj)
        #log_list(out, 'Current person %s' % obj.absolute_url())
        if not ret:
            if not [hp for hp in obj.objectValues() if do_it or get_intid(hp) not in del_intids['hp']]:
                delete(obj, get_intid(obj), typ='pr')

    # check organizations
    log_list(out, "\nOrganizations:")
    orgs = {}
    for brain in self.portal_catalog(portal_type=['organization'], sort_on='path', sort_order='reverse'):
        obj = brain.getObject()
        if IPloneGroupContact.providedBy(obj):
            continue
        # check relations with incoming mails or held_positions
        ret = find_relations(obj)
        #log_list(out, 'Current org %s' % obj.absolute_url())
        if not ret:
            if '/'.join(obj.getPhysicalPath()) not in orgs:
                delete(obj, get_intid(obj), typ='or')
        else:
            parts = brain.getPath().split('/')
            while(parts):
                parts.pop()
                path = '/'.join(parts)
                if path not in orgs:
                    orgs[path] = ''

    log_list(out, "\nDeleted im: %d, om: %d, hp: %d, pers: %d, org: %d\n" % (len(del_intids['im']),
                                                                             len(del_intids['om']),
                                                                             len(del_intids['hp']),
                                                                             len(del_intids['pr']),
                                                                             len(del_intids['or'])))

    # check cleaning
    if do_it:
        for brain in self.portal_catalog(portal_type='dmsincomingmail'):
            obj = brain.getObject()
            rel = obj.sender
            if rel.isBroken() or rel.to_path is None:
                log_list(out, "Sender relation broken on %s" % brain.getPath(), prefix='!! ')

    log_list(out, "\nFinished migrate_ll at %s" % datetime(1973, 02, 12).now())
    return '\n'.join(out)
