from __future__ import absolute_import
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
        output.append(self._green('SHA256: {hash}'.format(hash=artifact.sha256)))
        output.append(self._white('SHA1: {hash}'.format(hash=artifact.sha1)))
        output.append(self._white('MD5: {hash}'.format(hash=artifact.md5)))
        output.append(self._white('File type: mimetype: {mimetype}, extended_info: {extended_type}'.
                                  format(mimetype=artifact.mimetype, extended_type=artifact.extended_type)))

        if artifact.metadata:
            if artifact.metadata.hash:
                h = artifact.metadata.hash
                if 'ssdeep' in h:
                    output.append(self._white('SSDEEP: {}'.format(h['ssdeep'])))
                if 'tlsh' in h:
                    output.append(self._white('TLSH: {}'.format(h['tlsh'])))
                if 'authentihash' in h:
                    output.append(self._white('Authentihash: {}'.format(h['authentihash'])))
            if artifact.metadata.pefile:
                p = artifact.metadata.pefile
                if 'imphash' in p:
                    output.append(self._white('Imphash: {}'.format(p['imphash'])))
        output.append(self._white('First seen: {first_seen}'.format(first_seen=artifact.first_seen)))
        return self._output(output, write)

    def artifact_instance(self, instance, write=True):
        output = []
        output.extend(self.artifact(instance, write=False))
        output.append(self._white('Filename: {}'.format(instance.filename)))
        if instance.country:
            output.append(self._white('Country: {}'.format(instance.country)))

        if instance.polyscore is not None:
            formatter = self._get_score_format(instance.polyscore)
            output.append(formatter('PolyScore: {:.20f}'.format(instance.polyscore)))

        # only report information if we have scanned the file before
        if instance.permalink:
            output.append(self._white('Scan permalink: {}'.format(instance.permalink)))
        detections = 'Detections: {}/{} engines reported malicious'\
            .format(len(instance.detections), len(instance.valid_assertions))
        if len(instance.detections) > 0:
            output.append(self._red(detections))
        else:
            output.append(self._white(detections))

        for assertion in instance.assertions:
            if assertion.verdict is False:
                output.append(self._green('%s: %s' % (assertion.engine_name, 'Clean')))
            elif assertion.verdict is None or assertion.mask is False:
                output.append(self._blue('%s: %s' % (assertion.engine_name, 'Engine chose not respond to this bounty.')))
            else:
                value = 'Malicious'
                if assertion.metadata:
                    value += ', metadata: %s' % json.dumps(assertion.metadata, sort_keys=True)
                output.append(self._red('%s: %s' % (assertion.engine_name, value)))

        return self._output(output, write)

    def submission(self, submission, write=True):
        output = []
        output.append(self._green('Submission %s' % submission.uuid))
        output.append(self._white('Reference: %s' % submission.permalink))
        output.append(self._white('Community: %s' % submission.community))
        if submission.country:
            output.append(self._white('Country: %s' % submission.country))
        for instance in submission.instances:
            output.append(self._white('============================= Artifact Instance ============================='))
            self._open_group()
            output.extend(self.artifact_instance(instance, write=False))
            output.append('')
            self._close_group()
        return self._output(output, write)

    def hunt(self, result, write=True):
        output = []
        output.append(self._blue('Hunt Id: {}'.format(result.id)))
        if result.active is not None:
            output.append(self._white('Active: {}'.format(result.active)))
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
        output.extend(self.artifact(result.artifact, write=False))
        return self._output(output, write)

    def local_artifact(self, artifact, write=True):
        output = []
        output.append(self._white('Successfully downloaded artifact {} to {}'
                                  .format(artifact.artifact_name, artifact.path)))
        return self._output(output, write)

    def usage_exceeded(self):
        self.out.write(self._red(const.USAGE_EXCEEDED_MESSAGE)+'\n')

    def invalid_rule(self, e):
        self.out.write(self._red('Malformed yara file: {}'.format(e.args[0])+'\n'))

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
