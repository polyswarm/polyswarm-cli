from __future__ import absolute_import
import logging

import click


from polyswarm.client import utils
from polyswarm.client.report import SECTIONS

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with the Polyswarm reporting templates system.')
def report_template():
    pass


@report_template.command('create', short_help='Create a report template.')
@click.argument('template_name', type=click.STRING)
@click.option('--is-default', type=click.BOOL, is_flag=True, default=False)
@click.option('--primary-color', type=click.STRING)
@click.option('--footer-text', type=click.STRING)
@click.option('--last-page-text', type=click.STRING)
@click.option('--last-page-text-file', type=click.Path(exists=True), help='File with last page text.')
@click.option('--includes',
              help=f'Comma-separated list of sections to include in the report. Can be one ore more of: {SECTIONS}',
              multiple=True,
              callback=lambda _,o,x: x[0].split(',') if len(x) == 1 else x)
@click.option('--excludes',
              help=f'Comma-separated list of sections to exclude in the report. Can be one ore more of: {SECTIONS}',
              multiple=True,
              callback=lambda _,o,x: x[0].split(',') if len(x) == 1 else x)
@click.pass_context
def create(ctx, template_name, is_default, primary_color, footer_text, last_page_text, last_page_text_file, includes, excludes):
    api = ctx.obj['api']
    output = ctx.obj['output']
    if last_page_text_file:
        if last_page_text:
            raise click.BadOptionUsage('--last-page-text-file',
                                       'Cannot use both --last-page-text and --last-page-text-file')
        with open(last_page_text_file, 'r') as f:
            last_page_text = f.read()
    output.report_template(api.report_template_create(template_name=template_name,
                                                  is_default=is_default,
                                                  primary_color=primary_color,
                                                  footer_text=footer_text,
                                                  last_page_text=last_page_text,
                                                  includes=includes if includes else None,
                                                  excludes=excludes if excludes else None))


@report_template.command('get', short_help='Fetch a report template.')
@click.argument('template-id', callback=utils.validate_id)
@click.pass_context
def get(ctx, template_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.report_template(api.report_template_get(id=template_id))


@report_template.command('delete', short_help='Delete a report template.')
@click.argument('template-id', type=click.INT, required=True)
@click.pass_context
def delete(ctx, template_id):
    api = ctx.obj['api']
    api.report_template_delete(id=template_id)
    click.echo('Template deleted')


@report_template.command('list', short_help='List all templates.')
@click.pass_context
def list_rules(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for template in api.report_template_list():
        output.report_template(template)
