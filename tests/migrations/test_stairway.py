"""
Test can find forgotten downgrade methods, undeleted data types in downgrade
methods, typos and many other errors.
Does not require any maintenance - you just add it once to check 80% of typos
and mistakes in migrations forever.
"""
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Optional, Union

import pytest
from alembic.command import downgrade, upgrade
from alembic.config import Config
from alembic.script import Script, ScriptDirectory
from configargparse import Namespace

PROJECT_PATH = Path(__file__).parents[2].resolve()

def make_alembic_config(cmd_opts: Union[Namespace, SimpleNamespace],
                        base_path: str = PROJECT_PATH) -> Config:

    # Replace path to alembic.ini file to absolute
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name,
                    cmd_opts=cmd_opts)

    # Replace path to alembic folder to absolute
    alembic_location = config.get_main_option('script_location')
    if not os.path.isabs(alembic_location):
        config.set_main_option('script_location',
                               os.path.join(base_path, alembic_location))
    if cmd_opts.pg_url:
        config.set_main_option('sqlalchemy.url', cmd_opts.pg_url)

    return config


def alembic_config_from_url(pg_url: Optional[str] = None) -> Config:
    ''' Provides Python object, representing alembic.ini file. '''

    cmd_options = SimpleNamespace(
        config='alembic.ini', name='alembic', pg_url=pg_url,
        raiseerr=False, x=None,
    )

    return make_alembic_config(cmd_options)


def get_revisions():
    # Create Alembic configuration object
    # (we don't need database for getting revisions list)
    config = alembic_config_from_url()

    # Get directory object with Alembic migrations
    revisions_dir = ScriptDirectory.from_config(config)

    # Get & sort migrations, from first to last
    revisions = list(revisions_dir.walk_revisions('base', 'heads'))
    revisions.reverse()
    return revisions


@pytest.mark.parametrize('revision', get_revisions())
def test_migrations_stairway(alembic_config: Config, revision: Script):
    upgrade(alembic_config, revision.revision)

    # We need -1 for downgrading first migration (its down_revision is None)
    downgrade(alembic_config, revision.down_revision or '-1')
    upgrade(alembic_config, revision.revision)
