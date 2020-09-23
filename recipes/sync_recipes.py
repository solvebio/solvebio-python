import click
import solvebio as sb
import recipe.sync_recipe_utils as sr


@click.command()
@click.argument('recipes', nargs=1)
@click.option('--api-key', help='SolveBio API key to use')
@click.option('--api-host', help='SolveBio API host to use')
@click.option('--access-token', help='SolveBio access token to use')
@click.option('--mode', type=click.Choice(['sync', 'delete', 'export'], case_sensitive=False),
              help='`sync`, `delete` or `export` mode')
@click.option('--name', help='Name of the recipe')
@click.option('--all', is_flag=True,
              help='Apply the selected mode to all recipes in YAML file')
@click.option('--account-recipes', is_flag=True, help='Export recipes for logged in account')
@click.option('--public-recipes', is_flag=True, help='Export public recipes')
@click.pass_context
def sync_recipes(ctx, recipes, mode, account_recipes=None, public_recipes=None, name=None, all=False, api_key=None, access_token=None, api_host=None):
    """
    Deploys a recipes to SolveBio and export public/account recipes from SolveBio
    Provide the path/to/recipes.yml
    """

    sb.login(api_key=api_key, access_token=access_token, api_host=api_host)
    user = sb.User.retrieve()

    click.echo('Logged-in as: {} ({})'.format(
        user.full_name, user.id))

    if ((all or name) and (account_recipes or public_recipes)) or \
            ((all and name) or (account_recipes and public_recipes)):
        ctx.fail("Only one of the options --name, --all, "
                 "--account-recipes or --public-recipes should be present!")

    if not any([all, name, account_recipes, public_recipes]):
        ctx.fail("One of the options --name, --all, "
                 "--account-recipes or --public-recipes should be present!")

    if mode == "export":
        if account_recipes:
            click.echo("Exporting recipes for account {} to {}.".format(user['account']['id'], recipes))
            sr.export_recipes_to_yaml(sr.get_account_recipes(user), recipes)
            click.echo("Recipes successfully exported!")
        elif public_recipes:
            click.echo("Exporting all public recipes to {}.".format(recipes))
            sr.export_recipes_to_yaml(sr.get_public_recipes(), recipes)
            click.echo("Recipes successfully exported!")
        else:
            ctx.fail("Export mode should be used with --account-recipes or --public-recipes!")
    else:
        try:
            yml_recipes = sr.load_recipes_from_yaml(recipes)
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
    if sb.DatasetTemplate.all(name="{} (v{})"
            .format(yml_recipe['name'], yml_recipe['version'])):
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
