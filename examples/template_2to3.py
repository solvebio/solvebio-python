"""
Convert a template's expressions to Python 3.

This script will convert all expressions in a template to Python 3 using the 2to3 tool.
It will also show a diff of the changes detected and optionally save the changes to a new template.

Please install the following dependencies for best results:


    pip install solvebio click black


## Usage

Perform a diff of the changes detected in a template:

    python template_2to3.py YOUR_TEMPLATE_ID --api-host https://API_HOST.aws.quartz.bio --diff


Format the diff using Black:

    python template_2to3.py YOUR_TEMPLATE_ID --api-host https://API_HOST.aws.quartz.bio --diff --format-diff


Save a new copy of the template with the upgraded Python 3 expression:

    python template_2to3.py YOUR_TEMPLATE_ID --api-host https://API_HOST.aws.quartz.bio --save


Overwrite the existing template with upgraded Python 3 expression:

    python template_2to3.py YOUR_TEMPLATE_ID --api-host https://API_HOST.aws.quartz.bio --save --overwrite


"""

import solvebio
import click
import subprocess
import os
import re
import difflib
import tempfile


def convert_to_python3(code):
    # Run 2to3 on the given code
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        process = subprocess.Popen(
            ["2to3", "-w", f.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            # Successfully converted
            with open(f.name, "r") as read_f:
                new_code = read_f.read()
        else:
            # Conversion failed
            print(f"Error: {stderr}")
            new_code = "FAILED TO CONVERT"

        f.close()
        os.remove(f.name)

    return new_code


def diff_expressions(old, new):
    diff = list(difflib.ndiff(old.splitlines(), new.splitlines()))
    return "\n".join(diff)


def format_expression(code):
    try:
        import black
    except ImportError:
        print("Black is not installed. Please install it using 'pip install black'.")
        return code

    try:
        mode = black.Mode(line_length=120, target_versions={black.TargetVersion.PY38})
        formatted_code = black.format_str(code, mode=mode)
        return formatted_code
    except black.NothingChanged:
        return code


@click.command()
@click.argument("template_id")
@click.option("--api-host", default="https://api.solvebio.com")
@click.option("--diff", is_flag=True)
@click.option("--format-diff", is_flag=True)
@click.option("--save", is_flag=True)
@click.option("--overwrite", is_flag=True)
def convert_template(
    template_id, api_host, diff=False, format_diff=False, save=False, overwrite=False
):
    """
    Convert a template's expressions to Python 3.

    Arguments:

        - TEMPLATE_ID: The ID of the template to convert.

    Options:

        --diff: Show a diff of the changes detected.
        --format-diff: Format the diff output using Black.
        --save: Save the changes to a new template.
        --overwrite: Overwrite the existing template with the new expressions.

    """

    solvebio.login(api_host=api_host)

    if not save:
        print(
            "Running in dry-run mode. Use --save to save changes to a new template and "
            "--overwrite to modify the template in-place."
        )

    # Retrieve a template from EDP
    template = solvebio.DatasetTemplate.retrieve(template_id)
    # Convert each field to Python 3
    for field in template.fields:
        if not field["expression"]:
            continue

        # Remove linebreaks and consecutive spaces from code snippet
        old_expression = re.sub(
            r"\s+", " ", field["expression"].replace("\n", " ")
        ).strip()
        new_expression = convert_to_python3(old_expression)
        if new_expression != old_expression:
            # Save the new expression
            field["expression"] = new_expression

            # Show a "diff" format for the difference detected
            print(f"Field {field['name']} changes detected")

            if diff:
                if format_diff:
                    old_expression = format_expression(old_expression)
                    new_expression = format_expression(new_expression)

                print(diff_expressions(old_expression, new_expression))
                print()

    if save:
        if overwrite:
            print(
                f"Ovewriting existing template {template.id} with Python 3 expressions."
            )
            template.save()
        else:
            print("Creating a new template with Python 3 expressions.")
            template.name = f"{template.name} py3"
            solvebio.DatasetTemplate.create(**template)

        print(f"Template {template.id} saved with Python 3 expressions.")


if __name__ == "__main__":
    convert_template()
