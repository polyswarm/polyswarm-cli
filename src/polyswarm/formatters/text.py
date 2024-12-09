import sys
import functools
import json
from datetime import datetime

import click
from polyswarm_api.core import parse_isoformat

from polyswarm.formatters import base


def pretty_print_datetime(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = parse_isoformat(value)
    return datetime.strftime(value, '%Y-%m-%d %H:%M:%S UTC')


def is_grouped(fn):
    @functools.wraps(fn)
    def wrapper(self, text):
        return self._depth*'\t'+fn(self, text)

    return wrapper


class TextOutput(base.BaseOutput):
    name = 'text'

    def __init__(self, color=True, output=sys.stdout, **kwargs):
        super().__init__(output)
        self.color = color
        self._depth = 0
        self.color = color

    def _get_score_format(self, score):
        if score < 0.3:
            return self._white
        elif score < 0.7:
            return self._yellow
        else:
            return self._red

    def _output(self, output, write):
        if write:
            click.echo('\n'.join(output) + '\n', file=self.out)
        else:
            return output

    def artifact(self, artifact, write=True):
        output = []
        output.append(self._blue(f'SHA256: {artifact.sha256}'))
        output.append(self._white(f'SHA1: {artifact.sha1}'))
        output.append(self._white(f'MD5: {artifact.md5}'))
        output.append(self._white(f'File type: mimetype: {artifact.mimetype}, extended_info: {artifact.extended_type}'))

        h = artifact.metadata.hash
        if 'ssdeep' in h:
            output.append(self._white(f'SSDEEP: {h["ssdeep"]}'))
        if 'tlsh' in h:
            output.append(self._white(f'TLSH: {h["tlsh"]}'))
        if 'authentihash' in h:
            output.append(self._white(f'Authentihash: {h["authentihash"]}'))
        p = artifact.metadata.pefile
        if 'imphash' in p:
            output.append(self._white(f'Imphash: {p["imphash"]}'))
        output.append(self._white(f'First seen: {pretty_print_datetime(artifact.first_seen)}'))
        output.append(self._white(f'Last scanned: {pretty_print_datetime(artifact.last_scanned)}'))
        # Deprecated
        output.append(self._white(f'Last seen: {pretty_print_datetime(artifact.last_scanned)}'))
        return self._output(output, write)

    def artifact_instance(self, instance, write=True, timeout=False):
        output = []
        output.append(self._white('============================= Artifact Instance ============================='))
        if not instance.failed:
            output.append(self._white(f'Scan permalink: {instance.permalink}'))

        if instance.community == 'stream':
            output.append(self._white('Detections: This artifact has not been scanned. You can trigger a scan now.'))
        elif len(instance.valid_assertions) == 0 and instance.window_closed and not instance.failed:
            output.append(self._white('Detections: No engines responded to this scan. You can trigger a rescan now.'))
        elif len(instance.valid_assertions) > 0 and instance.window_closed and not instance.failed:
            malicious = f'Detections: {len(instance.malicious_assertions)}/{len(instance.valid_assertions)} engines reported malicious'
            if len(instance.malicious_assertions) > 0:
                output.append(self._red(malicious))
            else:
                output.append(self._white(malicious))
        elif not instance.window_closed and not instance.failed:
            output.append(self._white('Detections: This scan has not finished running yet.'))
        else:
            output.append(self._white('Detections: This scan has failed. Please try again.'))

        self._open_group()
        for assertion in instance.assertions:
            if assertion.verdict is False:
                output.append(f'{self._green(assertion.engine_name)}: {"Clean"}')
            elif assertion.verdict is None or assertion.mask is False:
                output.append(f"{self._blue(assertion.engine_name)}: Engine chose not respond to this bounty.")
            else:
                value = 'Malicious'
                if assertion.metadata:
                    value += f', metadata: {json.dumps(assertion.metadata, sort_keys=True)}'
                output.append(f'{self._red(assertion.engine_name)}: {value}')
        self._close_group()
        output.append(self._blue(f'Scan id: {instance.id}'))
        output.extend(self.artifact(instance, write=False))
        if instance.failed:
            output.append(self._red('Status: Failed'))
            if instance.failed_reason:
                output.append(self._red(f'Failure Reason: {instance.failed_reason}'))
        elif instance.window_closed:
            output.append(self._white('Status: Assertion window closed'))
        elif instance.community == 'stream':
            output.append(self._white('Status: This artifact has not been scanned. You can trigger a scan now.'))
        elif timeout:
            output.append(self._yellow('Status: Lookup timed-out, please retry'))
        else:
            output.append(self._white('Status: Running'))
        if instance.type == 'URL':
            output.append(self._white(f'URL: {instance.filename}'))
        else:
            output.append(self._white(f'Filename: {instance.filename}'))
        output.append(self._white(f'Community: {instance.community}'))
        output.append(self._white(f'Country: {instance.country}'))

        if instance.polyscore is not None:
            formatter = self._get_score_format(instance.polyscore)
            output.append(formatter(f'PolyScore: {instance.polyscore:.20f}'))

        return self._output(output, write)

    def hunt(self, result, write=True):
        output = []
        output.append(self._blue(f'Hunt Id: {result.id}'))
        output.append(self._white(f'Status: {result.status}'))
        if result.progress is not None:
            output.append(self._white(f'Progress: {result.progress:.2f}%'))
        if result.active is not None:
            output.append(self._white(f'Active: {result.active}'))
        output.append(self._white(f'Created at: {result.created}'))
        if result.summary:
            output.append(self._white(f'Total count: {result.summary["count"]}'))
            self._open_group()
            for rule, data in result.summary.get('rule', []).items():
                output.append(self._white(f'{rule}: {data["count"]}'))
            self._close_group()
        if result.results_csv_uri:
            output.append(self._white('Download Results CSV:'))
            self._open_group()
            output.append(self._white(result.results_csv_uri))
            self._close_group()
        if result.ruleset_name is not None:
            output.append(self._white(f'Ruleset Name: {result.ruleset_name}'))
        if result.yara:
            output.append(self._white(f'Ruleset Contents:\n{result.yara}'))
        return self._output(output, write)

    def hunt_deletion(self, result, write=True):
        output = []
        output.append(self._yellow('Successfully deleted Hunt:'))
        output.extend(self.hunt(result, write=False))

        return self._output(output, write)

    def historical_result(self, result, write=True):
        output = []
        output.append(self._blue(f'Id: {result.id}'))
        output.append(self._blue(f'Instance Id: {result.instance_id}'))
        output.append(self._white(f'Created at: {result.created}'))
        output.append(self._white(f'SHA256: {result.sha256}'))
        output.append(self._white(f'Rule: {result.rule_name}'))
        if result.malware_family:
            output.append(self._red(f'Malware Family: {result.malware_family}'))
        if result.polyscore is not None:
            formatter = self._get_score_format(result.polyscore)
            output.append(formatter(f'PolyScore: {result.polyscore:.20f}'))
        if result.detections:
            if result.detections['total'] == 0:
                output.append(self._white('Detections: No engines responded to this scan. You can trigger a rescan now.'))
            else:
                malicious = f'Detections: {result.detections["malicious"]}/{result.detections["total"]} engines reported malicious'
                if result.detections['malicious'] > 0:
                    output.append(self._red(malicious))
                else:
                    output.append(self._white(malicious))
        if result.tags:
            output.append(self._white(f'Tags: {result.tags}'))
        if result.download_url:
            output.append(self._white(f'Download Url: {result.download_url}'))
        return self._output(output, write)

    def live_result(self, result, write=True):
        output = []
        output.append(self._blue(f'Id: {result.id}'))
        output.append(self._blue(f'Instance Id: {result.instance_id}'))
        output.append(self._white(f'Created at: {result.created}'))
        output.append(self._white(f'SHA256: {result.sha256}'))
        output.append(self._white(f'Rule: {result.rule_name}'))
        if result.malware_family:
            output.append(self._red(f'Malware Family: {result.malware_family}'))
        if result.polyscore is not None:
            formatter = self._get_score_format(result.polyscore)
            output.append(formatter(f'PolyScore: {result.polyscore:.20f}'))
        if result.detections:
            if result.detections['total'] == 0:
                output.append(self._white('Detections: No engines responded to this scan. You can trigger a rescan now.'))
            else:
                malicious = f'Detections: {result.detections["malicious"]}/{result.detections["total"]} engines reported malicious'
                if result.detections['malicious'] > 0:
                    output.append(self._red(malicious))
                else:
                    output.append(self._white(malicious))
        if result.tags:
            output.append(self._white(f'Tags: {result.tags}'))
        if result.download_url:
            output.append(self._white(f'Download Url: {result.download_url}'))
        return self._output(output, write)

    def ruleset(self, result, write=True, contents=False):
        output = []
        output.append(self._blue(f'Ruleset Id: {result.id}'))
        if result.livescan_id:
            output.append(self._yellow(f'Live Hunt Id: {result.livescan_id}'))
            output.append(self._white(f'Live Hunt Created at: {result.livescan_created}'))
        output.append(self._white(f'Name: {result.name}'))
        output.append(self._white(f'Description: {result.description}'))
        output.append(self._white(f'Created at: {result.created}'))
        output.append(self._white(f'Modified at: {result.modified}'))
        if contents:
            output.append(self._white(f'Ruleset Contents:\n{result.yara}'))
        return self._output(output, write)

    def tag_link(self, result, write=True):
        output = []
        output.append(self._blue(f'SHA256: {result.sha256}'))
        output.append(self._white(f'First seen: {result.first_seen}'))
        output.append(self._white(f'Tags: {result.tags}'))
        output.append(self._white(f'Families: {result.families}'))
        output.append(self._white(f'Emerging: {result.emerging}'))
        return self._output(output, write)

    def family(self, result, write=True):
        output = []
        output.append(self._blue(f'Family: {result.name}'))
        output.append(self._white(f'Emerging: {result.emerging}'))
        return self._output(output, write)

    def tag(self, result, write=True):
        output = []
        output.append(self._blue(f'Tag: {result.name}'))
        return self._output(output, write)

    def local_artifact(self, artifact, write=True):
        output = []
        output.append(self._white(f'Successfully downloaded artifact {artifact.artifact_name} to {artifact.name}'))
        return self._output(output, write)

    def _dfs_mapping_render(self, output, path, tree, depth=0):
        tree_string = (' | ' * (depth - 1)) + ' +-' if depth > 0 else ''
        current_path = '.'.join(path)
        if not tree:
            output.append(self._white(tree_string + current_path))
        else:
            if path:
                output.append(self._white(tree_string + current_path))
            for k, v in tree.items():
                self._dfs_mapping_render(output, path + [k], v, depth=depth + 1)

    def mapping(self, mapping, write=True):
        output = []
        output.append(self._white('============================= Mapping ============================='))
        self._dfs_mapping_render(output, [], mapping.json)
        return self._output(output, write)

    def iocs(self, iocs, write=True):
        output = []
        output.append(self._white('============================= IOCs ============================='))
        for result in iocs:
            data = result.json
            if type(data) is dict:
                output.append(self._white(f'ImpHash: {data["imphash"]}'))
                output.append(self._white(f'IPs: {", ".join(data["ips"])}'))
                output.append(self._white(f'URLs: {", ".join(data["urls"])}'))
                output.append(self._white(f'TTPs: {", ".join(data["ttps"])}'))
            else:
                output.append(self._white(f'SHA256: {data}'))
        return self._output(output, write)
    
    def ioc(self, ioc, write=True):
        output = []
        output.append(self._white('============================= IOC ============================='))
        data = ioc.json
        if type(data) is dict:
            output.append(self._white(f'ImpHash: {data["imphash"]}'))
            output.append(self._white(f'IPs: {", ".join(data["ips"])}'))
            output.append(self._white(f'URLs: {", ".join(data["urls"])}'))
            output.append(self._white(f'TTPs: {", ".join(data["ttps"])}'))
        else:
            output.append(self._white(f'SHA256: {data}'))
        return self._output(output, write)
    
    def known_host(self, ioc_known, write=True):
        output = []
        output.append(self._white('============================= Known IOC ============================='))
        output.append(self._white(f'ID: {ioc_known.json["id"]}'))
        output.append(self._white(f'type: {ioc_known.json["type"]}'))
        output.append(self._white(f'host: {ioc_known.json["host"]}'))
        output.append(self._white(f'source: {ioc_known.json["source"]}'))
        output.append(self._white(f'good: {ioc_known.json["good"]}'))
        return self._output(output, write)

    def artifact_metadata(self, instance, write=True, only=None):
        output = []
        output.append(self._white('============================= Metadata Status ============================='))
        output.append(self._blue(f'Scan id: {instance.id}'))

        self._open_group()
        max_len = 0
        entries = sorted(iter(m for m in instance.json['metadata']),
                         key=lambda m: m['updated'], reverse=True)
        for metadata in entries:
            if only is None or metadata['tool'] in only:
                max_len = max(max_len, len(metadata['tool']))
        for metadata in entries:
            if only is None or metadata['tool'] in only:
                tool = self._white(metadata['tool'].rjust(max_len))
                output.append(f'{tool}: Updated at {pretty_print_datetime(metadata["updated"])}')
        self._close_group()

        return self._output(output, write)

    def sandbox_providers(self, result, write=True):
        output = []
        for provider in result.json['result'].values():
            output.append(self._white('============================= Provider ============================='))
            output.append(self._blue(f'slug: {provider["slug"]}'))
            output.append(self._white(f'name: {provider["name"]}'))
            output.append(self._white(f'tool: {provider["tool"]}'))
            self._open_group()
            for vm in provider['vms'].values():
                output.append(self._white('============================= VM ============================='))
                for k, v in vm.items():
                    output.append(self._white(f'{k}: {v}'))
            self._close_group()
        return self._output(output, write)
    
    def sandbox_task(self, task, write=True):
        output = []
        output.append(self._white('============================= Sandbox Task ============================='))
        output.append(self._blue(f'ID: {task.id}'))
        output.append(self._blue(f'SHA256: {task.sha256}'))
        artifact_type = task.config.get("artifact_type", 'FILE') if task.config else 'FILE'
        output.append(self._white(f'Type: {artifact_type}'))
        if artifact_type == 'URL':
            output.append(self._white(f'URL: {task.artifact["filename"]}'))
        else:
            output.append(self._white(f'Filename: {task.artifact["filename"]}'))
            output.append(self._white(f'File type: mimetype: {task.artifact["mimetype"]}, '
                                      f'extended_info: {task.artifact["extended_type"]}'))
        output.append(self._white(f'Sandbox Provider: {task.sandbox}'))
        output.append(self._white(f'Created: {task.created}'))
        output.append(self._white(f'Community: {task.community}'))
        output.append(self._white(f'Instance ID: {task.instance_id}'))
        if task.status in ('FAILED', 'FAILED_REIMBURSED', 'TIMEDOUT_REIMBURSED', 'TIMEDOUT'):
            output.append(self._red(f'Status: {task.status}'))
            if task.artifact.get("failed_reason"):
                output.append(self._red(f'Failure Reason: {task.artifact["failed_reason"]}'))
        elif task.status == 'SUCCEEDED':
            output.append(self._green(f'Status: {task.status}'))
        else:
            output.append(self._yellow(f'Status: {task.status}'))

        if task.account_number:
            output.append(self._white(f'Account Number: {task.account_number}'))
        if task.team_account_number:
            output.append(self._white(f'Team Account Number: {task.team_account_number}'))

        if task.sandbox_artifacts:
            output.append(self._white('Sandbox Artifacts:'))
        self._open_group()
        for artifact in task.sandbox_artifacts:
            output_string = f'{artifact.type}: '
            if artifact.name:
                output_string += f'{artifact.name}, '
            if artifact.mimetype:
                output_string += f'{artifact.mimetype}, '
            output_string += f'Instance ID: {artifact.instance_id}'
            output.append(self._white(output_string))
        self._close_group()

        if task.report:
            output.append(self._white('report: use `--fmt pretty-json` to see report content'))

        return self._output(output, write)

    def metadata(self, instance, write=True):
        output = []
        output.append(self._white('============================= Metadata ============================='))
        output.append(self._blue(f'Artifact id: {instance.id}'))
        output.append(self._white(f'Created: {instance.created}'))

        if instance.sha256:
            output.append(self._white(f'SHA256: {instance.sha256}'))
        if instance.sha1:
            output.append(self._white(f'SHA1: {instance.sha1}'))
        if instance.md5:
            output.append(self._white(f'MD5: {instance.md5}'))
        if instance.ssdeep:
            output.append(self._white(f'SSDEEP: {instance.ssdeep}'))
        if instance.tlsh:
            output.append(self._white(f'TLSH: {instance.tlsh}'))

        if instance.first_seen:
            output.append(self._white(f'First seen: {instance.first_seen}'))
        if instance.last_scanned:
            output.append(self._white(f'Last scanned: {instance.last_scanned}'))
            # Deprecated
            output.append(self._white(f'Last seen: {instance.last_scanned}'))

        if instance.mimetype:
            output.append(self._white(f'Mimetype: {instance.mimetype}'))
        if instance.extended_mimetype:
            output.append(self._white(f'Extended mimetype: {instance.extended_mimetype}'))
        if instance.malicious:
            output.append(self._white(f'Malicious: {instance.malicious}'))
        if instance.benign:
            output.append(self._white(f'Benign: {instance.benign}'))
        if instance.total_detections:
            output.append(self._white(f'Total detections: {instance.total_detections}'))

        if instance.domains:
            output.append(self._white('Domains:'))
            self._open_group()
            output.append(self._white(', '.join(instance.domains)))
            self._close_group()
        if instance.ipv4:
            output.append(self._white('Ipv4:'))
            self._open_group()
            output.append(self._white(', '.join(instance.ipv4)))
            self._close_group()
        if instance.ipv6:
            output.append(self._white('Ipv6:'))
            self._open_group()
            output.append(self._white(', '.join(instance.ipv6)))
            self._close_group()
        if instance.urls:
            output.append(self._white('Urls:'))
            self._open_group()
            output.append(self._white(', '.join(instance.urls)))
            self._close_group()

        if instance.filenames:
            output.append(self._white('Filenames:'))
            self._open_group()
            output.append(self._white(', '.join(instance.filenames)))
            self._close_group()

        return self._output(output, write)

    def assertions(self, instance, write=True):
        output = []
        output.append(self._white('============================= Assertions Job ============================='))
        output.append(self._blue(f'Assertions Job id: {instance.id}'))
        output.append(self._white(f'Engine id: {instance.engine_id}'))
        output.append(self._white(f'Created at: {instance.created}'))
        output.append(self._white(f'Start date: {instance.date_start}'))
        output.append(self._white(f'End date: {instance.date_end}'))

        if instance.storage_path is not None:
            output.append(self._white(f'Download: {instance.storage_path}'))
            output.append(self._white(f'True Positive: {instance.true_positive}'))
            output.append(self._white(f'True Negative: {instance.true_negative}'))
            output.append(self._white(f'False Positive: {instance.false_positive}'))
            output.append(self._white(f'False Negative: {instance.false_negative}'))
            output.append(self._white(f'Suspicious: {instance.suspicious}'))
            output.append(self._white(f'Unknown: {instance.unknown}'))
            output.append(self._white(f'Total: {instance.total}'))

        return self._output(output, write)

    def votes(self, instance, write=True):
        output = []
        output.append(self._white('============================= Votes Job ============================='))
        output.append(self._blue(f'Votes Job id: {instance.id}'))
        output.append(self._white(f'Engine id: {instance.engine_id}'))
        output.append(self._white(f'Created at: {instance.created}'))
        output.append(self._white(f'Start date: {instance.date_start}'))
        output.append(self._white(f'End date: {instance.date_end}'))

        if instance.storage_path is not None:
            output.append(self._white(f'Download: {instance.storage_path}'))
            output.append(self._white(f'True Positive: {instance.true_positive}'))
            output.append(self._white(f'True Negative: {instance.true_negative}'))
            output.append(self._white(f'False Positive: {instance.false_positive}'))
            output.append(self._white(f'False Negative: {instance.false_negative}'))
            output.append(self._white(f'Suspicious: {instance.suspicious}'))
            output.append(self._white(f'Unknown: {instance.unknown}'))
            output.append(self._white(f'Total: {instance.total}'))

        return self._output(output, write)

    def event(self, event, write=True):
        output = []
        output.append(self._white('============================= Event ============================='))
        output.append(self._white(f'event_timestamp: {event.json["event_timestamp"]}'))
        output.append(self._white(f'event_type: {event.json["event_type"]}'))
        output.append(self._white(f'source: {event.json["source"]}'))
        output.append(self._white(f'team_account_id: {event.json["team_account_id"]}'))
        output.append(self._white(f'user_account_id: {event.json["user_account_id"]}'))
        for key in event.json:
            if key not in {'event_timestamp', 'event_type', 'source', 'team_account_id', 'user_account_id'}:
                output.append(self._white(f'{key}: {event.json[key]}'))
        return self._output(output, write)

    def report_task(self, report, write=True):
        output = []
        output.append(self._white('============================= Report ============================='))
        output.append(self._blue(f'ID: {report.id}'))
        output.append(self._white(f'Community: {report.community}'))
        output.append(self._white(f'Created: {report.created}'))
        output.append(self._white(f'Type: {report.type}'))
        output.append(self._white(f'Format: {report.format}'))
        if report.template_id:
            output.append(self._white(f'Template ID: {report.template_id}'))
        if 'includes' in report.template_metadata:
            output.append(self._white(f'Includes: {", ".join(report.template_metadata["includes"])}'))
        if report.instance_id:
            output.append(self._white(f'Scan ID: {report.instance_id}'))
        elif report.sandbox_task_id:
            output.append(self._white(f'Sandbox ID: {report.sandbox_task_id}'))
        state_writer = self._red if report.state == 'FAILED' else self._yellow
        output.append(state_writer(f'State: {report.state}'))
        if report.url:
            output.append(self._white(f'URL: {report.url}'))
        return self._output(output, write)

    def report_template(self, template, write=True):
        output = []
        output.append(self._white('============================= Report Template ============================='))
        output.append(self._blue(f'ID: {template.id}'))
        output.append(self._white(f'Template Name: {template.template_name}'))
        output.append(self._white(f'Created: {template.created}'))
        if template.primary_color:
            output.append(self._white(f'Primary Color: {template.primary_color}'))
        if template.is_default:
            output.append(f'Is Default: {template.is_default}')
        if template.includes:
            output.append(self._white(f'Includes: {", ".join(template.includes)}'))
        if template.footer_text:
            output.append(self._white(f'Footer Text: {template.footer_text}'))
        if template.last_page_text:
            output.append(self._white(f'Last Page Text: {template.last_page_text}'))
        if template.logo_content_length:
            output.append(self._white(f'Logo Content Length: {template.logo_content_length}'))
            output.append(self._white(f'Logo Content Type: {template.logo_content_type}'))
            output.append(self._white(f'Logo URL: {template.logo_url}'))
            output.append(self._white(f'Logo Height: {template.logo_height}'))
            output.append(self._white(f'Logo Width: {template.logo_width}'))
        return self._output(output, write)

    def account_whois(self, account, write=True):
        output = []
        output.append(self._white('============================= Account Details ============================='))
        if account.account_type == 'user':
            output.append(self._blue(f'User Account Number: {account.account_number}'))
        else:
            output.append(self._blue(f'Account Number: {account.account_number}'))
            if account.account_type == 'team':
                output.append(self._blue(f'User Account Number: {account.user_account_number}'))
        output.append(self._white(f'Account Name: {account.account_name}'))
        output.append(self._white(f'Account Type: {account.account_type}'))
        if account.tenant:
            output.append(self._white(f'Tenant: {account.tenant}'))
        output.append(self._white(f'Communities: {", ".join(account.communities)}'))
        return self._output(output, write)

    def account_features(self, quota, write=True):
        output = []
        output.append(self._white('========================= Account Plan ========================='))

        if quota.user_account_number == quota.account_number:
            output.append(self._blue(f'User Account Number: {quota.user_account_number}'))
        else:
            output.append(self._blue(f'Account Number: {quota.account_number}'))
            output.append(self._blue(f'User Account Number: {quota.user_account_number}'))
        if quota.tenant:
            output.append(self._white(f'Tenant: {quota.tenant}'))
        output.append(self._white(f'Account Plan Name: {quota.account_plan_name}'))
        output.append(self._white(f'Plan Period Start: {quota.plan_period_start}'))
        if quota.plan_period_end:
            output.append(self._white(f'Plan Period End: {quota.plan_period_end}'))
        output.append(self._white(f'Window Start: {quota.window_start}'))
        output.append(self._white(f'Window End: {quota.window_end}'))
        output.append(self._white(f'Daily API Limit: {quota.daily_api_limit}'))
        output.append(self._white(f'Daily API Remaining: {quota.daily_api_remaining}'))
        output.append(self._white(f'Has Stream Access?: {"Yes" if quota.has_stream_access else "No"}'))
        if quota.is_trial:
            output.append(self._white('Is Trial?: Yes'))
            if quota.is_trial_expired:
                output.append(self._red('Is Trial Expired?: Yes'))
            else:
                output.append(self._white('Is Trial Expired?: No'))
            output.append(self._white(f'Trial Started At: {quota.trial_started_at}'))
            output.append(self._white(f'Trial Ended At: {quota.trial_ended_at}'))
        else:
            output.append(self._white('Is Trial?: No'))
        output.append(self._white('\n================== Account Features and Quota =================='))
        for feature in quota.features:
            output.append(self._yellow(f'Name: {feature["name"]}'))
            output.append(self._white(f'Tag: {feature["tag"]}'))
            output.append(self._white(f'Value: {feature["value"]}'))
            if feature.get("backing_feature"):
                output.append(self._white(f'Backing Feature: {feature["backing_feature"]}'))
            if feature["base_uses"]:
                output.append(self._white(f'Base Uses: {feature["base_uses"]}'))
                if feature["remaining_uses"]:
                    output.append(self._white(f'Remaining Uses: {feature["remaining_uses"]}'))
                else:
                    output.append(self._red(f'Remaining Uses: {feature["remaining_uses"]}'))
                if feature["overage"]:
                    output.append(self._white(f'Overage: {feature["overage"]}'))
            output.append(self._white("---"))
        return self._output(output, write)

    @is_grouped
    def _white(self, text):
        return click.style(text, fg='white')

    @is_grouped
    def _yellow(self, text):
        return click.style(text, fg='yellow')

    @is_grouped
    def _red(self, text):
        return click.style(text, fg='red')

    @is_grouped
    def _blue(self, text):
        return click.style(text, fg='blue')

    @is_grouped
    def _green(self, text):
        return click.style(text, fg='green')

    def _open_group(self):
        self._depth += 1

    def _close_group(self):
        self._depth -= 1
