import click
import recipes.sync_recipe_utils as sr
import solvebio as sb


@click.command()
@click.argument('recipes_file', nargs=1)
@click.option('--mode', type=click.Choice(['sync', 'delete', 'export'], case_sensitive=False),
              help='`sync`, `delete` or `export` mode', required=True)
@click.option('--name', help='Name of the recipe')
@click.option('--all', is_flag=True,
              help='Apply the selected mode to all recipes in YAML file')
@click.option('--account-recipes', is_flag=True, help='Export recipes for logged in account')
@click.option('--public-recipes', is_flag=True, help='Export public recipes')
@click.option('--access-token', help='Manually provide a SolveBio Access Token')
@click.option('--api-host', help='Override the default SolveBio API host')
@click.option('--api-key', help='Manually provide a SolveBio API key')
@click.pass_context
def sync_recipes(ctx, recipes_file, mode, account_recipes=None, public_recipes=None, name=None,
                 all=False, api_key=None, access_token=None, api_host=None):
    """
    Syncs, deletes or exports recipes on SolveBio
    """

    sb.login(api_key=api_key, access_token=access_token, api_host=api_host)
    user = sb.User.retrieve()

    click.echo('Logged-in as: {} ({})'.format(
        user.full_name, user.id))

    if mode == "export":
        if account_recipes:
            click.echo("Exporting recipes for account {} to {}.".format(user['account']['id'], recipes_file))
            sr.export_recipes_to_yaml(sr.get_account_recipes(user), recipes_file)
            click.echo("Recipes successfully exported!")
        elif public_recipes:
            click.echo("Exporting all public recipes to {}.".format(recipes_file))
            sr.export_recipes_to_yaml(sr.get_public_recipes(), recipes_file)
            click.echo("Recipes successfully exported!")
        else:
            ctx.fail("Export mode should be used with --account-recipes or --public-recipes!")
        return

    if (all and name):
        ctx.fail("Only one of the options --name or --all should be present!")
    elif not any([all, name]):
        ctx.fail("One of the options --name or --all should be present!")

    try:
        yml_recipes = sr.load_recipes_from_yaml(recipes_file)
        if all and mode == 'sync':
            for yml_recipe in yml_recipes:
                prompt_sync(yml_recipe)
        elif all and mode == 'delete':
            for yml_recipe in yml_recipes:
                prompt_delete("{} (v{})".format(yml_recipe['name'], yml_recipe['version']))
        elif name and mode == 'sync':
            yml_recipe = sr.get_recipe_by_name_from_yml(yml_recipes, name)
            prompt_sync(yml_recipe)
        elif name and mode == 'delete':
            prompt_delete(name)

    except Exception as e:
        ctx.fail(e)
        ctx.fail('Invalid path to YAML file with the recipes. Provide the full path to a '
                 'yaml_with_recipes.yml file containing a description of recipes.')


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
