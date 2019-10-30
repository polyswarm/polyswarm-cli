<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [polyswarm](#polyswarm)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Configuration](#configuration)
    - [Perform Scans](#perform-scans)
    - [Perform Searches](#perform-searches)
    - [Lookup UUIDs](#lookup-uuids)
    - [Download Files](#download-files)
    - [Perform Rescans](#perform-rescans)
    - [Chain commands](#chain-commands)
  - [Questions? Problems?](#questions-problems)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# polyswarm

A CLI tool for interacting with the public and private PolySwarm APIs.

Supports Python 2.7 and greater.

## Installation

From PyPI:

    pip install polyswarm

From source:

    python setup.py install

## Usage


### Configuration

```bash
$ export POLYSWARM_API_KEY=<Your API key from polyswarm.network>
$ export POLYSWARM_COMMUNITY=lima
# for tab completion
$ eval "$(_POLYSWARM_COMPLETE=source polyswarm)"
$ polyswarm
Usage: polyswarm [OPTIONS] COMMAND [ARGS]...

  This is a PolySwarm CLI client, which allows you to interact directly with
  the PolySwarm network to scan files, search hashes, and more.

Options:
  -a, --api-key TEXT              Your API key for polyswarm.network
                                  (required)
  -u, --api-uri TEXT              The API endpoint (ADVANCED)
  -o, --output-file FILENAME      Path to output file.
  --output-format, --fmt [text|json|sha256|sha1|md5]
                                  Output format. Human-readable text or JSON.
  --color / --no-color            Use colored output in text mode.
  -v, --verbose
  -c, --community TEXT            Community to use.
  --advanced-disable-version-check / --advanced-enable-version-check
                                  Enable/disable GitHub release version check.
  -h, --help                      Show this message and exit.

Commands:
  cat         cat artifact to stdout
  download    download file(s)
  historical  interact with historical scans
  live        interact with live scans
  lookup      lookup UUID(s)
  rescan      rescan files(s) by hash
  scan        scan files/directories
  search      interact with PolySwarm search api
  stream      access the polyswarm file stream
  url         scan url
```

### Perform Scans

```bash
$ polyswarm scan /tmp/eicar
Report for artifact eicar, hash: 131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267
        16 out of 19 engines reported this as malicious
        XVirus: Malicious, metadata: {'malware_family': '', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'vendor_version': '3.0.2.0', 'version': '0.2.0'}}
        Trustlook: Clean
        Virusdie: Malicious, metadata: {'malware_family': 'EICAR.TEST', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}, 'vendor_version': '1.3.0', 'version': '0.3.0'}}
        Ikarus: Malicious, metadata: {'malware_family': 'EICAR-Test-File', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}, 'signatures_version': '13.10.2019 18:20:55 (102021)', 'vendor_version': '5.2.9.0', 'version': '0.2.0'}}
        Nucleon: Clean
        Alibaba: Malicious, metadata: {'malware_family': 'Virus:Any/EICAR_Test_File.534838ff', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}}, 'type': 'eicar'}
        Jiangmin: Malicious, metadata: {'malware_family': 'Find Virus EICAR-Test-File in C:\\Users\\ContainerAdministrator\\AppData\\Local\\Temp\\polyswarm-artifact_2k4sehx', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'signatures_version': '', 'vendor_version': '16.0.100 ', 'version': '0.2.0'}}
        K7: Malicious, metadata: {'malware_family': 'Trojan ( 000139291 )', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'signatures_version': '11.66.31997|12/Sep/2019', 'vendor_version': '15.2.0.42', 'version': '0.2.0'}}
        ClamAV: Malicious, metadata: {'malware_family': 'Eicar-Test-Signature', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}, 'vendor_version': 'ClamAV 0.100.3/25601/Sun Oct 13 08:51:55 2019\n'}}
        Quick Heal: Malicious, metadata: {'malware_family': 'EICAR.TestFile', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'signatures_version': '09 September, 2019', 'version': '0.1.0'}}
        Rising: Malicious, metadata: {'malware_family': 'Virus.EICAR_Test_File!8.D9E', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}}}
        NanoAV: Malicious, metadata: {'malware_family': 'Marker.Dos.EICAR-Test-File.dyb', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'signatures_version': '0.14.32.16015|1568318271000', 'vendor_version': '1.0.134.90395', 'version': '0.1.0'}}
        0xBAFcaF4504FCB3608686b40eB1AEe09Ae1dd2bc3: Malicious, metadata: {'malware_family': 'infected with EICAR Test File (NOT a Virus!)', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}, 'signatures_version': 'Core engine version: 7.00.41.07240\nVirus database timestamp: 2019-Oct-13 22:55:51\nVirus database fingerprint: 8AC41842F33C025F71031B23CD5E104B\nVirus databases loaded: 170\nVirus records: 8212364\nAnti-spam core is not loaded\nLast successful update: 2019-Oct-14 00:56:00\nNext scheduled update: 2019-Oct-14 01:26:00\n', 'vendor_version': 'drweb-ctl 11.1.2.1907091642\n', 'version': '0.3.0'}}
        Lionic: Malicious, metadata: {'malware_family': '{"infections": [{"name": "Test.File.EICAR.y!c", "location": "polyswarm-artifactqlel80c6", "path": "C:/Users/ContainerAdministrator/AppData/Local/Temp/polyswarm-artifactqlel80c6", "time": "2019/10/14 01:10:11"}]}', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}}}
        SecureAge: Malicious, metadata: {'malware_family': '', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'signatures_version': '5.73', 'version': '0.3.0'}}
        VenusEye: Malicious, metadata: {'malware_family': '', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}, 'version': '0.1.0'}}
        Tachyon: Malicious, metadata: {'malware_family': 'EICAR-Test-File', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'vendor_version': '2018.11.28.1', 'version': '0.1.0'}}
        Qihoo 360: Malicious, metadata: {'malware_family': 'qex.eicar.gen.gen', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}}}
        ZeroCERT: Clean

$ polyswarm url https://google.com
Report for artifact url, hash: 05046f26c83e8c88b3ddab2eab63d0d16224ac1e564535fc75cdceee47a0938d
        All 5 engines reported this as benign or did not respond
        Virusdie: Clean
        Trustlook: Clean
        Nucleon: Clean
        Cyradar: Clean
        ZeroCERT: Clean
        Scan permalink: https://polyswarm.network/scan/results/1377b0e4-d54a-41b8-87bf-a0885d67cf3c
```

### Perform Searches

Please see the [polyswarm-api docs](https://github.com/polyswarm/polyswarm-api#metadata-terms) for more information on allowed search terms.

```bash
$ polyswarm -o /tmp/test.txt search hash 131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267
$ cat /tmp/test.txt
Found 1 matches to the search query.
Search results for sha256=131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267
File 131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267
        File type: mimetype: text/plain, extended_info: EICAR virus test files
        SHA256: 131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267
        SHA1: cf8bd9dfddff007f75adf4c2be48005cea317c62
        MD5: 69630e4574ec6798239b091cda43dca0
        First seen: Wed, 22 May 2019 15:25:47 GMT
        Observed countries: PR,US
        Observed filenames: 131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267,eicar.com,eicar.txt,cf8bd9dfddff007f75adf4c2be48005cea317c62,eicar.com.txt
        Scan permalink: https://polyswarm.network/scan/results/8f51790a-4e30-48ad-b0a2-036c7306168f
        Detections: 16/19 engines reported malicious
```

```bash
$ polyswarm -o /tmp/test.txt search metadata "strings.domains:en.wikipedia.org AND exiftool.ZipFileName:AndroidManifest.xml AND exiftool.ZipRequiredVersion:>19"
$ cat /tmp/test.txt | more
Found 1000 matches to the search query.
Search results for {'query': {'query_string': {'query': 'strings.domains:en.wikipedia.org AND exiftool.ZipFileName:AndroidManifest.xml'}}}
File 55f9d374e0d16ecaa047f2af9f2dcbb0a6576847caee0a2cbdc36a079961a991
        File type: mimetype: application/x-dosexec, extended_info: PE32 executable (GUI) Intel 80386, for MS Windows
        SHA256: 55f9d374e0d16ecaa047f2af9f2dcbb0a6576847caee0a2cbdc36a079961a991
        SHA1: 4a0da13003a36fc299ea5c7ebd54d59e42854f22
        MD5: ba72c9d80b336ae481a3eceaace1844e
        First seen: Mon, 02 Sep 2019 13:48:06 GMT
        Observed countries: US
        Observed filenames: 55f9d374e0d16ecaa047f2af9f2dcbb0a6576847caee0a2cbdc36a079961a991
        Scan permalink: https://polyswarm.network/scan/results/9c50c2ca-31a8-42cd-b067-b864eff57409
        Detections: 12/19 engines reported malicious
--More--
```

### Lookup UUIDs

```bash
$ polyswarm -vvv -o /tmp/test.json --fmt json lookup ac331689-c4a1-400c-be79-98268c182c88
DEBUG:root:Creating API instance: api_key:<redacted>, api_uri:https://api.polyswarm.network/v1
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): api.polyswarm.network:443
DEBUG:urllib3.connectionpool:https://api.polyswarm.network:443 "GET /v1/consumer/lima/uuid/ac331689-c4a1-400c-be79-98268c182c88 HTTP/1.1" 200 610
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): api.polyswarm.network:443
DEBUG:urllib3.connectionpool:https://api.polyswarm.network:443 "GET /v1/microengines/list HTTP/1.1" 200 1887
$ cat /tmp/test.json
{"files": [{"assertions": [{"author": "0x80Ed773972d8BA0A4FacF2401Aca5CEba52F76dc", "bid": 500000000000000000, "mask": true, "metadata": {"malware_family": "", "scanner": {"environment": {"architecture": "x86_64", "operating_system": "Linux"}, "vendor_version": "", "version": "0.1.0"}}, "verdict": false, "engine_name": "Nucleon"}, {"author": "0x8d80CEe474b9004949Cf7e4BfA28460AC8e370a1", "bid": 500000000000000000, "mask": true, "metadata": {"malware_family": "", "scanner": {"environment": {"architecture": "x86_64", "operating_system": "Linux"}, "version": "0.3.0"}}, "verdict": false, "engine_name": "Virusdie"}, {"author": "0xF598F7dA0D00D9AD21fb00663a7D62a19D43Ea61", "bid": 500000000000000000, "mask": true, "metadata": {"malware_family": "Search engine", "scanner": {"environment": {"architecture": "x86_64", "operating_system": "Linux"}, "vendor_version": "2", "version": "0.1.0"}}, "verdict": false, "engine_name": "Trustlook"}, {"author": "0x8434434991A61dAcE1544a7FC1B0F8d83523B778", "bid": 500000000000000000, "mask": true, "metadata": {"malware_family": "", "scanner": {"environment": {"architecture": "x86_64", "operating_system": "Linux"}, "vendor_version": "", "version": "0.1.0"}}, "verdict": false, "engine_name": "Cyradar"}, {"author": "0xdCc9064325c1aa24E08182676AD23B3D78b39E05", "bid": 500000000000000000, "mask": true, "metadata": {"malware_family": "", "scanner": {"environment": {"architecture": "x86_64", "operating_system": "Linux"}, "vendor_version": "1.1", "version": "0.1.0"}}, "verdict": false, "engine_name": "ZeroCERT"}], "bounty_guid": "423a680a-ebf5-41a1-ba66-c64a84924091", "bounty_status": "Bounty Settled", "failed": false, "filename": "url", "hash": "05046f26c83e8c88b3ddab2eab63d0d16224ac1e564535fc75cdceee47a0938d", "result": null, "size": 18, "submission_guid": "ac331689-c4a1-400c-be79-98268c182c88", "votes": [], "window_closed": true}], "forced": false, "status": "Bounty Settled", "uuid": "ac331689-c4a1-400c-be79-98268c182c88"}
```

### Download Files

```bash
$ polyswarm download test/ 131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267
Successfully downloaded artifact 131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267 to /home/user/test/131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267
```

### Perform Rescans

```bash
$ polyswarm rescan 131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267
Report for artifact 131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267, hash: 131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267
        17 out of 20 engines reported this as malicious
        VenusEye: Malicious, metadata: {'malware_family': '', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}, 'version': '0.1.0'}}
        K7: Malicious, metadata: {'malware_family': 'Trojan ( 000139291 )', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'signatures_version': '11.66.31997|12/Sep/2019', 'vendor_version': '15.2.0.42', 'version': '0.2.0'}}
        Jiangmin: Malicious, metadata: {'malware_family': 'Find Virus EICAR-Test-File in C:\\Users\\ContainerAdministrator\\AppData\\Local\\Temp\\polyswarm-artifactztoecu5h', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'signatures_version': '', 'vendor_version': '16.0.100 ', 'version': '0.2.0'}}
        Virusdie: Malicious, metadata: {'malware_family': 'EICAR.TEST', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}, 'vendor_version': '1.3.0', 'version': '0.3.0'}}
        Trustlook: Clean
        0xBAFcaF4504FCB3608686b40eB1AEe09Ae1dd2bc3: Malicious, metadata: {'malware_family': 'infected with EICAR Test File (NOT a Virus!)', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}, 'signatures_version': 'Core engine version: 7.00.41.07240\nVirus database timestamp: 2019-Oct-14 00:10:21\nVirus database fingerprint: 95CC1F8E066874DCF48E898334572198\nVirus databases loaded: 170\nVirus records: 8212567\nAnti-spam core is not loaded\nLast successful update: 2019-Oct-14 01:56:03\nNext scheduled update: 2019-Oct-14 02:26:03\n', 'vendor_version': 'drweb-ctl 11.1.2.1907091642\n', 'version': '0.3.0'}}
        Nucleon: Clean
        Alibaba: Malicious, metadata: {'malware_family': 'Virus:Any/EICAR_Test_File.534838ff', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}}, 'type': 'eicar'}
        NanoAV: Malicious, metadata: {'malware_family': 'Marker.Dos.EICAR-Test-File.dyb', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'signatures_version': '0.14.32.16015|1568318271000', 'vendor_version': '1.0.134.90395', 'version': '0.1.0'}}
        Quick Heal: Malicious, metadata: {'malware_family': 'EICAR.TestFile', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'signatures_version': '09 September, 2019', 'version': '0.1.0'}}
        Qihoo 360: Malicious, metadata: {'malware_family': 'qex.eicar.gen.gen', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}}}
        ZeroCERT: Clean
        XVirus: Malicious, metadata: {'malware_family': '', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'vendor_version': '3.0.2.0', 'version': '0.2.0'}}
        Ikarus: Malicious, metadata: {'malware_family': 'EICAR-Test-File', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}, 'signatures_version': '13.10.2019 18:20:55 (102021)', 'vendor_version': '5.2.9.0', 'version': '0.2.0'}}
        ClamAV: Malicious, metadata: {'malware_family': 'Eicar-Test-Signature', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}, 'vendor_version': 'ClamAV 0.100.3/25601/Sun Oct 13 08:51:55 2019\n'}}
        SecureAge: Malicious, metadata: {'malware_family': '', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'signatures_version': '5.73', 'version': '0.3.0'}}
        Lionic: Malicious, metadata: {'malware_family': '{"infections": [{"name": "Test.File.EICAR.y!c", "location": "polyswarm-artifact52c_247x", "path": "C:/Users/ContainerAdministrator/AppData/Local/Temp/polyswarm-artifact52c_247x", "time": "2019/10/14 02:00:47"}]}', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}}}
        Antiy-AVL: Malicious, metadata: {'malware_family': 'Virus/DOS.EICAR_Test_File', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}}}
        Tachyon: Malicious, metadata: {'malware_family': 'EICAR-Test-File', 'scanner': {'environment': {'architecture': 'AMD64', 'operating_system': 'Windows'}, 'vendor_version': '2018.11.28.1', 'version': '0.1.0'}}
        Rising: Malicious, metadata: {'malware_family': 'Virus.EICAR_Test_File!8.D9E', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}}}
        Scan permalink: https://polyswarm.network/scan/results/ce290fc6-77c1-4dd2-944d-2dc52b6ea722
```

For information regarding the JSON format, please see [polyswarm-api's API.md](https://github.com/polyswarm/polyswarm-api/blob/master/API.md).

### Chain commands
Some commands in the CLI are composable using the `sha256` format option. For instance, if we wanted to download all the results matching a metadata query:

```bash
$ polyswarm --fmt sha256 search metadata 'strings.domains:malicious.com' | polyswarm download malicious -r -
Successfully downloaded artifact 131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267 to /home/user/malicious/131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ffbdfd8267
```

## Questions? Problems?

File a ticket or email us at `info@polyswarm.io`.
