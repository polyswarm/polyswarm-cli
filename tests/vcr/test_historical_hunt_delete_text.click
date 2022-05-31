result: "Successfully deleted Hunt:\nHunt Id: 96916002705221564\nStatus: DELETING\n\
  Created at: 2022-05-26 19:08:30.323397\nRuleset Name: eicar.yara\nRuleset Contents:\n\
  rule eicar_av_test {\n    /*\n       Per standard, match only if entire file is\
  \ EICAR string plus optional trailing whitespace.\n       The raw EICAR string to\
  \ be matched is:\n       X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*\n\
  \    */\n\n    meta:\n        description = \"This is a standard AV test, intended\
  \ to verify that BinaryAlert is working correctly.\"\n        author = \"Austin\
  \ Byers | Airbnb CSIRT\"\n        reference = \"http://www.eicar.org/86-0-Intended-use.html\"\
  \n\n    strings:\n        $eicar_regex = /^X5O!P%@AP\\[4\\\\PZX54\\(P\\^\\)7CC\\\
  )7\\}\\$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!\\$H\\+H\\*\\s*$/\n\n    condition:\n\
  \        all of them\n}\n\nrule eicar_substring_test {\n    /*\n       More generic\
  \ - match just the embedded EICAR string (e.g. in packed executables, PDFs, etc)\n\
  \    */\n\n    meta:\n        description = \"Standard AV test, checking for an\
  \ EICAR substring\"\n        author = \"Austin Byers | Airbnb CSIRT\"\n\n    strings:\n\
  \        $eicar_substring = \"$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!\"\n\n    condition:\n\
  \        all of them\n}\n\n"
