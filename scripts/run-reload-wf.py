# -*- coding: utf-8 -*-
from collections import OrderedDict
from collective.wfadaptations.api import apply_from_registry
from collective.wfadaptations.api import get_applied_adaptations
from imio.helpers.security import setup_app
from imio.helpers.security import setup_logger
from imio.helpers.setup import load_workflow_from_package
from Products.CMFPlone.utils import safe_unicode

import logging
import transaction


logger = logging.getLogger('wkf:')
portal = obj  # noqa
setup_logger()
setup_app(app)  # noqa
wkf_name = "outgoingmail_workflow"
wkf = portal.portal_workflow[wkf_name]
storage = {}


def states_info(msg, store=None):
    print(msg)
    states = [wn for wn in wkf.states]
    for state_name in sorted(states):
        state = wkf.states[state_name]
        print(u">> %s: %s" % (state_name, safe_unicode(state.title)))
        print(u"\ttransitions: %s" % u", ".join(sorted(state.transitions)))
        if store:
            storage.setdefault(store, OrderedDict())[state_name] = u", ".join(sorted(state.transitions))


def compare_storage(frm, to):
    errors = 0
    for state_name in storage[frm]:
        if state_name not in storage[to]:
            print(u"Error comparing %s to %s: state %s not there" % (frm, to, state_name))
            errors += 1
            continue
        if storage[frm][state_name] != storage[to][state_name]:
            print(u"Error comparing %s to %s state %s transitions: %s <> %s" % (
                frm, to, state_name, storage[frm][state_name], storage[to][state_name]))
            errors += 1
            continue
    if errors:
        return False
    return True


states_info("STARTING %s reload script" % wkf_name, store="start")

reset = load_workflow_from_package("outgoingmail_workflow", "imio.dms.mail:default")
states_info("RELOADED base %s wokflow" % wkf_name)
applied_adaptations = [dic["adaptation"] for dic in get_applied_adaptations()
                       if dic["workflow"] == "outgoingmail_workflow"]
if reset:
    for i, name in enumerate(applied_adaptations):
        success, errors = apply_from_registry(reapply=True, name=name)
        states_info("RE-APPLIED %s adaptation" % name, store=(i == len(applied_adaptations) - 1 and "last" or None))
        if errors:
            raise Exception("Problem applying wf adaptations '%s': %d errors" % (name, errors))
else:
    raise Exception("outgoingmail_workflow not reloaded !")

if compare_storage("start", "last"):
    transaction.commit()
