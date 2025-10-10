# -*- coding: utf-8 -*-
from datetime import datetime
from imio.dms.mail import _
from imio.dms.mail.utils import add_mail_files_to_session
from imio.dms.mail.utils import change_approval_user_status
from imio.dms.mail.utils import get_approval_annot
from imio.esign.utils import get_session_annotation
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
    {
     'approval': 1,
     'files': {'4115fb4c265647ca82d85285504973b8': {1: {'status': 'p'}, 2: {'status': 'w'}}}, 
     'numbers': {1: {'status': 'p', 'signer': ('dirg', 'stephan.geulette@imio.be', u'Maxime DG', u'Directeur G\xe9n\xe9ral'), 'users': ['dirg']}, 2: {'status': 'w', 'signer': ('bourgmestre', 'stephan.geulette+s2@imio.be', u'Paul BM', u'Bourgmestre'), 'users': ['bourgmestre', 'chef']}},
     'session_id': None,
     'users': {'bourgmestre': {'status': 'w', 'editor': False, 'name': u'Monsieur Paul BM', 'order': 2}, 'chef': {'status': 'w', 'editor': False, 'name': u'Monsieur Michel Chef', 'order': 2}, 'dirg': {'status': 'w', 'editor': True, 'name': u'Monsieur Maxime DG', 'order': 1}},
    }
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
    approval["files"][f_uid][c_a]["approved_on"] = datetime.now()
    approval["files"][f_uid][c_a]["status"] = "a"
    """
    {
     'approval': 1,
     'files': {'4115fb4c265647ca82d85285504973b8': {1: {'status': 'p'}, 2: {'status': 'w'}}}, 
     'numbers': {1: {'status': 'p', 'signer': ('dirg', 'stephan.geulette@imio.be', u'Maxime DG', u'Directeur G\xe9n\xe9ral'), 'users': ['dirg']}, 2: {'status': 'w', 'signer': ('bourgmestre', 'stephan.geulette+s2@imio.be', u'Paul BM', u'Bourgmestre'), 'users': ['bourgmestre', 'chef']}},
     'session_id': None,
     'users': {'bourgmestre': {'status': 'w', 'editor': False, 'name': u'Monsieur Paul BM', 'order': 2}, 'chef': {'status': 'w', 'editor': False, 'name': u'Monsieur Michel Chef', 'order': 2}, 'dirg': {'status': 'w', 'editor': True, 'name': u'Monsieur Maxime DG', 'order': 1}},
    }
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


def print_session_annotation(self):
    """
        Print the session annotation for debug.
    """
    annot = get_session_annotation()
    return str(annot)


def add_to_session(self):
    """
        Add the current file to the esign session.
    """
    if self.portal_type != "dmsoutgoingmail":
        return
    mail = self
    ret, msg = add_mail_files_to_session(mail, approval=get_approval_annot(mail))
    if not ret:
        api.portal.show_message(
            message=_(u"There was an error while creating the signing session: ${msg} !",
                      mapping={"msg": msg}),
            request=mail.REQUEST,
            type="error",
        )
    else:
        api.portal.show_message(
            message=_(u"A signing session has been created: ${msg}.",
                      mapping={"msg": msg}),
            request=mail.REQUEST,
            type="info",
        )
    return self.REQUEST.RESPONSE.redirect(mail.absolute_url())
