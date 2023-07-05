from __future__ import absolute_import, unicode_literals
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
        super(TextOutput, self).__init__(output)
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
        output.append(self._blue('SHA256: {hash}'.format(hash=artifact.sha256)))
        output.append(self._white('SHA1: {hash}'.format(hash=artifact.sha1)))
        output.append(self._white('MD5: {hash}'.format(hash=artifact.md5)))
        output.append(self._white('File type: mimetype: {mimetype}, extended_info: {extended_type}'.
                                  format(mimetype=artifact.mimetype, extended_type=artifact.extended_type)))

        h = artifact.metadata.hash
        if 'ssdeep' in h:
            output.append(self._white('SSDEEP: {}'.format(h['ssdeep'])))
        if 'tlsh' in h:
            output.append(self._white('TLSH: {}'.format(h['tlsh'])))
        if 'authentihash' in h:
            output.append(self._white('Authentihash: {}'.format(h['authentihash'])))
        p = artifact.metadata.pefile
        if 'imphash' in p:
            output.append(self._white('Imphash: {}'.format(p['imphash'])))
        output.append(self._white('First seen: {}'.format(
            pretty_print_datetime(artifact.first_seen))))
        output.append(self._white('Last scanned: {}'.format(
            pretty_print_datetime(artifact.last_scanned))))
        # Deprecated
        output.append(self._white('Last seen: {}'.format(
            pretty_print_datetime(artifact.last_scanned))))
        return self._output(output, write)

    def artifact_instance(self, instance, write=True, timeout=False):
        output = []
        output.append(self._white('============================= Artifact Instance ============================='))
        output.append(self._white('Scan permalink: {}'.format(instance.permalink)))

        if instance.community == 'stream':
            output.append(self._white('Detections: This artifact has not been scanned. You can trigger a scan now.'))
        elif len(instance.valid_assertions) == 0 and instance.window_closed and not instance.failed:
            output.append(self._white('Detections: No engines responded to this scan. You can trigger a rescan now.'))
        elif len(instance.valid_assertions) > 0 and instance.window_closed and not instance.failed:
            malicious = 'Detections: {}/{} engines reported malicious'\
                .format(len(instance.malicious_assertions), len(instance.valid_assertions))
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
                output.append('%s: %s' % (self._green(assertion.engine_name), 'Clean'))
            elif assertion.verdict is None or assertion.mask is False:
                output.append('%s: %s' % (self._blue(assertion.engine_name), 'Engine chose not respond to this bounty.'))
            else:
                value = 'Malicious'
                if assertion.metadata:
                    value += ', metadata: %s' % json.dumps(assertion.metadata, sort_keys=True)
                output.append('%s: %s' % (self._red(assertion.engine_name), value))
        self._close_group()
        output.append(self._blue('Scan id: {}'.format(instance.id)))
        output.extend(self.artifact(instance, write=False))
        if instance.failed:
            output.append(self._red('Status: Failed'))
        elif instance.window_closed:
            output.append(self._white('Status: Assertion window closed'))
        elif instance.community == 'stream':
            output.append(self._white('Status: This artifact has not been scanned. You can trigger a scan now.'))
        elif timeout:
            output.append(self._yellow('Status: Lookup timed-out, please retry'))
        else:
            output.append(self._white('Status: Running'))
        if instance.type == 'URL':
            output.append(self._white('URL: {}'.format(instance.filename)))
        else:
            output.append(self._white('Filename: {}'.format(instance.filename)))
        output.append(self._white('Community: {}'.format(instance.community)))
        output.append(self._white('Country: {}'.format(instance.country)))

        if instance.polyscore is not None:
            formatter = self._get_score_format(instance.polyscore)
            output.append(formatter('PolyScore: {:.20f}'.format(instance.polyscore)))

        return self._output(output, write)

    def hunt(self, result, write=True):
        output = []
        output.append(self._blue('Hunt Id: {}'.format(result.id)))
        output.append(self._white('Status: {}'.format(result.status)))
        if result.progress is not None:
            output.append(self._white('Progress: {:.2f}%'.format(result.progress)))
        if result.active is not None:
            output.append(self._white('Active: {}'.format(result.active)))
        output.append(self._white('Created at: {}'.format(result.created)))
        if result.summary:
            output.append(self._white('Total count: {}'.format(result.summary['count'])))
            self._open_group()
            for rule, data in result.summary.get('rule', []).items():
                output.append(self._white('{}: {}'.format(rule, data['count'])))
            self._close_group()
        if result.results_csv_uri:
            output.append(self._white('Download Results CSV:'))
            self._open_group()
            output.append(self._white(result.results_csv_uri))
            self._close_group()
        if result.ruleset_name is not None:
            output.append(self._white('Ruleset Name: {}'.format(result.ruleset_name)))
        if result.yara:
            output.append(self._white('Ruleset Contents:\n{}'.format(result.yara)))
        return self._output(output, write)

    def hunt_deletion(self, result, write=True):
        output = []
        output.append(self._yellow('Successfully deleted Hunt:'))
        output.extend(self.hunt(result, write=False))

        return self._output(output, write)

    def historical_result(self, result, write=True):
        output = []
        output.append(self._blue('Id: {}'.format(result.id)))
        output.append(self._blue('Instance Id: {}'.format(result.instance_id)))
        output.append(self._white('Created at: {}'.format(result.created)))
        output.append(self._white('SHA256: {}'.format(result.sha256)))
        output.append(self._white('Rule: {}'.format(result.rule_name)))
        if result.malware_family:
            output.append(self._red('Malware Family: {result_tags}'.format(result_tags=result.malware_family)))
        if result.polyscore is not None:
            formatter = self._get_score_format(result.polyscore)
            output.append(formatter('PolyScore: {:.20f}'.format(result.polyscore)))
        if result.detections:
            if result.detections['total'] == 0:
                output.append(self._white('Detections: No engines responded to this scan. You can trigger a rescan now.'))
            else:
                malicious = 'Detections: {}/{} engines reported malicious'\
                    .format(result.detections['malicious'], result.detections['total'])
                if result.detections['malicious'] > 0:
                    output.append(self._red(malicious))
                else:
                    output.append(self._white(malicious))
        if result.tags:
            output.append(self._white('Tags: {result_tags}'.format(result_tags=result.tags)))
        if result.download_url:
            output.append(self._white('Download Url: {result_tags}'.format(result_tags=result.download_url)))
        return self._output(output, write)

    def live_result(self, result, write=True):
        output = []
        output.append(self._blue('Id: {}'.format(result.id)))
        output.append(self._blue('Instance Id: {}'.format(result.instance_id)))
        output.append(self._white('Created at: {}'.format(result.created)))
        output.append(self._white('SHA256: {}'.format(result.sha256)))
        output.append(self._white('Rule: {}'.format(result.rule_name)))
        if result.malware_family:
            output.append(self._red('Malware Family: {result_tags}'.format(result_tags=result.malware_family)))
        if result.polyscore is not None:
            formatter = self._get_score_format(result.polyscore)
            output.append(formatter('PolyScore: {:.20f}'.format(result.polyscore)))
        if result.detections:
            if result.detections['total'] == 0:
                output.append(self._white('Detections: No engines responded to this scan. You can trigger a rescan now.'))
            else:
                malicious = 'Detections: {}/{} engines reported malicious'\
                    .format(result.detections['malicious'], result.detections['total'])
                if result.detections['malicious'] > 0:
                    output.append(self._red(malicious))
                else:
                    output.append(self._white(malicious))
        if result.tags:
            output.append(self._white('Tags: {result_tags}'.format(result_tags=result.tags)))
        if result.download_url:
            output.append(self._white('Download Url: {result_tags}'.format(result_tags=result.download_url)))
        return self._output(output, write)

    def ruleset(self, result, write=True, contents=False):
        output = []
        output.append(self._blue('Ruleset Id: {}'.format(result.id)))
        if result.livescan_id:
            output.append(self._yellow('Live Hunt Id: {}'.format(result.livescan_id)))
            output.append(self._white('Live Hunt Created at: {}'.format(result.livescan_created)))
        output.append(self._white('Name: {}'.format(result.name)))
        output.append(self._white('Description: {}'.format(result.description)))
        output.append(self._white('Created at: {}'.format(result.created)))
        output.append(self._white('Modified at: {}'.format(result.modified)))
        if contents:
            output.append(self._white('Ruleset Contents:\n{}'.format(result.yara)))
        return self._output(output, write)

    def tag_link(self, result, write=True):
        output = []
        output.append(self._blue('SHA256: {}'.format(result.sha256)))
        output.append(self._white('First seen: {}'.format(result.first_seen)))
        output.append(self._white('Tags: {}'.format(result.tags)))
        output.append(self._white('Families: {}'.format(result.families)))
        output.append(self._white('Emerging: {}'.format(result.emerging)))
        return self._output(output, write)

    def family(self, result, write=True):
        output = []
        output.append(self._blue('Family: {}'.format(result.name)))
        output.append(self._white('Emerging: {}'.format(result.emerging)))
        return self._output(output, write)

    def tag(self, result, write=True):
        output = []
        output.append(self._blue('Tag: {}'.format(result.name)))
        return self._output(output, write)

    def local_artifact(self, artifact, write=True):
        output = []
        output.append(self._white('Successfully downloaded artifact {} to {}'
                                  .format(artifact.artifact_name, artifact.name)))
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
                output.append(self._white('ImpHash: {}'.format(data['imphash'])))
                output.append(self._white('IPs: {}'.format(", ".join(data['ips']))))
                output.append(self._white('URLs: {}'.format(", ".join(data['urls']))))
                output.append(self._white('TTPs: {}'.format(", ".join(data['ttps']))))
            else:
                output.append(self._white('SHA256: {}'.format(data)))
        return self._output(output, write)
    
    def ioc(self, ioc, write=True):
        output = []
        output.append(self._white('============================= IOC ============================='))
        data = ioc.json
        if type(data) is dict:
            output.append(self._white('ImpHash: {}'.format(data['imphash'])))
            output.append(self._white('IPs: {}'.format(", ".join(data['ips']))))
            output.append(self._white('URLs: {}'.format(", ".join(data['urls']))))
            output.append(self._white('TTPs: {}'.format(", ".join(data['ttps']))))
        else:
            output.append(self._white('SHA256: {}'.format(data)))
        return self._output(output, write)
    
    def known_host(self, ioc_known, write=True):
        output = []
        output.append(self._white('============================= Known IOC ============================='))
        output.append(self._white('ID: {}'.format(ioc_known.json['id'])))
        output.append(self._white('type: {}'.format(ioc_known.json['type'])))
        output.append(self._white('host: {}'.format(ioc_known.json['host'])))
        output.append(self._white('source: {}'.format(ioc_known.json['source'])))
        output.append(self._white('good: {}'.format(ioc_known.json['good'])))
        return self._output(output, write)

    def artifact_metadata(self, instance, write=True, only=None):
        output = []
        output.append(self._white('============================= Metadata Status ============================='))
        output.append(self._blue('Scan id: {}'.format(instance.id)))

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
                output.append('%s: Updated at %s' % (tool, pretty_print_datetime(metadata['updated'])))
        self._close_group()

        return self._output(output, write)

    def sandbox_providers(self, result, write=True):
        output = []
        for provider in result.json['result'].values():
            output.append(self._white('============================= Provider ============================='))
            output.append(self._blue('slug: {}'.format(provider['slug'])))
            output.append(self._white('name: {}'.format(provider['name'])))
            output.append(self._white('tool: {}'.format(provider['tool'])))
            self._open_group()
            for vm in provider['vms'].values():
                output.append(self._white('============================= VM ============================='))
                for k, v in vm.items():
                    output.append(self._white('{}: {}'.format(k, v)))
            self._close_group()
        return self._output(output, write)
    
    def sandbox_task(self, task, write=True):
        output = []
        output.append(self._white('============================= Sandbox Task ============================='))
        output.append(self._blue('id: {}'.format(task.id)))
        output.append(self._blue('sha256: {}'.format(task.sha256)))
        output.append(self._blue('sandbox: {}'.format(task.sandbox)))
        output.append(self._white('created: {}'.format(task.created)))
        output.append(self._white('community: {}'.format(task.community)))
        output.append(self._white('instance id: {}'.format(task.instance_id)))
        output.append(self._white('status: {}'.format(task.status)))

        if task.account_number:
            output.append(self._white('account number: {}'.format(task.account_number)))
        if task.team_account_number:
            output.append(self._white('team account number: {}'.format(task.team_account_number)))

        if task.sandbox_artifacts:
            output.append(self._white('sandbox artifacts:'))
        self._open_group()
        for artifact in task.sandbox_artifacts:
            output_string = '{}: '.format(artifact.type)
            if artifact.name:
                output_string += '{}, '.format(artifact.name)
            if artifact.mimetype:
                output_string += '{}, '.format(artifact.mimetype)
            output_string += 'instance id: {}'.format(artifact.instance_id)
            output.append(self._white(output_string))
        self._close_group()

        if task.report:
            output.append(self._white('report: use `--fmt pretty-json` to see report content'))

        return self._output(output, write)

    def metadata(self, instance, write=True):
        output = []
        output.append(self._white('============================= Metadata ============================='))
        output.append(self._blue('Artifact id: {}'.format(instance.id)))
        output.append(self._white('Created: {}'.format(instance.created)))

        if instance.sha256:
            output.append(self._white('SHA256: {}'.format(instance.sha256)))
        if instance.sha1:
            output.append(self._white('SHA1: {}'.format(instance.sha1)))
        if instance.md5:
            output.append(self._white('MD5: {}'.format(instance.md5)))
        if instance.ssdeep:
            output.append(self._white('SSDEEP: {}'.format(instance.ssdeep)))
        if instance.tlsh:
            output.append(self._white('TLSH: {}'.format(instance.tlsh)))

        if instance.first_seen:
            output.append(self._white('First seen: {}'.format(instance.first_seen)))
        if instance.last_scanned:
            output.append(self._white('Last scanned: {}'.format(instance.last_scanned)))
            # Deprecated
            output.append(self._white('Last seen: {}'.format(instance.last_scanned)))

        if instance.mimetype:
            output.append(self._white('Mimetype: {}'.format(instance.mimetype)))
        if instance.extended_mimetype:
            output.append(self._white('Extended mimetype: {}'.format(instance.extended_mimetype)))
        if instance.malicious:
            output.append(self._white('Malicious: {}'.format(instance.malicious)))
        if instance.benign:
            output.append(self._white('Benign: {}'.format(instance.benign)))
        if instance.total_detections:
            output.append(self._white('Total detections: {}'.format(instance.total_detections)))

        if instance.domains:
            output.append(self._white('Domains:'))
            self._open_group()
            output.append(self._white('{}'.format(', '.join(instance.domains))))
            self._close_group()
        if instance.ipv4:
            output.append(self._white('Ipv4:'))
            self._open_group()
            output.append(self._white('{}'.format(', '.join(instance.ipv4))))
            self._close_group()
        if instance.ipv6:
            output.append(self._white('Ipv6:'))
            self._open_group()
            output.append(self._white('{}'.format(', '.join(instance.ipv6))))
            self._close_group()
        if instance.urls:
            output.append(self._white('Urls:'))
            self._open_group()
            output.append(self._white('{}'.format(', '.join(instance.urls))))
            self._close_group()

        if instance.filenames:
            output.append(self._white('Filenames:'))
            self._open_group()
            output.append(self._white('{}'.format(', '.join(instance.filenames))))
            self._close_group()

        return self._output(output, write)

    def assertions(self, instance, write=True):
        output = []
        output.append(self._white('============================= Assertions Job ============================='))
        output.append(self._blue('Assertions Job id: {}'.format(instance.id)))
        output.append(self._white('Engine id: {}'.format(instance.engine_id)))
        output.append(self._white('Created at: {}'.format(instance.created)))
        output.append(self._white('Start date: {}'.format(instance.date_start)))
        output.append(self._white('End date: {}'.format(instance.date_end)))

        if instance.storage_path is not None:
            output.append(self._white('Download: {}'.format(instance.storage_path)))
            output.append(self._white('True Positive: {}'.format(instance.true_positive)))
            output.append(self._white('True Negative: {}'.format(instance.true_negative)))
            output.append(self._white('False Positive: {}'.format(instance.false_positive)))
            output.append(self._white('False Negative: {}'.format(instance.false_negative)))
            output.append(self._white('Suspicious: {}'.format(instance.suspicious)))
            output.append(self._white('Unknown: {}'.format(instance.unknown)))
            output.append(self._white('Total: {}'.format(instance.total)))

        return self._output(output, write)

    def votes(self, instance, write=True):
        output = []
        output.append(self._white('============================= Votes Job ============================='))
        output.append(self._blue('Votes Job id: {}'.format(instance.id)))
        output.append(self._white('Engine id: {}'.format(instance.engine_id)))
        output.append(self._white('Created at: {}'.format(instance.created)))
        output.append(self._white('Start date: {}'.format(instance.date_start)))
        output.append(self._white('End date: {}'.format(instance.date_end)))

        if instance.storage_path is not None:
            output.append(self._white('Download: {}'.format(instance.storage_path)))
            output.append(self._white('True Positive: {}'.format(instance.true_positive)))
            output.append(self._white('True Negative: {}'.format(instance.true_negative)))
            output.append(self._white('False Positive: {}'.format(instance.false_positive)))
            output.append(self._white('False Negative: {}'.format(instance.false_negative)))
            output.append(self._white('Suspicious: {}'.format(instance.suspicious)))
            output.append(self._white('Unknown: {}'.format(instance.unknown)))
            output.append(self._white('Total: {}'.format(instance.total)))

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
