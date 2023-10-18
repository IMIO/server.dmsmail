*******
Schemas
*******

..
  bin/instance1 -Oc30-5 run docs/schemas.py

Fields Tables with:
    * field name (prefixed on behavior)
    * title (in french)
    * field class
    * value type, with extra informations:
        * 📌: indicates a link to another object
        * ❓: indicates a special content

dmsincomingmail (courrier entrant) & dmsincoming_email (email entrant)
----------------------------------------------------------------------

Parent: specific Folder /incoming-mail

.. list-table:: FIELDS
   :widths: 30 25 30 10 5
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
     - Default
   * - IClassificationFolder.classification_categories
     - Codes de classement
     - zope.schema._field.List
     - Choice (📌 **code de classement**)
     -
   * - IClassificationFolder.classification_folders
     - Dossiers
     - zope.schema._field.List
     - Choice (📌 **farde ou chemise**)
     -
   * - IDmsMailCreatingGroup.creating_group
     - Groupe indicateur
     - dexterity.localrolesfield.field.LocalRoleField
     - (📌 **service**)
     -
   * - IDublinCore.description
     - Description
     - zope.schema._bootstrapfields.Text
     -
     -
   * - IDublinCore.title
     - Titre
     - zope.schema._bootstrapfields.TextLine
     -
     -
   * - ITask.assigned_user
     - Utilisateur assigné
     - dexterity.localrolesfield.field.LocalRoleField
     - (📌 **utilisateur d'un groupe**)
     -
   * - ITask.due_date
     - Échéance
     - zope.schema._field.Date
     -
     -
   * - ITask.task_description
     - Description du travail
     - plone.app.textfield.RichText
     -
     -
   * - document_in_service
     - Le document original est dans le service
     - zope.schema._bootstrapfields.Bool
     -
     - Oui
   * - external_reference_no
     - Référence externe
     - zope.schema._bootstrapfields.TextLine
     -
     -
   * - internal_reference_no
     - Référence interne
     - zope.schema._bootstrapfields.TextLine
     - (❓ *référence interne spécifique*)
     - Oui
   * - mail_type
     - Type de courrier
     - zope.schema._field.Choice
     - (📌 **config: type**)
     -
   * - orig_sender_email
     - Email de l'expéditeur original
     - zope.schema._bootstrapfields.TextLine
     -
     -
   * - original_mail_date
     - Date du courrier
     - zope.schema._field.Date
     -
     - Oui
   * - reception_date
     - Date de réception
     - zope.schema._field.Datetime
     -
     - Oui
   * - recipient_groups
     - Services en copie
     - dexterity.localrolesfield.field.LocalRolesField
     - Choice (📌 **service**)
     -
   * - reply_to
     - Courriers liés
     - collective.dms.basecontent.relateddocs.RelatedDocs
     - RelationChoice (📌 **courrier entrant ou sortant**)
     -
   * - sender
     - Expéditeurs
     - collective.contact.widget.schema.ContactList
     - ContactChoice (📌 **contact**)
     -
   * - treating_groups
     - Service traitant
     - collective.task.field.LocalRoleMasterSelectField
     - (📌 **service**)
     -

dmsoutgoingmail (courrier sortant)
----------------------------------

Parent: specific Folder /outgoing-mail

.. list-table:: FIELDS
   :widths: 30 25 30 10 5
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
     - Default
   * - IClassificationFolder.classification_categories
     - Codes de classement
     - zope.schema._field.List
     - Choice (📌 **code de classement**)
     -
   * - IClassificationFolder.classification_folders
     - Dossiers
     - zope.schema._field.List
     - Choice (📌 **farde ou chemise**)
     -
   * - IDmsMailCreatingGroup.creating_group
     - Groupe indicateur
     - dexterity.localrolesfield.field.LocalRoleField
     - (📌 **service**)
     -
   * - IDublinCore.description
     - Description
     - zope.schema._bootstrapfields.Text
     -
     -
   * - IDublinCore.title
     - Titre
     - zope.schema._bootstrapfields.TextLine
     -
     -
   * - ITask.assigned_user
     - Utilisateur assigné
     - dexterity.localrolesfield.field.LocalRoleField
     - (📌 **utilisateur d'un groupe**)
     -
   * - ITask.due_date
     - Échéance
     - zope.schema._field.Date
     -
     -
   * - ITask.task_description
     - Description du travail
     - plone.app.textfield.RichText
     -
     -
   * - email_attachments
     - Pièces jointes
     - zope.schema._field.List
     - Choice (📌 **fichier ged ou annexe**)
     -
   * - email_body
     - Corps de l'email
     - plone.app.textfield.RichText
     -
     -
   * - email_cc
     - Emails des destinataires en copie
     - zope.schema._bootstrapfields.TextLine
     -
     -
   * - email_recipient
     - Emails des destinataires
     - zope.schema._bootstrapfields.TextLine
     -
     -
   * - email_sender
     - Email de l'expéditeur
     - zope.schema._bootstrapfields.TextLine
     -
     -
   * - email_status
     - Statut
     - zope.schema._bootstrapfields.TextLine
     -
     -
   * - email_subject
     - Sujet de l'email
     - zope.schema._bootstrapfields.TextLine
     -
     -
   * - external_reference_no
     - Référence externe
     - zope.schema._bootstrapfields.TextLine
     - (❓ *référence interne spécifique*)
     -
   * - internal_reference_no
     - Référence interne
     - zope.schema._bootstrapfields.TextLine
     -
     -
   * - mail_date
     - Date du courrier
     - zope.schema._field.Date
     -
     - Oui
   * - mail_type
     - Type de courrier
     - zope.schema._field.Choice
     - (📌 **config: type**)
     -
   * - orig_sender_email
     - Email de l'expéditeur original
     - zope.schema._bootstrapfields.TextLine
     -
     -
   * - outgoing_date
     - Date d'expédition
     - zope.schema._field.Datetime
     -
     -
   * - recipient_groups
     - Services en copie
     - dexterity.localrolesfield.field.LocalRolesField
     - Choice (📌 **service**)
     -
   * - recipients
     - Destinataires
     - collective.contact.widget.schema.ContactList
     - ContactChoice (📌 **contact**)
     -
   * - reply_to
     - Courriers liés
     - collective.dms.basecontent.relateddocs.RelatedDocs
     - RelationChoice (📌 **courrier**)
     -
   * - send_modes
     - Formes d'envoi
     - zope.schema._field.List
     - Choice (📌 **config: forme d'envoi**)
     -
   * - sender
     - Expéditeur
     - zope.schema._field.Choice
     - (📌 **fonction occupée interne**)
     -
   * - treating_groups
     - Service traitant
     - collective.task.field.LocalRoleMasterSelectField
     - (📌 **service**)
     -

dmsmainfile & dmsommainfile (fichier ged)
-----------------------------------------

Parent:
    * im or iem
    * om

.. list-table:: FIELDS
   :widths: 30 30 30 10
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
   * - IScanFields.pages_number
     - Nombre de pages
     - zope.schema._bootstrapfields.Int
     -
   * - IScanFields.scan_date
     - Date de scan
     - zope.schema._field.Datetime
     -
   * - IScanFields.scan_id
     - Identifiant de scan
     - zope.schema._bootstrapfields.TextLine
     -
   * - IScanFields.scan_user
     - Opérateur
     - zope.schema._bootstrapfields.TextLine
     -
   * - IScanFields.scanner
     - Scanner
     - zope.schema._bootstrapfields.TextLine
     -
   * - IScanFields.signed
     - Version signée
     - zope.schema._bootstrapfields.Bool
     -
   * - IScanFields.to_sign
     - À signer?
     - zope.schema._bootstrapfields.Bool
     -
   * - IScanFields.version
     - Version
     - zope.schema._bootstrapfields.Int
     -
   * - file
     - Fichier
     - plone.namedfile.field.NamedBlobFile
     -
   * - label
     - Intitulé
     - zope.schema._bootstrapfields.TextLine
     -
   * - title
     - Numéro de fichier ged
     - zope.schema._bootstrapfields.TextLine
     -

dmsappendixfile (annexe)
------------------------

Parent:
    * im or iem
    * om

.. list-table:: FIELDS
   :widths: 30 30 30 10
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
   * - IBasic.description
     - Description
     - zope.schema._bootstrapfields.Text
     -
   * - IBasic.title
     - Titre
     - zope.schema._bootstrapfields.TextLine
     -
   * - file
     - Fichier
     - plone.namedfile.field.NamedBlobFile
     -

directory (annuaire)
--------------------

Specific object /contacts

.. list-table:: FIELDS
   :widths: 30 30 30 10
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
   * - IBasic.description
     - Description
     - zope.schema._bootstrapfields.Text
     -
   * - IBasic.title
     - Titre
     - zope.schema._bootstrapfields.TextLine
     -
   * - organization_levels
     - Niveaux d'organisation
     - zope.schema._field.List
     - DictRow
   * - organization_types
     - Types d'organisations
     - zope.schema._field.List
     - DictRow
   * - position_types
     - Types de fonctions
     - zope.schema._field.List
     - DictRow

organization (organisation)
---------------------------

Parent:
    * directory /contacts
    * other organization

.. list-table:: FIELDS
   :widths: 30 30 30 10
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
   * - IBasic.description
     - Description
     - zope.schema._bootstrapfields.Text
     -
   * - IBasic.title
     - Titre
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.additional_address_details
     - Complément d'adresse
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.cell_phone
     - Téléphone portable
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.city
     - Ville
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.country
     - Pays
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.email
     - Courriel
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.fax
     - Fax
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.im_handle
     - Identifiant de messagerie instantanée
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.number
     - Numéro
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.parent_address
     -
     - plone.app.textfield.RichText
     -
   * - IContactDetails.phone
     - Téléphone
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.region
     - Région
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.street
     - Rue
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.use_parent_address
     - Utiliser l'adresse de l'entité d'appartenance
     - plone.formwidget.masterselect.MasterSelectBoolField
     -
   * - IContactDetails.website
     - Site web
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.zip_code
     - Code postal
     - zope.schema._bootstrapfields.TextLine
     -
   * - activity
     - Activité
     - plone.app.textfield.RichText
     -
   * - enterprise_number
     - Numéro d'entreprise (ou de TVA)
     - zope.schema._bootstrapfields.TextLine
     -
   * - logo
     - Logo
     - plone.namedfile.field.NamedImage
     -
   * - organization_type
     - Type ou niveau
     - zope.schema._field.Choice
     - (📌 **type ou niveau de l'annuaire**)

person (personne)
-----------------

Parent: directory /contacts

.. list-table:: FIELDS
   :widths: 30 30 30 10
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
   * - IBirthday.birthday
     - Date de naissance
     - zope.schema._field.Date
     -
   * - IContactDetails.additional_address_details
     - Complément d'adresse
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.cell_phone
     - Téléphone portable
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.city
     - Ville
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.country
     - Pays
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.email
     - Courriel
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.fax
     - Fax
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.im_handle
     - Identifiant de messagerie instantanée
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.number
     - Numéro
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.parent_address
     -
     - plone.app.textfield.RichText
     -
   * - IContactDetails.phone
     - Téléphone
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.region
     - Région
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.street
     - Rue
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.use_parent_address
     - Utiliser l'adresse de l'entité d'appartenance
     - plone.formwidget.masterselect.MasterSelectBoolField
     -
   * - IContactDetails.website
     - Site web
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.zip_code
     - Code postal
     - zope.schema._bootstrapfields.TextLine
     -
   * - firstname
     - Prénom
     - zope.schema._bootstrapfields.TextLine
     -
   * - gender
     - Genre
     - zope.schema._field.Choice
     -
   * - lastname
     - Nom de famille
     - zope.schema._bootstrapfields.TextLine
     -
   * - person_title
     - Civilité
     - zope.schema._bootstrapfields.TextLine
     -
   * - photo
     - Photo
     - plone.namedfile.field.NamedImage
     -
   * - signature
     - Signature
     - plone.namedfile.field.NamedImage
     -
   * - userid
     - Identifiant Plone
     - zope.schema._field.Choice
     - (📌 **utilisateur**)

held_position (fonction occupée)
--------------------------------

Parent: person

.. list-table:: FIELDS
   :widths: 30 30 30 10
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
   * - IContactDetails.additional_address_details
     - Complément d'adresse
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.cell_phone
     - Téléphone portable
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.city
     - Ville
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.country
     - Pays
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.email
     - Courriel
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.fax
     - Fax
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.im_handle
     - Identifiant de messagerie instantanée
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.number
     - Numéro
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.parent_address
     -
     - plone.app.textfield.RichText
     -
   * - IContactDetails.phone
     - Téléphone
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.region
     - Région
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.street
     - Rue
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.use_parent_address
     - Utiliser l'adresse de l'entité d'appartenance
     - plone.formwidget.masterselect.MasterSelectBoolField
     -
   * - IContactDetails.website
     - Site web
     - zope.schema._bootstrapfields.TextLine
     -
   * - IContactDetails.zip_code
     - Code postal
     - zope.schema._bootstrapfields.TextLine
     -
   * - end_date
     - Date de fin
     - zope.schema._field.Date
     -
   * - label
     - Intitulé de fonction
     - zope.schema._bootstrapfields.TextLine
     -
   * - photo
     - Photo
     - plone.namedfile.field.NamedImage
     -
   * - position
     - Organisation/Fonction
     - collective.contact.widget.schema.ContactChoice
     - (📌 **organisation**)
   * - start_date
     - Date de début
     - zope.schema._field.Date
     -

ClassificationCategory (code de classement)
-------------------------------------------

Parent: specific ClassificationContainer /tree

.. list-table:: FIELDS
   :widths: 30 30 30 10
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
   * - enabled
     - Activé
     - zope.schema._bootstrapfields.Bool
     -
   * - identifier
     - Identifiant
     - zope.schema._bootstrapfields.TextLine
     -
   * - informations
     - Informations
     - zope.schema._bootstrapfields.TextLine
     -
   * - title
     - Nom
     - zope.schema._bootstrapfields.TextLine
     -

ClassificationFolder (farde) & ClassificationSubfolder (chemise)
----------------------------------------------------------------

Parent:
    * specific ClassificationFolders /folders
    * ClassificationFolder

.. list-table:: FIELDS
   :widths: 30 30 30 10
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
   * - archived
     - Archivé
     - zope.schema._bootstrapfields.Bool
     -
   * - classification_categories
     - Codes de classement
     - zope.schema._field.List
     - Choice (📌 **code de classement**)
   * - classification_informations
     - Informations
     - zope.schema._bootstrapfields.Text
     -
   * - internal_reference_no
     - Identifiant unique
     - zope.schema._bootstrapfields.TextLine
     -
   * - recipient_groups
     - Services en copie
     - dexterity.localrolesfield.field.LocalRolesField
     - Choice (📌 **service**)
   * - title
     - Titre
     - zope.schema._bootstrapfields.TextLine
     -
   * - treating_groups
     - Service traitant
     - dexterity.localrolesfield.field.LocalRoleField
     - (📌 **service**)

task (tâche)
------------

Parent:
    * im or iem
    * om
    * task

.. list-table:: FIELDS
   :widths: 30 30 30 10
   :header-rows: 1

   * - Field name
     - Title
     - Class
     - Value type
   * - ITask.assigned_group
     - Groupe assigné
     - collective.task.field.LocalRoleMasterSelectField
     - (📌 **service**)
   * - ITask.assigned_user
     - Utilisateur assigné
     - dexterity.localrolesfield.field.LocalRoleField
     - (📌 **utilisateur d'un groupe**)
   * - ITask.due_date
     - Échéance
     - zope.schema._field.Date
     -
   * - ITask.enquirer
     - Service proposant
     - dexterity.localrolesfield.field.LocalRoleField
     - (📌 **service**)
   * - ITask.task_description
     - Description du travail
     - plone.app.textfield.RichText
     -
   * - parents_assigned_groups
     - Groupes assignés venant des tâches parentes
     - dexterity.localrolesfield.field.LocalRolesField
     - Choice (📌 **service**)
   * - parents_enquirers
     - Initiateurs venant des tâches parentes
     - dexterity.localrolesfield.field.LocalRolesField
     - Choice (📌 **service**)
   * - title
     - Titre
     - zope.schema._bootstrapfields.TextLine
     -
