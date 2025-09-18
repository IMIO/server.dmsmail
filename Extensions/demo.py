# -*- coding: utf-8 -*-
from imio.dms.mail.utils import add_mail_files_to_session
from imio.dms.mail.utils import change_approval_user_status
from imio.dms.mail.utils import get_approval_annot
from plone import api
from Products.CMFPlone.utils import safe_unicode


def approve_file(self, mail=None, userid=None):
    """
        Approve the current file.
    """
    afile = self
    if userid is None:
        user = api.user.get_current()
        userid = user.getId()
    approval = get_approval_annot(mail)
    c_a = approval["approval"]  # current approval
    """
    {'approval': None,
     'files': {'48b13604e05843e4ae747e168af83ae5': {1: {'status': 'w'}, 2: {'status': 'w'}}},
     'numbers': {1: {'status': 'w', 'signer': ('dirg', 'dirg@macommune.be', u'Maxime DG', 1), 'users': ['dirg']}, 2: {'status': 'w', 'signer': ('bourgmestre', 'bourgmestre@macommune.be', u'Paul BM', 2), 'users': ['bourgmestre']}},
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
            message=u"The file '{}' is not in the list of files to approve.".format(safe_unicode(afile.Title())),
            request=self.REQUEST,
            type="warning",
        )
        return self.REQUEST.RESPONSE.redirect(mail.absolute_url())
    if approval["files"][f_uid][c_a]["status"] == "a":
        api.portal.show_message(
            message=u"The file '{}' has already been approved by {}.".format(
                safe_unicode(afile.Title()),
                approval["files"][f_uid][c_a].get("approved_by", "?")),
            request=self.REQUEST,
            type="warning",
        )
        return self.REQUEST.RESPONSE.redirect(mail.absolute_url())
    # "awaiting" (w), "pending" (p), "approved" (a)
    # approve
    approval["files"][f_uid][c_a]["approved_by"] = userid
    approval["files"][f_uid][c_a]["status"] = "a"
    """
    {'approval': None,
     'files': {'48b13604e05843e4ae747e168af83ae5': {1: {'status': 'w'}, 2: {'status': 'w'}}},
     'numbers': {1: {'status': 'w', 'signer': ('dirg', 'dirg@macommune.be', u'Maxime DG', 1), 'users': ['dirg']}, 2: {'status': 'w', 'signer': ('bourgmestre', 'bourgmestre@macommune.be', u'Paul BM', 2), 'users': ['bourgmestre']}},
     'users': {'bourgmestre': {'status': 'w', 'order': 2, 'name': u'Monsieur Paul BM'}, 'dirg': {'status': 'w', 'order': 1, 'name': u'Monsieur Maxime DG'}}}
     """  # noqa
    yet_to_approve = [fuid for fuid in approval["files"] if approval["files"][fuid][c_a]["status"] != "a"]
    if yet_to_approve:
        api.portal.show_message(
            message=u"The file '{}' has been approved by {}. However, there is/are yet {} files to apprrove in this "
                    u"mail.".format(safe_unicode(afile.Title()), userid, len(yet_to_approve)),
            request=self.REQUEST,
            type="info",
        )
        return self.REQUEST.RESPONSE.redirect(mail.absolute_url())
    change_approval_user_status(approval, c_a, "a", userid=userid)
    message = u"The file '{}' has been approved by {}. ".format(safe_unicode(afile.Title()), userid)
    max_number = max(approval["numbers"].keys())
    if c_a < max_number:
        approval["approval"] += 1
        change_approval_user_status(approval, approval["approval"], "p")
        mail.portal_catalog.reindexObject(mail, idxs=("approvings",), update_metadata=0)
        mail.reindexObjectSecurity()  # to update local roles from adapter
        message += u"Next approval number is {}.".format(approval["approval"])
        api.portal.show_message(message=message, request=self.REQUEST, type="info")
    else:
        approval["approval"] = 99  # all approved
        mail.portal_catalog.reindexObject(mail, idxs=("approvings",), update_metadata=0)
        message += u"All approvals have been done for this file."
        api.portal.show_message(message=message, request=self.REQUEST, type="info")
        # we create a signing session if needed
        if mail.esign:
            with api.env.adopt_roles(["Manager"]):
                ret, msg = add_mail_files_to_session(mail, approval=approval)
                if not ret:
                    api.portal.show_message(
                        message=u"There was an error while creating the signing session: {}".format(msg),
                        request=self.REQUEST,
                        type="error",
                    )
                else:
                    api.portal.show_message(
                        message=u"A signing session has been created: {}".format(msg),
                        request=self.REQUEST,
                        type="info",
                    )
    return None
    # return self.REQUEST.RESPONSE.redirect(mail.absolute_url())


def approve_files(self, userid=None):
    """
        Approve all files in the current context.
    """
    for fil in self.get_files_to_sign():
        approve_file(fil, mail=self, userid=userid)
    return self.REQUEST.RESPONSE.redirect(self.absolute_url())
