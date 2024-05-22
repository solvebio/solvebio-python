"""
helper functions for managing recipes
"""
import sys
from collections import OrderedDict

import solvebio as sb
import ruamel.yaml as yaml
import click


def create_recipe(description):
    fields = [description['fields']]
    recipe_version = description['version']
    recipe_name = description['name']
    recipe_description = description['description']
    is_public = description['is_public']
    sb.DatasetTemplate.create(
        name="{} (v{})".format(recipe_name, recipe_version),
        description="{}".format(recipe_description) if recipe_description else None,
        template_type="recipe",
        tags=["recipe"],
        is_public=is_public,
        version=recipe_version,
        annotator_params={
            "annotator": "parallel"
        },
        fields=fields
    )


def delete_recipe(recipe_name):
    existing_recipe = sb.DatasetTemplate.all(name=recipe_name)
    if not existing_recipe:
        click.echo("{} doesn't exist!".format(recipe_name))
        return
    for recipe in existing_recipe:
        recipe.delete(force=True)


def sync_recipe(recipe):
    delete_recipe("{} (v{})".format(recipe['name'], recipe['version']))
    create_recipe(recipe)


def get_recipe_by_name_from_yml(all_recipes, name):
    for recipe in all_recipes:
        if recipe["name"] in name and recipe["version"] in name:
            return recipe
    click.echo("{} doesn't exist in the provided YAML file!".format(name))
    return None


def load_recipes_from_yaml(yml_file):
    with open(yml_file, 'r') as yml:
        y = yaml.YAML()
        all_recipes = y.load(yml)
    return all_recipes['recipes']


def get_public_recipes():
    public_recipes = []
    all_templates = sb.DatasetTemplate.all()
    if all_templates:
        for template in all_templates:
            if template['template_type'] == "recipe" and template['is_public']:
                public_recipes.append(template)

    return public_recipes


def get_account_recipes(user):
    account_recipes = []
    all_templates = sb.DatasetTemplate.all()
    if all_templates:
        for template in all_templates:
            if template['template_type'] == "recipe" \
                    and template['account'] == user["account"]["id"]:
                account_recipes.append(template)

    return account_recipes


def export_recipes_to_yaml(recipes, yml_file):
    with open(yml_file, 'w') as outfile:
        class RecipeDumper(yaml.Dumper):
            pass

        class literal(unicode):
            pass

        def _dict_representer(dumper, data):
            return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

        def _literal_representer(dumper, data):
            return dumper.represent_scalar(
                u'tag:yaml.org,2002:str', data, style='|')

        RecipeDumper.add_representer(dict, _dict_representer)
        RecipeDumper.add_representer(literal, _literal_representer)

        # Needed for python2,
        # otherwise: 'item': !!python/unicode "some string" is dumped
        if sys.version_info < (3,0):
            def represent_unicode(dumper, data):
                return dumper.represent_scalar(u'tag:yaml.org,2002:str', data)

            RecipeDumper.add_representer(unicode, represent_unicode)

        yaml_recipes = []
        for r in recipes:
            recipe_expression = literal(unicode(dict(r)['fields'][0]['expression']))
            dict(r)['fields'][0]['expression'] = recipe_expression
            recipe_details = {
                "name": dict(r)['name'],
                "description": dict(r)['description'],
                "template_type": "recipe",
                "is_public": "True" if dict(r)['is_public'] else "False",
                "version": dict(r)['version'],
                "annotator_params": {
                    "annotator": "parallel"
                },
                "fields": {i: dict(r)['fields'][0][i]
                           for i in dict(r)['fields'][0]
                           if i not in ['state', 'dictitems'] and dict(r)['fields'][0][i]}
            }
            yaml_recipes.append(recipe_details)
        yaml.dump({"recipes": yaml_recipes}, outfile, RecipeDumper, encoding='utf-8',
                  default_flow_style=False)

    print("Wrote recipe to file: {}".format(yml_file))
