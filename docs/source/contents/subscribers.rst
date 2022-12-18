***********
Subscribers
***********

Data transfer info:
    * ❓: to check following cases
    * ✅: to keep
    * ❌: to deactivate

collective.behavior.internalnumber.behavior.IInternalNumberBehavior
-------------------------------------------------------------------

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: collective.behavior.internalnumber.subscribers.object_added

collective.classification.folder.content.classification_folders.IClassificationFolders
--------------------------------------------------------------------------------------

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: collective.classification.folder.content.classification_folders.on_create

collective.classification.folder.content.classification_folder.IClassificationFolder
------------------------------------------------------------------------------------

* zope.lifecycleevent.IObjectModifiedEvent

  * .. autofunction:: collective.classification.folder.content.classification_folder.on_modify

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: collective.classification.folder.content.classification_folder.on_create

* zope.lifecycleevent.interfaces.IObjectMovedEvent

  * .. autofunction:: collective.classification.folder.content.classification_folder.on_move

* zope.lifecycleevent.interfaces.IObjectRemovedEvent

  * .. autofunction:: collective.classification.folder.content.classification_folder.on_delete

collective.classification.folder.content.classification_subfolder.IClassificationSubfolder
------------------------------------------------------------------------------------------

* zope.lifecycleevent.interfaces.IObjectMovedEvent

  * .. autofunction:: collective.classification.folder.content.classification_subfolder.on_move

collective.classification.tree.contents.container.IClassificationContainer
--------------------------------------------------------------------------

* zope.container.interfaces.IContainerModifiedEvent

  * .. autofunction:: collective.classification.tree.contents.container.container_modified

collective.classification.tree.contents.category.IClassificationCategory
------------------------------------------------------------------------

* zope.container.interfaces.IContainerModifiedEvent

  * .. autofunction:: collective.classification.tree.contents.category.container_modified

* zope.lifecycleevent.IObjectModifiedEvent

  * .. autofunction:: collective.classification.tree.contents.category.category_modified

* zope.lifecycleevent.interfaces.IObjectRemovedEvent

  * .. autofunction:: collective.classification.tree.contents.category.category_deleted

plone.app.relationfield.interfaces.IDexterityHasRelations
---------------------------------------------------------

* zope.lifecycleevent.interfaces.IObjectRemovedEvent

  * .. autofunction:: collective.contact.core.subscribers.referencedObjectRemoved

z3c.relationfield.interfaces.IHasIncomingRelations
--------------------------------------------------

* OFS.interfaces.IObjectWillBeRemovedEvent

  * .. autofunction:: collective.contact.core.subscribers.referenceRemoved

plone.registry.interfaces.IRecordModifiedEvent
----------------------------------------------

* UNCONFIGURE:

  * plone.registry.interfaces.IRecordModifiedEvent

    * .. autofunction:: imio.pm.wsclient.browser.settings.notify_configuration_changed

* plone.registry.interfaces.IRecordModifiedEvent

  * .. autofunction:: collective.contact.core.subscribers.recordModified

  * .. autofunction:: collective.contact.plonegroup.browser.settings.detectContactPlonegroupChange

  * .. autofunction:: imio.dms.mail.browser.settings.imiodmsmail_settings_changed

  * .. autofunction:: imio.dms.mail.subscribers.contact_plonegroup_change

  * .. autofunction:: imio.dms.mail.subscribers.user_related_modification

  * .. autofunction:: imio.dms.mail.subscribers.wsclient_configuration_changed

collective.contact.plonegroup.interfaces.IPloneGroupContact
-----------------------------------------------------------

* OFS.interfaces.IObjectWillBeRemovedEvent

  * .. autofunction:: collective.contact.plonegroup.subscribers.plonegroupOrganizationRemoved

* Products.DCWorkflow.interfaces.IBeforeTransitionEvent

  * .. autofunction:: collective.contact.plonegroup.subscribers.plonegroup_contact_transition

* zope.app.container.interfaces.IObjectMovedEvent

  * .. autofunction:: collective.contact.plonegroup.browser.settings.adaptPloneGroupDefinition

  * .. autofunction:: imio.dms.mail.subscribers.plonegroup_contact_changed

* zope.lifecycleevent.interfaces.IObjectModifiedEvent

  * .. autofunction:: collective.contact.plonegroup.browser.settings.adaptPloneGroupDefinition

  * .. autofunction:: imio.dms.mail.subscribers.plonegroup_contact_changed

* zope.lifecycleevent.interfaces.IObjectRemovedEvent

  * .. autofunction:: collective.contact.plonegroup.subscribers.referencedObjectRemoved

Products.PluggableAuthService.interfaces.events.IGroupDeletedEvent
------------------------------------------------------------------

* Products.PluggableAuthService.interfaces.events.IGroupDeletedEvent

  * .. autofunction:: collective.contact.plonegroup.subscribers.group_deleted

  * .. autofunction:: imio.helpers.events.onGroupDeleted

  * .. autofunction:: imio.dms.mail.subscribers.group_deleted

collective.contact.widget.interfaces.IContactContent
----------------------------------------------------

* UNCONFIGURE:

  * zope.lifecycleevent.interfaces.IObjectMovedEvent

    * .. autofunction:: collective.contact.plonegroup.subscribers.mark_organization

* Products.DCWorkflow.interfaces.IAfterTransitionEvent

  * .. autofunction:: imio.dms.mail.subscribers.contact_modified

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: imio.dms.mail.subscribers.contact_added

* zope.lifecycleevent.interfaces.IObjectModifiedEvent

  * .. autofunction:: imio.dms.mail.subscribers.contact_modified

* zope.lifecycleevent.interfaces.IObjectMovedEvent

  * .. autofunction:: collective.contact.plonegroup.subscribers.mark_organization

  * .. autofunction:: imio.dms.mail.subscribers.mark_contact

collective.dms.mailcontent.dmsmail.IDmsIncomingMail
---------------------------------------------------

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: collective.dms.mailcontent.dmsmail.incrementIncomingMailNumber

collective.dms.mailcontent.dmsmail.IDmsOutgoingMail
---------------------------------------------------

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: collective.dms.mailcontent.dmsmail.incrementOutgoingMailNumber

zope.interface.Interface
------------------------

* eea.facetednavigation.interfaces.IQueryWillBeExecutedEvent

  * .. autofunction:: collective.querynextprev.subscribers.record_query_in_session

collective.task.behaviors.ITask
-------------------------------

* UNCONFIGURE:

  * Products.DCWorkflow.interfaces.IAfterTransitionEvent

    * .. autofunction:: collective.task.subscribers.afterTransitionITaskSubscriber

* Products.DCWorkflow.interfaces.IAfterTransitionEvent

  * .. autofunction:: collective.task.subscribers.afterTransitionITaskSubscriber

collective.task.interfaces.ITaskContent
---------------------------------------

* Products.DCWorkflow.interfaces.IAfterTransitionEvent

  * .. autofunction:: imio.dms.mail.subscribers.task_transition

* zope.lifecycleevent.interfaces.IObjectModifiedEvent

  * .. autofunction:: collective.task.subscribers.taskContent_modified

* zope.lifecycleevent.interfaces.IObjectMovedEvent

  * .. autofunction:: collective.task.subscribers.taskContent_created

Products.PluggableAuthService.interfaces.events.IPrincipalCreatedEvent
----------------------------------------------------------------------

* Products.PluggableAuthService.interfaces.events.IPrincipalCreatedEvent

  * .. autofunction:: imio.helpers.events.onPrincipalCreated

Products.PluggableAuthService.interfaces.events.IPrincipalDeletedEvent
----------------------------------------------------------------------

* Products.PluggableAuthService.interfaces.events.IPrincipalDeletedEvent

  * .. autofunction:: imio.helpers.events.onPrincipalDeleted

  * .. autofunction:: imio.dms.mail.subscribers.user_deleted

Products.PluggableAuthService.interfaces.events.IPropertiesUpdatedEvent
-----------------------------------------------------------------------

* Products.PluggableAuthService.interfaces.events.IPropertiesUpdatedEvent

  * .. autofunction:: imio.helpers.events.onPrincipalModified

Products.PluggableAuthService.interfaces.events.IPrincipalAddedToGroupEvent
---------------------------------------------------------------------------

* UNCONFIGURE:

  * Products.PluggableAuthService.interfaces.events.IPrincipalAddedToGroupEvent

    * .. autofunction:: imio.helpers.events.onPrincipalAddedToGroup

* Products.PluggableAuthService.interfaces.events.IPrincipalAddedToGroupEvent

  * .. autofunction:: imio.helpers.events.onPrincipalAddedToGroup

  * .. autofunction:: imio.dms.mail.subscribers.group_assignment

Products.PluggableAuthService.interfaces.events.IPrincipalRemovedFromGroupEvent
-------------------------------------------------------------------------------

* UNCONFIGURE:

  * Products.PluggableAuthService.interfaces.events.IPrincipalRemovedFromGroupEvent

    * .. autofunction:: imio.helpers.events.onPrincipalRemovedFromGroup

* Products.PluggableAuthService.interfaces.events.IPrincipalRemovedFromGroupEvent

  * .. autofunction:: imio.helpers.events.onPrincipalRemovedFromGroup

  * .. autofunction:: imio.dms.mail.subscribers.group_unassignment

Products.PluggableAuthService.interfaces.events.IGroupCreatedEvent
------------------------------------------------------------------

* Products.PluggableAuthService.interfaces.events.IGroupCreatedEvent

  * .. autofunction:: imio.helpers.events.onGroupCreated

plone.dexterity.interfaces.IDexterityContent
--------------------------------------------

* OFS.interfaces.IObjectWillBeMovedEvent

  * .. autofunction:: dexterity.localroles.subscriber.related_change_on_moving

  * .. autofunction:: dexterity.localrolesfield.subscriber.related_change_on_moving

* Products.CMFCore.interfaces.IActionSucceededEvent

  * .. autofunction:: collective.documentviewer.subscribers.handle_workflow_change

* Products.DCWorkflow.interfaces.IAfterTransitionEvent

  * .. autofunction:: dexterity.localroles.subscriber.related_change_on_transition

  * .. autofunction:: dexterity.localrolesfield.subscriber.related_change_on_transition

  * .. autofunction:: imio.dms.mail.subscribers.dexterity_transition

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: collective.documentviewer.subscribers.handle_file_creation

  * .. autofunction:: dexterity.localroles.subscriber.related_change_on_addition

  * .. autofunction:: dexterity.localrolesfield.subscriber.related_change_on_addition

* zope.lifecycleevent.interfaces.IObjectModifiedEvent

  * .. autofunction:: collective.documentviewer.subscribers.handle_file_creation

  * .. autofunction:: dexterity.localrolesfield.subscriber.object_modified

* zope.lifecycleevent.interfaces.IObjectMovedEvent

  * .. autofunction:: dexterity.localroles.subscriber.related_change_on_moved

  * .. autofunction:: dexterity.localrolesfield.subscriber.related_change_on_moved

* zope.lifecycleevent.interfaces.IObjectRemovedEvent

  * .. autofunction:: dexterity.localroles.subscriber.related_change_on_removal

  * .. autofunction:: dexterity.localrolesfield.subscriber.related_change_on_removal

dexterity.localroles.browser.interfaces.ILocalRoleListUpdatedEvent
------------------------------------------------------------------

* UNCONFIGURE:

  * dexterity.localroles.browser.interfaces.ILocalRoleListUpdatedEvent

    * .. autofunction:: dexterity.localroles.subscriber.local_role_related_configuration_updated

* dexterity.localroles.browser.interfaces.ILocalRoleListUpdatedEvent

  * .. autofunction:: dexterity.localroles.subscriber.local_role_related_configuration_updated

  * .. autofunction:: dexterity.localrolesfield.subscriber.local_role_related_configuration_updated

plone.dexterity.interfaces.IDexterityFTI
----------------------------------------

* zope.lifecycleevent.interfaces.IObjectModifiedEvent

  * .. autofunction:: dexterity.localrolesfield.subscriber.fti_modified

z3c.relationfield.interfaces.IHasOutgoingRelations
--------------------------------------------------

* UNCONFIGURE:

  * zope.app.container.interfaces.IObjectRemovedEvent

    * .. autofunction:: z3c.relationfield.event.removeRelations

  * zope.lifecycleevent.IObjectModifiedEvent

    * .. autofunction:: z3c.relationfield.event.updateRelations

* zope.app.container.interfaces.IObjectRemovedEvent

  * .. autofunction:: imio.dms.mail.subscribers.remove_relations

* zope.lifecycleevent.IObjectModifiedEvent

  * .. autofunction:: imio.dms.mail.subscribers.update_relations

OFS.interfaces.IItem
--------------------

* OFS.interfaces.IObjectWillBeMovedEvent

  * .. autofunction:: imio.dms.mail.subscribers.item_moved

* zope.lifecycleevent.IObjectAddedEvent

  * .. autofunction:: imio.dms.mail.subscribers.item_added

* zope.lifecycleevent.IObjectCopiedEvent

  * .. autofunction:: imio.dms.mail.subscribers.item_copied

collective.dms.basecontent.dmsdocument.IDmsDocument
---------------------------------------------------

* OFS.interfaces.IObjectWillBeRemovedEvent

  * .. autofunction:: imio.dms.mail.subscribers.reference_document_removed

* Products.DCWorkflow.interfaces.IAfterTransitionEvent

  * .. autofunction:: imio.dms.mail.subscribers.dmsdocument_transition

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: imio.dms.mail.subscribers.dmsdocument_added

* zope.lifecycleevent.interfaces.IObjectModifiedEvent

  * .. autofunction:: imio.dms.mail.subscribers.dmsdocument_modified

imio.dms.mail.dmsmail.IImioDmsIncomingMail
------------------------------------------

* Products.DCWorkflow.interfaces.IAfterTransitionEvent

  * .. autofunction:: imio.dms.mail.subscribers.dmsincomingmail_transition

* plone.dexterity.interfaces.IEditFinishedEvent

  * .. autofunction:: imio.dms.mail.subscribers.im_edit_finished

imio.dms.mail.dmsmail.IImioDmsOutgoingMail
------------------------------------------

* Products.DCWorkflow.interfaces.IAfterTransitionEvent

  * .. autofunction:: imio.dms.mail.subscribers.dmsoutgoingmail_transition

collective.dms.basecontent.dmsfile.IDmsAppendixFile
---------------------------------------------------

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: imio.dms.mail.subscribers.dmsappendixfile_added

collective.dms.basecontent.dmsfile.IDmsFile
-------------------------------------------

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: imio.dms.mail.subscribers.dmsmainfile_added

* zope.lifecycleevent.interfaces.IObjectModifiedEvent

  * .. autofunction:: imio.dms.mail.subscribers.dmsmainfile_modified

imio.dms.mail.dmsfile.IImioDmsFile
----------------------------------

* collective.documentviewer.interfaces.IConversionFinishedEvent

  * .. autofunction:: imio.dms.mail.subscribers.conversion_finished

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: imio.dms.mail.subscribers.imiodmsfile_added

imio.dms.mail.interfaces.IMemberAreaFolder
------------------------------------------

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: imio.dms.mail.subscribers.member_area_added

Products.ATContentTypes.interfaces.folder.IATFolder
---------------------------------------------------

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: imio.dms.mail.subscribers.folder_added

plone.app.controlpanel.interfaces.IConfigurationChangedEvent
------------------------------------------------------------

* UNCONFIGURE:

  * plone.app.controlpanel.interfaces.IConfigurationChangedEvent

    * .. autofunction:: imio.pm.wsclient.browser.settings.notify_configuration_changed

* plone.app.controlpanel.interfaces.IConfigurationChangedEvent

  * .. autofunction:: imio.dms.mail.subscribers.user_related_modification

  * .. autofunction:: imio.dms.mail.subscribers.wsclient_configuration_changed

collective.contact.core.content.organization.IOrganization
----------------------------------------------------------

* zope.lifecycleevent.interfaces.IObjectModifiedEvent

  * .. autofunction:: imio.dms.mail.subscribers.organization_modified

* zope.lifecycleevent.interfaces.IObjectMovedEvent

  * .. autofunction:: imio.dms.mail.subscribers.organization_modified

collective.contact.contactlist.interfaces.IContactList
------------------------------------------------------

* zope.lifecycleevent.interfaces.IObjectAddedEvent

  * .. autofunction:: imio.dms.mail.subscribers.contact_added

* zope.lifecycleevent.interfaces.IObjectMovedEvent

  * .. autofunction:: imio.dms.mail.subscribers.mark_contact

imio.dms.mail.interfaces.IPersonnelContact
------------------------------------------

* OFS.interfaces.IObjectWillBeRemovedEvent

  * .. autofunction:: imio.dms.mail.subscribers.personnel_contact_removed

collective.ckeditortemplates.cktemplate.ICKTemplate
---------------------------------------------------

* zope.lifecycleevent.interfaces.IObjectMovedEvent

  * .. autofunction:: imio.dms.mail.subscribers.cktemplate_moved

zope.processlifetime.IProcessStarting
-------------------------------------

* zope.processlifetime.IProcessStarting

  * .. autofunction:: imio.dms.mail.subscribers.zope_ready
