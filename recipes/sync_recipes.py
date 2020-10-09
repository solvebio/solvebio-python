import click
import recipes.sync_recipe_utils as sr
import solvebio as sb

__version__ = '1.0.0'


@click.group()
@click.option('--access-token', help='Manually provide a SolveBio Access Token')
@click.option('--api-host', help='Override the default SolveBio API host')
@click.option('--api-key', help='Manually provide a SolveBio API key')
@click.pass_context
def sync_recipes(ctx, api_key=None, access_token=None, api_host=None):

    sb.login(api_key=api_key, access_token=access_token, api_host=api_host,
             version=__version__, name="SolveBio Recipes")
    user = sb.User.retrieve()

    click.echo('Logged-in as: {} ({})'.format(
        user.full_name, user.id))


@sync_recipes.command()
@click.argument('recipes_file', nargs=1)
@click.option('--name', help='Name of the recipe')
@click.option('--all', is_flag=True,
              help='Apply the selected mode to all recipes in YAML file')
@click.pass_context
def sync(ctx, recipes_file=None, all=False, name=None):
    if (all and name):
        ctx.fail("Only one of the options --name or --all should be present!")
    elif not any([all, name]):
        ctx.fail("One of the options --name or --all should be present!")

    try:
        yml_recipes = sr.load_recipes_from_yaml(recipes_file)
        if all:
            for yml_recipe in yml_recipes:
                prompt_sync(yml_recipe)
        else:
            yml_recipe = sr.get_recipe_by_name_from_yml(yml_recipes, name)
            if yml_recipe:
                prompt_sync(yml_recipe)

    except Exception as e:
        ctx.fail(e)
        ctx.fail('Invalid path to YAML file with the recipes. Provide the full path to a '
                 'yaml_with_recipes.yml file containing a description of recipes.')


@sync_recipes.command()
@click.argument('recipes_file', nargs=1, required=False)
@click.option('--name', help='Name of the recipe')
@click.option('--all', is_flag=True,
              help='Apply the selected mode to all recipes in YAML file')
@click.pass_context
def delete(ctx, recipes_file, all=False, name=None):
    if (all and name):
        ctx.fail("Only one of the options --name or --all should be present!")
    elif not any([all, name]):
        ctx.fail("One of the options --name or --all should be present!")

    try:
        yml_recipes = sr.load_recipes_from_yaml(recipes_file)
        if all:
            for yml_recipe in yml_recipes:
                prompt_delete("{} (v{})".format(yml_recipe['name'], yml_recipe['version']))
        else:
            prompt_delete(name)

    except Exception as e:
        ctx.fail(e)
        ctx.fail('Invalid path to YAML file with the recipes. Provide the full path to a '
                 'yaml_with_recipes.yml file containing a description of recipes.')


@sync_recipes.command()
@click.argument('recipes_file', nargs=1)
@click.option('--account-recipes', is_flag=True, help='Export recipes for logged in account')
@click.option('--public-recipes', is_flag=True, help='Export public recipes')
@click.pass_context
def export(ctx, recipes_file, account_recipes, public_recipes):
    if account_recipes:
        user = sb.User.retrieve()
        click.echo("Exporting recipes for account {} to {}."
                   .format(user['account']['id'], recipes_file))
        sr.export_recipes_to_yaml(sr.get_account_recipes(user), recipes_file)
        click.echo("Recipes successfully exported!")
    elif public_recipes:
        click.echo("Exporting all public recipes to {}.".format(recipes_file))
        sr.export_recipes_to_yaml(sr.get_public_recipes(), recipes_file)
        click.echo("Recipes successfully exported!")
    else:
        ctx.fail("Export mode should be used with --account-recipes or --public-recipes!")
    return


def prompt_sync(yml_recipe):
    if sb.DatasetTemplate.all(name="{} (v{})".format(yml_recipe['name'], yml_recipe['version'])):
        if click.confirm("Are you sure you want to sync {} (v{}) recipe?"
                                 .format(yml_recipe['name'], yml_recipe['version'])):
            sr.sync_recipe(yml_recipe)
        else:
            click.echo("Aborted.")
    elif click.confirm("Are you sure you want to create {} (v{}) recipe?"
                               .format(yml_recipe['name'], yml_recipe['version'])):
        sr.create_recipe(yml_recipe)
    else:
        click.echo("Aborted.")


def prompt_delete(name):
    if sb.DatasetTemplate.all(name=name):
        if click.confirm("Are you sure you want to delete {} recipe?".format(name)):
            sr.delete_recipe(name)
        else:
            click.echo("Aborted.")
    else:
        click.echo("Requested recipe {} doesn't exist in SolveBio!".format(name))


if __name__ == '__main__':
    sync_recipes()
