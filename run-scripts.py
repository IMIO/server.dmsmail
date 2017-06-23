import sys
from imio.pyutils.system import verbose, error
import transaction
from plone import api

# Parameters check
if len(sys.argv) < 3 or sys.argv[2] != 'run-scripts.py':
    error("Inconsistent or unexpected args len: %s" % sys.argv)
    sys.exit(0)


def script1():
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


def script2():
    verbose('Setting documentgenerator config on %s' % obj.absolute_url_path())
    from collective.documentgenerator.config import set_oo_port, set_uno_path
    set_oo_port()
    set_uno_path()
    transaction.commit()


def script3():
    if len(sys.argv) < 6:
        error("Missing profile and step names in args")
        sys.exit(0)
    profile = sys.argv[4]
    step = sys.argv[5]
    if not profile.startswith('profile-'):
        profile = 'profile-%s' % profile
    verbose('Running "%s#%s" step on %s' % (profile, step, obj.absolute_url_path()))
    ret = obj.portal_setup.runImportStepFromProfile(profile, step)
    if 'messages' in ret:
        for step in ret['messages']:
            verbose("%s:\n%s" % (step, ret['messages'][step]))
    else:
        verbose("No output")
    transaction.commit()


info = ["You can pass following parameters (with the first one always script number):", "1 : activate test message"]
scripts = {'1': script1, '2': script2, '3': script3}

if len(sys.argv) < 4 or sys.argv[3] not in scripts:
    error("Bad script parameter")
    verbose('\n>> =>'.join(info))
    sys.exit(0)

with api.env.adopt_user(username='admin'):
    scripts[sys.argv[3]]()
