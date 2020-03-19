from __future__ import absolute_import, unicode_literals
import sys
import functools
import json
from . import base
from polyswarm_api import const


# TODO rewrite some of this to be not terrible
def is_colored(fn):
    prefix, suffix = {
                '_red': ('\033[91m', '\033[0m'),
                '_yellow': ('\033[93m', '\033[0m'),
                '_green': ('\033[92m', '\033[0m'),
                '_white': ('', ''),
                '_blue': ('\033[94m', '\033[0m'),
                '_open_group': ('\033[94m', '\033[0m'),
    }.get(fn.__name__, ('', ''))

    @functools.wraps(fn)
    def wrapper(self, text):
        if self.color:
            return prefix + fn(self, text) + suffix
        else:
            return fn(self, text)
    return wrapper


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
            self.out.write('\n'.join(output) + '\n\n')
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
        output.append(self._white('Last seen: {}'.format(artifact.last_seen)))
        return self._output(output, write)

    def artifact_instance(self, instance, write=True, timeout=False):
        output = []
        output.append(self._white('============================= Artifact Instance ============================='))
        output.append(self._white('Scan permalink: {}'.format(instance.permalink)))
        detections = 'Detections: {}/{} engines reported malicious'\
            .format(len(instance.detections), len(instance.valid_assertions))
        if len(instance.detections) > 0:
            output.append(self._red(detections))
        else:
            output.append(self._white(detections))
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
        elif timeout:
            output.append(self._yellow('Status: Lookup timed-out, please retry'))
        else:
            output.append(self._white('Status: Running'))
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
        output.append(self._blue('Ruleset Id: {}'.format(result.id)))
        output.append(self._green('Sha256: {}'.format(result.sha256)))
        output.append(self._white('Created at: {}'.format(result.created)))
        output.append(self._white('Updated at: {}'.format(result.updated)))
        output.append(self._white('First seen: {}'.format(result.first_seen)))
        output.append(self._white('Tags:: {}'.format(result.tags)))
        output.append(self._white('Families: {}'.format(result.families)))
        return self._output(output, write)

    def family(self, result, write=True):
        output = []
        output.append(self._blue('Family Id: {}'.format(result.id)))
        output.append(self._blue('Name: {}'.format(result.name)))
        output.append(self._white('Emerging: {}'.format(result.emerging)))
        return self._output(output, write)

    def tag(self, result, write=True):
        output = []
        output.append(self._blue('Tag Id: {}'.format(result.id)))
        output.append(self._blue('Name: {}'.format(result.name)))
        return self._output(output, write)

    def local_artifact(self, artifact, write=True):
        output = []
        output.append(self._white('Successfully downloaded artifact {} to {}'
                                  .format(artifact.artifact_name, artifact.name)))
        return self._output(output, write)

    def usage_exceeded(self):
        self.out.write(self._red(const.USAGE_EXCEEDED_MESSAGE)+'\n')

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
        if instance.last_seen:
            output.append(self._white('Last seen: {}'.format(instance.last_seen)))
        if instance.mimetype:
            output.append(self._white('Mimetype: {}'.format(instance.mimetype)))
        if instance.extended_mimetype:
            output.append(self._white('Extended mimetype: {}'.format(instance.tlsh)))
        if instance.detections:
            output.append(self._white('Detections: {}'.format(instance.detections)))
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

        return self._output(output, write)


    @is_colored
    @is_grouped
    def _white(self, text):
        return '%s' % text

    @is_colored
    @is_grouped
    def _yellow(self, text):
        return '%s' % text

    @is_colored
    @is_grouped
    def _red(self, text):
        return '%s' % text

    @is_colored
    @is_grouped
    def _blue(self, text):
        return '%s' % text

    @is_colored
    @is_grouped
    def _green(self, text):
        return '%s' % text

    def _open_group(self):
        self._depth += 1

    def _close_group(self):
        self._depth -= 1
