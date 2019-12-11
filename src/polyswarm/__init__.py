import logging

import click
from click_log import core


# Creating our own handler class that always uses stderr to output logs.
# This way, we can avoid mixing logging information with actual output from
# the command line client.
class MyClickHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            click.echo(msg, err=True)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


core._default_handler = MyClickHandler()
core._default_handler.formatter = core.ColorFormatter()

# adding color to INFO log messages as well
core.ColorFormatter.colors['info'] = dict(fg='green')
