# -*- coding: utf-8 -*-
from imio.dms.mail.utils import change_approval_user_status
from imio.dms.mail.utils import get_approval_annot
from plone import api


def approve_file(self, mail=None):
    """
        Approve the current file.
    """
    afile = self
    # get current user
    user = api.user.get_current()
    userid = user.getId()
    # TEMPORARY for tests
    # userid = "dirg"
    approval = get_approval_annot(mail)
    c_a = approval["approval"]
    import ipdb; ipdb.set_trace()
    """
    {'approval': 1,
     'files': {'48b13604e05843e4ae747e168af83ae5': {1: {'status': 'w', 'users': ['dirg']}, 2: {'status': 'w', 'users': ['bourgmestre']}}},
     'numbers': {1: {'status': 'w', 'users': ['dirg']}, 2: {'status': 'w', 'users': ['bourgmestre']}},
     'users': {'bourgmestre': {'status': 'w', 'order': 2, 'name': u'Monsieur Paul BM'}, 'dirg': {'status': 'w', 'order': 1, 'name': u'Monsieur Maxime DG'}}}
    """  # noqa
    # checks
    if not c_a:
        api.portal.show_message(
            message=u"You cannot approve for now.",
            request=self.REQUEST,
            type="warning",
        )
        return self.REQUEST.RESPONSE.redirect(mail.absolute_url())
    if userid not in approval["users"] or approval["users"][userid]["order"] != c_a:
        api.portal.show_message(
            message=u"Current user {} cannot approve the file.".format(userid),
            request=self.REQUEST,
            type="warning",
        )
        return self.REQUEST.RESPONSE.redirect(mail.absolute_url())
    # TODO is this useful ?
    if approval["users"][userid]["status"] != "w":
        api.portal.show_message(
            message=u"Current user {} has already approved the file.".format(userid),
            request=self.REQUEST,
            type="warning",
        )
        return self.REQUEST.RESPONSE.redirect(mail.absolute_url())
    f_uid = afile.UID()
    if f_uid not in approval["files"]:
        api.portal.show_message(
            message=u"The file is not in the list of files to approve.",
            request=self.REQUEST,
            type="warning",
        )
        return self.REQUEST.RESPONSE.redirect(mail.absolute_url())
    if approval["files"][f_uid][c_a]["status"] == "a":
        api.portal.show_message(
            message=u"The file has already been approved by {}.".format(
                approval["files"][f_uid][c_a].get("approving", "?")),
            request=self.REQUEST,
            type="warning",
        )
        return self.REQUEST.RESPONSE.redirect(mail.absolute_url())
    # "awaiting" (w), "pending" (p), "approved" (a)
    # approve
    approval["files"][f_uid][c_a]["approving"] = userid
    change_approval_user_status(approval, c_a, "a", userid=userid)
    message = u"The file has been approved by {}. ".format(userid)
    max_number = max(approval["numbers"].keys())
    if c_a < max_number:
        approval["approval"] += 1
        change_approval_user_status(approval, approval["approval"], "p")
        mail.portal_catalog.reindexObject(mail, idxs=("approvings",), update_metadata=0)
        message += u"Next approval number is {}.".format(approval["approval"])
        api.portal.show_message(message=message, request=self.REQUEST, type="info")
    else:
        message += u"All approvals have been done."
        api.portal.show_message(message=message, request=self.REQUEST, type="info")
        # TO BE CONTINUED

    return self.REQUEST.RESPONSE.redirect(mail.absolute_url())


def approve_files(self):
    """
        Approve all files in the current context.
    """
    for fil in self.get_files_to_sign():
        approve_file(fil, mail=self)
