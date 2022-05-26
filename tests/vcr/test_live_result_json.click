result: '{"created": "2022-05-26T19:41:33.797898", "detections": {"benign": 0, "malicious":
  1, "total": 1}, "download_url": "http://minio:9000/cache-public/27/5a/02/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f3395856ce81f2b7382dee72602f798b642f1414044d88612fea8a8f36de82e1278abb02f?response-content-disposition=attachment%3Bfilename%3Dinfected&response-content-type=application%2Foctet-stream&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIOSFODNN7EXAMPLE%2F20220526%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220526T194531Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=b31ec7308335475cdbe4422f77d68cdb13a7bca1991c326639c246d904085211",
  "id": "11704609705052856", "instance_id": "99734963618630386", "livescan_id": "51856636346307547",
  "malware_family": null, "polyscore": 0.23213458159978606, "rule_name": "eicar_substring_test",
  "sha256": "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f", "tags":
  "{}", "yara": "rule eicar_av_test {\n    /*\n       Per standard, match only if
  entire file is EICAR string plus optional trailing whitespace.\n       The raw EICAR
  string to be matched is:\n       X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*\n    */\n\n    meta:\n        description
  = \"This is a standard AV test, intended to verify that BinaryAlert is working correctly.\"\n        author
  = \"Austin Byers | Airbnb CSIRT\"\n        reference = \"http://www.eicar.org/86-0-Intended-use.html\"\n\n    strings:\n        $eicar_regex
  = /^X5O!P%@AP\\[4\\\\PZX54\\(P\\^\\)7CC\\)7\\}\\$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!\\$H\\+H\\*\\s*$/\n\n    condition:\n        all
  of them\n}\n\nrule eicar_substring_test {\n    /*\n       More generic - match just
  the embedded EICAR string (e.g. in packed executables, PDFs, etc)\n    */\n\n    meta:\n        description
  = \"Standard AV test, checking for an EICAR substring\"\n        author = \"Austin
  Byers | Airbnb CSIRT\"\n\n    strings:\n        $eicar_substring = \"$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!\"\n\n    condition:\n        all
  of them\n}"}

  '
