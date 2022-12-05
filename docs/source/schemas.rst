#######
Schemas
#######

..
  bin/instance1 -Oc30-5 run scripts/schemas.py

**************************************************
dmsincomingmail (courrier entrant & email entrant)
**************************************************

.. list-table:: FIELDS
   :widths: 30 30 30 10
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
   * - IClassificationFolder.classification_categories
     - Codes de classement
     - zope.schema._field.List
     - Choice
   * - IClassificationFolder.classification_folders
     - Dossiers
     - zope.schema._field.List
     - Choice
   * - IDmsMailCreatingGroup.creating_group
     - Groupe indicateur
     - dexterity.localrolesfield.field.LocalRoleField
     -
   * - IDublinCore.description
     - Description
     - zope.schema._bootstrapfields.Text
     -
   * - IDublinCore.title
     - Titre
     - zope.schema._bootstrapfields.TextLine
     -
   * - ITask.assigned_user
     - Utilisateur assigné
     - dexterity.localrolesfield.field.LocalRoleField
     -
   * - ITask.due_date
     - Échéance
     - zope.schema._field.Date
     -
   * - ITask.task_description
     - Description du travail
     - plone.app.textfield.RichText
     -
   * - document_in_service
     - Le document original est dans le service
     - zope.schema._bootstrapfields.Bool
     -
   * - external_reference_no
     - Référence externe
     - zope.schema._bootstrapfields.TextLine
     -
   * - internal_reference_no
     - Référence interne
     - zope.schema._bootstrapfields.TextLine
     -
   * - mail_type
     - Type de courrier
     - zope.schema._field.Choice
     -
   * - orig_sender_email
     - Email de l'expéditeur original
     - zope.schema._bootstrapfields.TextLine
     -
   * - original_mail_date
     - Date du courrier
     - zope.schema._field.Date
     -
   * - reception_date
     - Date de réception
     - zope.schema._field.Datetime
     -
   * - recipient_groups
     - Services en copie
     - dexterity.localrolesfield.field.LocalRolesField
     - Choice
   * - reply_to
     - Courriers liés
     - collective.dms.basecontent.relateddocs.RelatedDocs
     - RelationChoice
   * - sender
     - Expéditeurs
     - collective.contact.widget.schema.ContactList
     - ContactChoice
   * - treating_groups
     - Service traitant
     - collective.task.field.LocalRoleMasterSelectField
     -

**********************************
dmsoutgoingmail (courrier sortant)
**********************************

.. list-table:: FIELDS
   :widths: 30 30 30 10
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
   * - IClassificationFolder.classification_categories
     - Codes de classement
     - zope.schema._field.List
     - Choice
   * - IClassificationFolder.classification_folders
     - Dossiers
     - zope.schema._field.List
     - Choice
   * - IDmsMailCreatingGroup.creating_group
     - Groupe indicateur
     - dexterity.localrolesfield.field.LocalRoleField
     -
   * - IDublinCore.description
     - Description
     - zope.schema._bootstrapfields.Text
     -
   * - IDublinCore.title
     - Titre
     - zope.schema._bootstrapfields.TextLine
     -
   * - ITask.assigned_user
     - Utilisateur assigné
     - dexterity.localrolesfield.field.LocalRoleField
     -
   * - ITask.due_date
     - Échéance
     - zope.schema._field.Date
     -
   * - ITask.task_description
     - Description du travail
     - plone.app.textfield.RichText
     -
   * - email_attachments
     - Pièces jointes
     - zope.schema._field.List
     - Choice
   * - email_body
     - Corps de l'email
     - plone.app.textfield.RichText
     -
   * - email_cc
     - Emails des destinataires en copie
     - zope.schema._bootstrapfields.TextLine
     -
   * - email_recipient
     - Emails des destinataires
     - zope.schema._bootstrapfields.TextLine
     -
   * - email_sender
     - Email de l'expéditeur
     - zope.schema._bootstrapfields.TextLine
     -
   * - email_status
     - Statut
     - zope.schema._bootstrapfields.TextLine
     -
   * - email_subject
     - Sujet de l'email
     - zope.schema._bootstrapfields.TextLine
     -
   * - external_reference_no
     - Référence externe
     - zope.schema._bootstrapfields.TextLine
     -
   * - internal_reference_no
     - Référence interne
     - zope.schema._bootstrapfields.TextLine
     -
   * - mail_date
     - Date du courrier
     - zope.schema._field.Date
     -
   * - mail_type
     - Type de courrier
     - zope.schema._field.Choice
     -
   * - orig_sender_email
     - Email de l'expéditeur original
     - zope.schema._bootstrapfields.TextLine
     -
   * - outgoing_date
     - Date d'expédition
     - zope.schema._field.Datetime
     -
   * - recipient_groups
     - Services en copie
     - dexterity.localrolesfield.field.LocalRolesField
     - Choice
   * - recipients
     - Destinataires
     - collective.contact.widget.schema.ContactList
     - ContactChoice
   * - reply_to
     - Courriers liés
     - collective.dms.basecontent.relateddocs.RelatedDocs
     - RelationChoice
   * - send_modes
     - Formes d'envoi
     - zope.schema._field.List
     - Choice
   * - sender
     - Expéditeur
     - zope.schema._field.Choice
     -
   * - treating_groups
     - Service traitant
     - collective.task.field.LocalRoleMasterSelectField
     -
