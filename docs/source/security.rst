################
General security
################

Types:

* manual = manual local roles
* static = dx static local roles
* field = dx field local roles
* inherited = from parents

Roles:

* R = reader
* E = editor
* C = contributor
* R = reviewer
* WB = write base fields
* WT = write treating_groups field
* FC = DmsFile contributor

**************
Incoming mails
**************

incoming-mail folder
####################

+---------------------------+---------------+----------------+---------------------+
| States                    | Principal     | Roles          | Type                |
+===========================+===============+================+=====================+
|                           | encodeurs     | C,R            | manual              |
+---------------------------+---------------+----------------+---------------------+

dmsincomingmail
###############

__ac_local_roles_block__ = True

+---------------------+---------------------+----------------+---------------------+
| States              | Principal           | Roles          | Type                |
+=====================+=====================+================+=====================+
| created             | encodeurs           | E,C,WB,WT,FC   | static              |
+---------------------+---------------------+----------------+---------------------+
| proposed_to_manager | encodeurs           | R,WB           | static              |
+---------------------+---------------------+----------------+---------------------+
| proposed_to_manager | dir_general         | E,C,R,WB,WT    | static              |
+---------------------+---------------------+----------------+---------------------+
| proposed_to_manager | lecteurs_globaux_ce | R              | static              |
+---------------------+---------------------+----------------+---------------------+
| proposed_to_n_plus_1| encodeurs,          | R              | static              |
|                     | lecteurs_globaux_ce |                |                     |
+---------------------+---------------------+----------------+---------------------+
| proposed_to_n_plus_1| dir_general         | E,C,R,WB,WT    | static              |
+---------------------+---------------------+----------------+---------------------+
| proposed_to_agent   | encodeurs,          | R              | static              |
|                     | lecteurs_globaux_ce |                |                     |
+---------------------+---------------------+----------------+---------------------+
| proposed_to_agent   | dir_general         | E,C,R,WT       | static              |
+---------------------+---------------------+----------------+---------------------+
| in_treatment        | encodeurs,          | R              | static              |
|                     | lecteurs_globaux_ce |                |                     |
+---------------------+---------------------+----------------+---------------------+
| in_treatment        | dir_general         | E,C,R,WT       | static              |
+---------------------+---------------------+----------------+---------------------+
| closed              | encodeurs,          | R              | static              |
|                     | lecteurs_globaux_ce |                |                     |
+---------------------+---------------------+----------------+---------------------+
| closed              | dir_general         | E,C,R,WT       | static              |
+---------------------+---------------------+----------------+---------------------+
