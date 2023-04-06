######################
Data transfer pipeline
######################


**********************************
Main steps order to create content
**********************************

#. (Part a) Organization (service). Mapping to be done with actual service. Can be deactivated service (prefixed).
   Found in:

    * dmsincomingmail & dmsincoming_email (treating_groups, recipient_groups, creating_group)
    * dmsoutgoingmail (treating_groups, recipient_groups, creating_group)
    * held_position (position)
    * ClassificationFolder & ClassificationSubfolder (recipient_groups, treating_groups)
    * task (assigned_group, enquirer, parents_assigned_groups, parents_enquirers)

#. (Part b) Configuration:

    * mail_types (dmsincomingmail mail_type)
    * omail_types (dmsoutgoingmail mail_type)
    * omail_send_modes (dmsoutgoingmail send_modes)

#. (Part c) User. Mapping to be done with actual user. Can be deactivated user (prefixed). Must be mandatory put in group ❓

    * dmsincomingmail & dmsincoming_email (assigned_user)
    * dmsoutgoingmail (assigned_user)
    * person (userid)
    * task (assigned_user)

#. (Part d) held_position (in personnel)

    * dmsoutgoingmail (sender)

#. (Part e) ClassificationCategory (code de classement)

    * dmsincomingmail & dmsincoming_email (classification_categories)
    * dmsoutgoingmail (classification_categories)
    * ClassificationFolder (classification_categories)
    * ClassificationSubfolder (classification_categories)

#. (Part f) ClassificationFolder (farde)

    * dmsincomingmail & dmsincoming_email (classification_folders)
    * dmsoutgoingmail (classification_folders)

#. (Part g) ClassificationSubfolder (chemise)

    * dmsincomingmail & dmsincoming_email (classification_folders)
    * dmsoutgoingmail (classification_folders)

#. (Part h) directory (organization_types, organization_levels)

    * organization (organization_type)

#. (Part i) Contact (organization, person, held_position)

    * dmsincomingmail & dmsincoming_email (sender)
    * dmsoutgoingmail (recipients, sender)

#. (Part l) dmsincomingmail & dmsincoming_email
#. (Part p) dmsoutgoingmail
#. (Part t) dmsmainfile (in im and iem)
#. (Part u) dmsommainfile (in om)
#. (Part v) dmsappendixfile
#. (Part w) dmsoutgoingmail email_attachments
#. (Part x) Relations between im and om (reply_to)
#. (Part y) tasks ❓

*******************
Points of attention
*******************

* checks if internalnumber is activated and if a default value is needed (must the counter be increased ?).
* tree: caching.invalidate_cache("collective.classification.tree.utils.iterate_over_tree", container.UID())
* contact: reindex all contacts after creation: hp before person,