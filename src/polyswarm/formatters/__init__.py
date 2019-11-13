from .text import TextOutput
from .json import JSONOutput, PrettyJSONOutput
from .hashes import SHA256Output, MD5Output, SHA1Output

formatter_list = [TextOutput, JSONOutput, PrettyJSONOutput, SHA256Output, SHA1Output, MD5Output]

formatters = {cls.name: cls for cls in formatter_list}
