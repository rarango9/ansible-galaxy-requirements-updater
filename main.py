#!/usr/bin/env python3
# ======================================================================
# Updates the Roles and Collections with versions for an
# Ansible Galaxy Requirements file to the latest available versions.
# ======================================================================

from argparse import ArgumentParser
import pathlib


from json import loads
from sys import exit
from urllib.error import URLError
from urllib.request import Request, urlopen
from yaml import dump, safe_load, SafeDumper, YAMLError


prefix = '\033[36;1m❱❱\033[0m'


class RequirementsDumper(SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(RequirementsDumper, self).increase_indent(flow, False)

    def write_line_break(self, data=None):
        super().write_line_break(data)
        if len(self.indents) == 1 and self.line != 1:
            super().write_line_break()


def collection_latest_version(author, name):
    try:
        url = F"https://galaxy.ansible.com/api/v2/collections/{author}/{name}/"
        data = loads(urlopen(Request(url)).read())

        if 'code' not in data:
            return data['latest_version']['version']
        else:
            return None

    except URLError as e:
        print(F"Failed looking up: {author}.{name}")
        print(e)
        exit(1)


def role_latest_version(author, name):
    try:
        url = F"https://galaxy.ansible.com/api/v1/roles/?owner__username={author}&name={name}"
        data = loads(urlopen(Request(url)).read())

        if 'results' in data and len(data['results']) == 1:
            return data['results'][0]['summary_fields']['versions'][0]['name']
        return None

    except URLError as e:
        print(F"Failed looking up: {author}.{name}")
        print(e)
        exit(1)


def main():
    # Parse arguments passed to the script and validate options.
    p = ArgumentParser()
    p.add_argument('file_path')
    p.add_argument('-w', '--write', action='store_true')
    args = p.parse_args()

    print('┌─┐┌┐┌┌─┐┬┌┐ ┬  ┌─┐  ┌─┐┌─┐┬  ┌─┐─┐ ┬┬ ┬  ┬─┐┌─┐┌─┐ ┬ ┬┬┬─┐┌─┐┌┬┐┌─┐┌┐┌┌┬┐┌─┐  ┬ ┬┌─┐┌┬┐┌─┐┌┬┐┌─┐┬─┐',
          '├─┤│││└─┐│├┴┐│  ├┤   │ ┬├─┤│  ├─┤┌┴┬┘└┬┘  ├┬┘├┤ │─┼┐│ ││├┬┘├┤ │││├┤ │││ │ └─┐  │ │├─┘ ││├─┤ │ ├┤ ├┬┘',
          '┴ ┴┘└┘└─┘┴└─┘┴─┘└─┘  └─┘┴ ┴┴─┘┴ ┴┴ └─ ┴   ┴└─└─┘└─┘└└─┘┴┴└─└─┘┴ ┴└─┘┘└┘ ┴ └─┘  └─┘┴  ─┴┘┴ ┴ ┴ └─┘┴└─',
          sep='\n', end='\n\n')

    # Get the absolute path to the requirements file.
    abs_path = pathlib.Path(args.file_path).resolve()

    # Load the old contents and print it out.
    try:
        with open(abs_path, 'r') as file:
            old_contents = safe_load(file)
            print(prefix, 'Old Contents:')
            print(dump(old_contents,
                       Dumper=RequirementsDumper,
                       indent=2,
                       explicit_start=True,
                       sort_keys=False))
    except (FileNotFoundError, YAMLError) as e:
        print(e)
        exit(1)

    # Loop through the roles and collections
    print(prefix, 'Checking for Latest Versions:')
    new_contents = {}

    for key, values in old_contents.items():
        new_contents[key] = []

        for value in values:
            if isinstance(value, dict) and 'version' in value:
                author, name = value['name'].split('.')

                if key == 'collections':
                    latest = collection_latest_version(author, name)
                elif key == 'roles':
                    latest = role_latest_version(author, name)
                else:
                    print('Only roles and collections supported')
                    exit(1)

                if latest is not None and latest != value['version']:
                    old = value['version']
                    value['version'] = latest
                    print(F"{author}.{name} : {old} --> "
                          F"\033[33;1m{latest}\033[0m")
                else:
                    if latest is None:
                        print(F"{author}.{name} : Could not find in Galaxy")
                    else:
                        print(F"{author}.{name} : {value['version']}")

                new_contents[key].append(value)

            else:
                new_contents[key].append(value)
                module = value['name'] if isinstance(value, dict) else value
                print(module, ': No defined version')
    print()

    print(prefix, 'New Contents:')
    print(dump(new_contents,
               Dumper=RequirementsDumper,
               indent=2,
               explicit_start=True,
               sort_keys=False))

    # Write the contents out to the file or display a reminder that you can.
    if args.write:
        with open(abs_path, 'w+') as f:
            dump(new_contents,
                 f,
                 Dumper=RequirementsDumper,
                 indent=2,
                 explicit_start=True,
                 sort_keys=False)
            print(prefix, 'New requirements written to file')
    else:
        print(prefix, 'Review the changes above (Any changes are in yellow)')
        print("   To write the changes, re-run with '-w' or '--write'")


if __name__ == '__main__':
    main()
