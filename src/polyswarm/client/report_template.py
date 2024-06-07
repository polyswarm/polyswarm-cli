import logging
import os

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
@click.pass_context
def create(ctx, template_name, is_default, primary_color,
           footer_text, last_page_text, last_page_text_file, includes):
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
                                                      includes=includes if includes else None))


@report_template.command('update', short_help='Edit a report template.')
@click.argument('template-id', callback=utils.validate_id)
@click.option('--template-name', type=click.STRING)
@click.option('--is-default', type=click.BOOL, is_flag=True, help='Make the report template is default or not.')
@click.option('--primary-color', type=click.STRING)
@click.option('--footer-text', type=click.STRING)
@click.option('--last-page-text', type=click.STRING)
@click.option('--last-page-text-file', type=click.Path(exists=True), help='File with last page text.')
@click.option('--includes',
              help=f'Comma-separated list of sections to include in the report. Can be one ore more of: {SECTIONS}',
              multiple=True,
              callback=lambda _,o,x: x[0].split(',') if len(x) == 1 else x)
@click.pass_context
def update(ctx, template_id, template_name, is_default, primary_color,
           footer_text, last_page_text, last_page_text_file, includes):
    api = ctx.obj['api']
    output = ctx.obj['output']
    if last_page_text_file:
        if last_page_text:
            raise click.BadOptionUsage('--last-page-text-file',
                                       'Cannot use both --last-page-text and --last-page-text-file')
        with open(last_page_text_file, 'r') as f:
            last_page_text = f.read()
    output.report_template(api.report_template_update(template_id=template_id,
                                                      template_name=template_name,
                                                      is_default=is_default,
                                                      primary_color=primary_color,
                                                      footer_text=footer_text,
                                                      last_page_text=last_page_text,
                                                      includes=includes if includes else None))


@report_template.command('get', short_help='Fetch a report template.')
@click.argument('template-id', callback=utils.validate_id)
@click.pass_context
def get(ctx, template_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.report_template(api.report_template_get(template_id=template_id))


@report_template.command('delete', short_help='Delete a report template.')
@click.argument('template-id', type=click.INT, required=True)
@click.pass_context
def delete(ctx, template_id):
    api = ctx.obj['api']
    api.report_template_delete(template_id=template_id)
    click.echo('Template deleted')


@report_template.command('list', short_help='List all templates.')
@click.option('--is-default', type=click.BOOL, is_flag=True, default=False)
@click.pass_context
def list_templates(ctx, is_default):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for template in api.report_template_list(is_default=is_default):
        output.report_template(template)


@report_template.command('logo-download', short_help='Download the template logo.')
@click.argument('template-id', type=click.INT, required=True)
@click.option('-d', '--destination', type=click.Path(file_okay=False),
              help='Path where to store the downloaded file.', default=os.getcwd())
@click.pass_context
def logo_download(ctx, template_id, destination):
    api = ctx.obj['api']
    output = ctx.obj['output']
    report_object = api.report_template_logo_download(template_id, destination)
    output.local_artifact(report_object)


@report_template.command('logo-delete', short_help='Delete the template logo.')
@click.argument('template-id', type=click.INT, required=True)
@click.pass_context
def logo_delete(ctx, template_id):
    api = ctx.obj['api']
    api.report_template_logo_delete(template_id=template_id)
    click.echo('Template logo deleted')


@report_template.command('logo-upload', short_help='Upload template logo.')
@click.argument('template-id', type=click.INT, required=True)
@click.argument('path', type=click.Path(exists=True), required=True)
@click.pass_context
def logo_upload(ctx, template_id, path):
    file_extension = path.split('.')[-1]
    if file_extension not in ('png', 'jpg', 'jpeg'):
        raise click.BadArgumentUsage('Only PNG and JPEG images are supported.')

    api = ctx.obj['api']
    output = ctx.obj['output']
    content_type = 'image/png' if file_extension == 'png' else 'image/jpeg'
    with open(path, 'rb') as logo_file:
        template = api.report_template_logo_upload(template_id, logo_file, content_type)
        output.report_template(template)
