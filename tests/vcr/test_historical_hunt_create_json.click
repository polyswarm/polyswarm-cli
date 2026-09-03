result: '{"account_number": "111", "archives_in_flight": 0, "archives_scanned": 0,
  "archives_total": 0, "communities": ["gamma"], "created": "2026-08-25T18:27:00.017968+00:00",
  "failed_max_retries": 0, "failed_other": 0, "id": "58957063950682201", "progress":
  null, "results_csv_uri": null, "rule_id": null, "rule_modified": null, "ruleset_name":
  "eicar.yara", "source_rule_changed": null, "status": "PENDING", "summary": null,
  "user_account_number": "111", "yara": "rule eicar_av_test : eicar match {\n    /*\n       Per
  standard, match only if entire file is EICAR string plus optional trailing whitespace.\n       The
  raw EICAR string to be matched is:\n       X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*\n    */\n\n    meta:\n        description
  = \"This is a standard AV test, intended to verify that BinaryAlert is working correctly.\"\n        author
  = \"Austin Byers | Airbnb CSIRT\"\n        reference = \"http://www.eicar.org/86-0-Intended-use.html\"\n\n    strings:\n        $eicar_regex
  = /^X5O!P%@AP\\[4\\\\PZX54\\(P\\^\\)7CC\\)7\\}\\$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!\\$H\\+H\\*\\s*$/\n\n    condition:\n        all
  of them\n}\n\nrule eicar_substring_test : eicar substring {\n    /*\n       More
  generic - match just the embedded EICAR string (e.g. in packed executables, PDFs,
  etc)\n    */\n\n    meta:\n        description = \"Standard AV test, checking for
  an EICAR substring\"\n        author = \"Austin Byers | Airbnb CSIRT\"\n\n    strings:\n        $eicar_substring
  = \"$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!\"\n\n    condition:\n        all of them\n}"}

  '
