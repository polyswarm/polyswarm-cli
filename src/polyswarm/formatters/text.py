from __future__ import absolute_import, unicode_literals
import sys
import functools
import json

import click

from polyswarm.formatters import base


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
        if score < 0.15:
            return self._white
        elif score < 0.4:
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
        output.append(self._white('First seen: {}'.format(artifact.first_seen)))
        output.append(self._white('Last scanned: {}'.format(artifact.last_scanned)))
        # Deprecated
        output.append(self._white('Last seen: {}'.format(artifact.last_scanned)))
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
        if result.active is not None:
            output.append(self._white('Active: {}'.format(result.active)))
        if result.ruleset_name is not None:
            output.append(self._white('Ruleset Name: {}'.format(result.ruleset_name)))
        output.append(self._white('Created at: {}'.format(result.created)))

        return self._output(output, write)

    def hunt_deletion(self, result, write=True):
        output = []
        output.append(self._yellow('Successfully deleted Hunt:'))
        output.extend(self.hunt(result, write=False))

        return self._output(output, write)

    def hunt_result(self, result, write=True):
        output = []
        output.append(self._white('Match on rule {name}'.format(name=result.rule_name) +
                                  (', tags: {result_tags}'.format(
                                     result_tags=result.tags) if result.tags != '' else '')))
        output.extend(self.artifact_instance(result.artifact, write=False))
        return self._output(output, write)

    def ruleset(self, result, write=True, contents=False):
        output = []
        output.append(self._blue('Ruleset Id: {}'.format(result.id)))
        output.append(self._white('Name: {}'.format(result.name)))
        output.append(self._white('Description: {}'.format(result.description)))
        output.append(self._white('Created at: {}'.format(result.created)))
        output.append(self._white('Modified at: {}'.format(result.modified)))
        if contents:
            output.append(self._white('Contents:\n{}'.format(result.yara)))
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
