# ansible-galaxy-requirements-updater

Update an Ansible Galaxy requirements file.

# Requirements

- Python3

# Usage:

After locally cloning the repository:

```shell
cd ansible-galaxy-requirements-updater/
./main.py <FILE_PATH>
```

Remotely pull and execute the script:

```shell
curl -s "https://raw.githubusercontent.com/rarango9/ansible-galaxy-requirements-updater/main/main.py" | python3 - "$@" <FILE_PATH>
```

# Maintainers

Rob Arango
