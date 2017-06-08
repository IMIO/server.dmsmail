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

info = ["You can pass following parameters (with the first one always script number):", "1 : activate test message"]
scripts = {'1': script1}

if len(sys.argv) < 4 or sys.argv[3] not in scripts:
    error("Bad script parameter")
    verbose('\n>> =>'.join(info))
    sys.exit(0)

with api.env.adopt_user(username='admin'):
    scripts[sys.argv[3]]()
