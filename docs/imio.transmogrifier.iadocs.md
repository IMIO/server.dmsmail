# imio.transmogrifier.iadocs

Data retrieval / migration package (`parts/omelette/imio/transmogrifier/iadocs`,
source: `src/imio.transmogrifier.iadocs`).
Imports legacy DMS data (services, users, mail types, classification, contacts, IM/OM mails,
files, links) into an ia.docs Plone site through a transmogrifier pipeline.

Reference docs (more detail, kept up to date separately):
`src/imio.transmogrifier.iadocs/docs/source/` — `pipeline_data_transfer.rst` (part-by-part content
mapping), `indexes.rst`, `security.rst`. Blueprint parameters are documented in the class docstrings
of `blueprints/{main,various,csv_files,handlers}.py` (also exposed via sphinx `automodule`).

**When working in a claude terminal, always ask which pipeline file is used (when not given).**

## Run

```
env FUNC_PART=a bin/instance-debug -O<plone_site> run \
    parts/omelette/imio/transmogrifier/iadocs/execute_pipeline.py <pipeline.cfg> -c0
```

- `-c/--commit` `0|1`: commit the transaction at the end (default 0 = dry run).
- `-p/--parts`: extra parts to run (letters, e.g. `abc`).
- Env vars read by `execute_pipeline.py`: `FUNC_PART` (the main part, mandatory in practice),
  `BATCH` (max items per run, 0 = all), `COMMIT` (commit every n items).
- `auto_parts()` resolves `FUNC_PART` into the full part set by reading the `need_other`
  section declared for that part (`parts = ...`), then checks it against `config:permitted_sections`.
  So you never list dependencies by hand: `FUNC_PART=l` pulls `abce` in automatically.
- Options end up in `storage` as `parts`, `commit`, `commit_nb`, `batch_nb`.

## Pipeline files

Base pipelines live in the package root, one per source application:
`data-transfer.cfg.1` / `.1b` / `.1c` (I8s variants), `.2` (A8e), `.3` (B7c), `.4` (E8o),
`.5E` / `.5S` (H3y in/out). Per-customer copies are in `pipelines/` (`data-transfer.cfg.1.col`, …)
and in the buildout root for the current instance (`data-transfer.cfg.colfontaine`,
`data-transfer.cfg.huy`).

Two mandatory sections: `[config]` (global options: `raise_on_error`, `none_value`, `creator`,
default dates/types, `permitted_sections`, behavior types to install) and `[transmogrifier]`
(the `pipeline` list). `[initialization]` sets the working paths (`basepath`/`subpath`,
`csvpath`, `filespath`) and builds `storage`.

## Section naming

`<parts>__<[variant_]name>` — everything before `__` is the **part letters** the section belongs to
(`get_related_parts()`), so `dm__1_contacts_read` runs for parts `d` and `m`.
Sections with no `__` (`constructor`, `schemaupdater`, `lastsection`, …) always run.
Parts are single chars, case-sensitive (`f` vs `F`, `E` vs `e`), and digits are valid parts too
(`0`, `1`).

The digit right after `__` is the **source variant** number, matching the `data-transfer.cfg.<n>`
suffix: `l__1_type_insert` is I8s-specific, `a__5_service_read` is H3y-specific. Sections without a
digit are generic. These variant sections are the ones to review/adapt per customer
(cf. `# CHANGE l__1_type_insert FOR EACH CUSTOMER`).

Parts are commented out with `#` or `;` in the `pipeline` list — very common, both to disable
optional steps and to keep customer variants around. Check whether a section is actually in the
pipeline before debugging it.

## Storage & item conventions

`storage` = annotation on the transmogrifier (`ANNOTATION_KEY`), also set as
`transmogrifier.storage` so it is reachable from any `condition` expression. Main keys:

- `wp`, `csvp`, `filesp`: working / csv / files paths
- `data`: the shared dicts, keyed by *bp_key* (`e_service`, `e_mail_i`, `e_folder`, `p_orgs_all`, …)
- `plone`: site info (`directory`, `directory_path`, `firstname_first`)
- `parts`, `commit`, `commit_nb`, `batch_nb`, `creation_date`
- `course`: per-section item counters, printed at the end by `last_section`
- `lastsection.pkl_dump`: pickles to dump at the end

Item keys use a leading underscore for pipeline metadata: `_bpk` (which blueprint/csv produced it),
`_eid` (external id), `_id`, `_type` (portal_type), `_path`, `_parent`, `_act` (`U` = update),
`_error` (set by `utils.log_error`), `_fs_path`, `_filename`. `e_*` prefixes = external (source) data,
`p_*` = existing Plone data.

Condition option naming is consistent across blueprints: `b_condition` = evaluated once at
blueprint construction (skip the whole section), `condition` = per item, `d_condition` = dump
condition (`pickle_data`). `imio.transmogrifier.iadocs.condition` takes `condition1` (does this
section apply) + `condition2` (keep the item) — that is how the `*_only` and `*_batched`
sections work.

## Files in the imports dir (`csvpath`)

Numeric prefixes are a convention:

- `0_*.csv`: written by the pipeline — current Plone content (`0_imio_service.csv`) and
  match templates to be completed by hand (`0_service_match.csv`)
- `1_*.csv`: the completed mapping files, read back on the next run (`1_service_match.csv`).
  A section's `b_condition` usually tests the existence of the `1_` file to decide between
  "produce the template" and "use the mapping".
- `*.csv`: raw source exports (`eServices.csv`, `eCourriers.csv`, …)
- `2_*.pkl` / `2_*.csv` / `2_*.txt`: caches passed between parts (`pickle_data`), e.g.
  `2_e_mail_i.pkl` written by part `l` and read by parts `m`, `t`, `x`, `y`
- `3_*.csv`: manually provided extra input (`3_folder_created.csv`, `3_meeting_item.csv`)

Logs are written in imports folder: `<site>_dt.log`, `<site>_dt_input_errors.log`
(+ `_commit` variants when `-c1`), from the `dt`/`dti`/`dto` loggers.

## Parts

a) Mapping on organizations (services).
b) Mapping on mail types and send modes.
c) Mapping on users.
d) Create internal held positions to be used as sender on outgoing mail.
e) Import classification categories.
f) Import classification folders (`F` = already created folders variant).
h) Configure contacts directory (organization types/levels).
i) Import contacts in directory (optional).
l) Import dmsincomingmail & dmsincoming_email.
m) Import dmsincomingmail & dmsincoming_email recipients.
p) Import dmsoutgoingmail.
q) Import dmsoutgoingmail recipients.
r) Import dmsoutgoingmail recipient_groups.
s) Import classification_folders assignments on mails.
t) Import dmsmainfile (in im and iem).
u) Import dmsommainfile (in om).
w) Create links for meeting items (for another tool).
x) Create relations between im and om (reply_to).
y) Correct dates on created objects.
0/1) Utility parts: file listing on disk (`0`) and rsync file generation (`1`).

## Blueprint families (~60, all namespaced `imio.transmogrifier.iadocs.*`)

- **csv_files.py**: `csv_reader`, `csv_writer`
- **main.py** (generic plumbing): `init`, `store_in_data`, `read_from_data`, `add_data_in_item`,
  `pickle_data`, `common_input_checks`, `dependency_sorter`, `path_insert`, `parent_path_insert`,
  `files_list`, `state_set`, `owner_set`, `last_section`
- **various.py** (flow control / debug): `condition`, `inserter`, `manipulator`, `count`,
  `need_other`, `filter_item`, `item_field_split`, `replace_variables`, `short_log`, `print_item`,
  `stop`, `breakpoint`, `time_display`
- **handlers.py** (business logic, one per part/step): `a_service_update`, `b_mailtype_update`,
  `d_personnel_creation`, `e_category_update`, `f_*`, `h_contact_type_update`, `i_*_contact_update`,
  `l_*`, `m_1_assigned_user`, `p_om_sender_set`, `q_*`, `r_*`, `s_*`, `t_1_dmsfile_creation`,
  `x_1_reply_to_update`, `contact_set`, `contact_as_text_update`, `post_actions`, `rsync_writer`,
  `xml_contact_store`, `workflow_history_update`
- Standard transmogrifier sections are used for the creation tail: `constructor`, `schemaupdater`,
  `datesupdater`, `uidupdater`, `reindexobject`.

`utils.py` holds the helpers called from cfg expressions — most notably
`is_in_part(transmogrifier, 'l')`, used in nearly every `condition`, plus
`get_plonegroup_orgs`, `get_personnel`, `get_mailtypes`, `get_categories`, `get_folders`,
`get_file_content`, `log_error`.

## Side effects to know about

`init` / `last_section` mutate site configuration: install and configure
`collective.behavior.internalnumber`, add the `IDmsMailDataTransfer` behavior, disable
documentviewer auto-convert during file parts (`tuv`) and re-enable it at the end, disable
versioning, and clear cron jobs on an archive site. A pipeline interrupted mid-run can leave
those in the intermediate state.
