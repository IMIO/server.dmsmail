# -*- coding: utf-8 -*-
from imio.dms.mail.interfaces import IOMApproval
from imio.esign.utils import get_session_annotation

import os


def print_session_annotation(self):
    """
        Print the session annotation for debug.
    """
    annot = get_session_annotation()
    return str(annot)


def generate_pdf(self):
    om = self.__parent__
    fobj = self
    approval = IOMApproval(om)
    f_title = os.path.splitext(fobj.file.filename)[0]
    session_file_uids = []
    approval._create_pdf_file(fobj, fobj.file, f_title, fobj.UID(), 0, session_file_uids)
