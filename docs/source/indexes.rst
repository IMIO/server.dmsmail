########
Indexers
########

*******
Indexes
*******

Alphabetically listed

assigned_group
--------------
Product = collective.task, FieldIndex

Used on
    * IContentish : assigned_group
    * IDmsMailCreatingGroup : creating_group

assigned_user
-------------
Product = collective.task, FieldIndex

Used on IContentish : assigned_user

email
-----
Product = collective.contact.core, FieldIndex

Used on
    * IContactContent : email
    * IImioDmsIncomingMail : orig_sender_email
    * IImioDmsOutgoingMail : orig_sender_email

enabled
-------
Product = collective.eeafaceted.collectionwidget, BooleanIndex

Used on
    * ICollection : enabled
    * IImioDmsOutgoingMail : "email is ready to be sent"

external_reference_number
-------------------------
Product = collective.dms.mailcontent, FieldIndex

Used on
    * IDmsIncomingMail : external_reference_no
    * IDmsOutgoingMail : external_reference_no

in_out_date
-----------
Product = imio.dms.mail, DateIndex

Used on
    * IImioDmsIncomingMail : reception_date
    * IImioDmsOutgoingMail : outgoing_date

in_reply_to
-----------
Product = Products.CMFPlone, FieldIndex

Used on * : in_reply_to (for plone comments !, not reply_to from mailcontent)

internal_number
---------------
Product = collectibe.behavior.internalnumber, FieldIndex

Used on IContentish : internal_number

internal_reference_number
-------------------------
Product = collective.dms.mailcontent, FieldIndex

Used on
    * IDmsIncomingMail : internal_reference_no
    * IDmsOutgoingMail : internal_reference_no

labels
------
Product = ftw.labels, KeywordIndex

Used on ILabelSupport : annotation.

Stores a list of:
    * '_' : no label
    * label_id : for "global" label
    * user_id:label_id : for "by_user" label

mail_date
---------
Product = imio.dms.mail, DateIndex

Used on
    * IImioDmsIncomingMail : original_mail_date
    * IImioDmsOutgoingMail : mail_date

mail_type
---------
Product = imio.dms.mail, FieldIndex

Used on
    * IContentish : mail_type
    * IDmsPerson : userid
    * IHeldPosition : parent userid
    * ITaskContent : enquirer

markers
-------
Product = imio.dms.mail, KeywordIndex

Used on IImioDmsIncomingMail : "hasResponse"
Used on IImioDmsOutgoingMail : "lastDmsFileIsOdt"

organization_type
-----------------
Product = imio.dms.mail, FieldIndex

Used on
    * IContentish : organization_type
    * IImioDmsIncomingMail : reception_date (in sec)
    * IImioDmsOutgoingMail : outgoing_date (in sec)

recipient_groups
----------------
Product = collective.dms.basecontent, KeywordIndex

Used on IItem : recipient_groups

recipients_index
----------------
Product = collective.dms.mailcontent, KeywordIndex

Used on IDmsDocument : recipients

Stores a list of:
    * recipients UIDs
    * organizations chain UIDs if the recipient is an organization or a
      held position, prefixed by 'l:'

scan_id
-------
Product = collective.dms.scanbehavior, FieldIndex

Used on IScanFields : scan_id

sender_index
------------
Product = collective.dms.mailcontent, KeywordIndex

Used on IDmsDocument : sender

Stores a list of:
    * recipients UIDs
    * organizations chain UIDs if the sender is an organization or a
      held position, prefixed by 'l:'

signed
------
Product = collective.dms.scanbehavior, BooleanIndex

Used on * : signed

state_group
-----------
Product = imio.dms.mail, FieldIndex

Used on IDmsDocument and ITaskContent.

Stores:
    * state,org_uid when validation is at org level
    * state only otherwise

Subject
-------
Product = Products.CMFPlone, KeywordIndex

Used on
    * IContentish : Subject
    * IImioDmsOutgoingMail : send_modes

treating_groups
---------------
Product = collective.dms.basecontent, KeywordIndex

Used on IItem : treating_groups


***************************
Usage for main portal types
***************************

dmsincomingmail, dmsincoming_email
----------------------------------
* assigned_group = creating_group
* assigned_user
* email = orig_sender_email
* external_reference_number = external_reference_no
* in_out_date = reception_date
* internal_reference_number = internal_reference_no
* labels
* mail_date = original_mail_date
* mail_type
* markers = "hasResponse"
* organization_type = reception_date (in sec)
* recipient_groups
* sender
* state_group
* treating_groups

dmsoutgoingmail
---------------
* assigned_group = creating_group
* assigned_user
* email = orig_sender_email
* enabled = "email is ready to be sent"
* external_reference_number = external_reference_no
* in_out_date = outgoing_date
* internal_reference_number = internal_reference_no
* mail_date
* mail_type
* markers = "lastDmsFileIsOdt"
* organization_type = outgoing_date (in sec)
* recipient_groups
* recipients_index = recipients
* sender
* state_group
* Subject = send_modes
* treating_groups

organization, person, held_position
-----------------------------------
* assigned_group = creating_group
* email
* internal_number
* mail_type = userid (person, held_position)
* organization_type

task
----
* assigned_group
* assigned_user
* mail_type = enquirer
* state_group

*********
Extenders
*********
