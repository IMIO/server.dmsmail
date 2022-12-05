# -*- coding: utf-8 -*-

from imio.dms.mail import _tr
from imio.helpers.content import get_schema_fields
from operator import itemgetter
from Products.CPUtils.Extensions.utils import check_role


import sys


def get_pt_fields_info(pt, excluded):
    fields = get_schema_fields(type_name=pt, prefix=True)
    infos = []
    for fname, field in fields:
        if fname in excluded:
            continue
        field_type = '{}.{}'.format(field.__class__.__module__, field.__class__.__name__)
        value_type = hasattr(field, 'value_type') and field.value_type.__class__.__name__ or ''
        infos.append((fname, _tr(field.title), field_type, value_type))
    return sorted(infos, key=itemgetter(0))


portal = obj  # noqa
if not check_role(portal):
    sys.exit("You must have a manager role to run this script")
sfmt = '''   * - {}
     - {}
     - {}
     - {}'''
res = get_pt_fields_info('dmsincomingmail',
                         ['IDublinCore.contributors', 'IDublinCore.creators', 'IDublinCore.effective',
                          'IDublinCore.expires', 'IDublinCore.language', 'IDublinCore.rights', 'IDublinCore.subjects',
                          'INameFromTitle.title', 'ITask.assigned_group', 'ITask.enquirer', 'IVersionable.changeNote',
                          'notes', 'recipients', 'related_docs'])
res = get_pt_fields_info('dmsoutgoingmail',
                                 ['IDublinCore.contributors', 'IDublinCore.creators', 'IDublinCore.effective',
                                  'IDublinCore.expires', 'IDublinCore.language', 'IDublinCore.rights',
                                  'IDublinCore.subjects', 'INameFromTitle.title', 'ITask.assigned_group',
                                  'ITask.enquirer', 'IVersionable.changeNote', 'notes', 'related_docs'])
for name, title, klass, value in res:
    print(sfmt.format(name, title.encode('utf8'), klass, value))
