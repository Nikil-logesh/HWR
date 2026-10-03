# Refresh

`SnapshotStore` (SQLite) keeps every distinct profile state; an identical rerun updates the latest row's check
dates instead of adding a duplicate. `apply_refresh(previous, fresh, now)` (pure) stamps claims and emits `changes[]`.

* unchanged value: `first_observed_at` kept, `last_checked_at` = now, no change event
* changed / added / removed: event in the kit's change schema (`organisation_number, field, old_value, new_value,
  source_url, retrieved_at, effective_at, source_class, old/new_content_sha256, status`) plus `change_type`,
  `material`, `detected_at`, `previous_run_id`, old/new reporting periods and, for lists, `detail.added/removed`
* material: status, legal name, registered address, legal form, official website, roles, deleted registry record,
  new filing / restated figures
* jobs and news are volatile: even when the homepage hash is unchanged, the careers and news/feed pages are re-fetched
  on every run (only the static web facts and the LLM call are skipped); changes are typed `new_job_posting`,
  `closed_job`, `job_postings_changed`, `new_activity`, `hiring_status_change`, `careers_page_change` (not material)
* change types: status_change, name_change, address_change, legal_form_change, role_change, website_change,
  new_filing, financials_restated, registry_record_change, workplace_change, employees_change, field_added/removed
* a failed or blocked source never erases a supported value: it is carried forward (`carried_forward=true`, note,
  `errors[].kind=carried_forward`) and its `last_checked_at` is NOT bumped
* unchanged sources are skipped cheaply: if the homepage content hash equals the last verified run, secondary
  pages and the LLM call are skipped and the verified web claims are reused
* the Brreg entity endpoint sends no ETag, so register freshness is detected by diffing values / content hashes;
  the Brreg update feed was not used because it lists every change in the register, which costs more than re-reading
  the batch's own companies

Run with a prior state: `--previous <envelopes.jsonl>` (CLI, Phase 6) or a persistent `--store` SQLite file.
