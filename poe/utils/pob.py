import json
import logging
import os
from pathlib import Path
from shutil import which
from subprocess import PIPE, Popen

from poe.config import settings
from poe.schema import PoBDataSchema, PoBFileType

logger = logging.getLogger('poe.wrapper')


class PoBWrapper:
    def __init__(self, character_name: str, items_data: dict, tree_data: dict) -> None:
        if not which('luajit') or not any(settings.POB_RUNTIME_PATH, settings.POB_SOURCE_PATH):
            raise ModuleNotFoundError('luajit is not installed for current system or env variables are misconfigured')
        self.save_pob_file(character_name, PoBFileType.ITEMS, items_data)
        self.save_pob_file(character_name, PoBFileType.TREE, tree_data)

    @property
    def lua_scipt_path(self):
        return os.path.join(Path(__file__).resolve().parent, 'cli.lua')

    @property
    def env(self):
        new_env = os.environ.copy()
        new_env['LUA_PATH'] = ';'.join([
            f'{settings.POB_RUNTIME_PATH}/lua/?.lua',
            f'{settings.POB_RUNTIME_PATH}/lua/?/init.lua'
        ])
        return new_env

    def save_pob_file(self, character_name: str, file_type: PoBFileType, data: dict):
        try:
            tmp_path = os.path.join(settings.TEMP_FOLDER, f'{character_name}.{file_type}.json')
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as exc:
            logger.error(exc)

    def get_character_pob_data(self, character_name: str) -> PoBDataSchema:
        args = ['luajit', self.lua_scipt_path, character_name]
        with Popen(
            args=args, cwd=settings.POB_SOURCE_PATH, env=self.env, stdin=PIPE,
            stdout=PIPE, stderr=PIPE, universal_newlines=True, bufsize=1
        ) as proc:
            returncode = proc.wait(timeout=30)

            if returncode == 0:
                output_file = os.path.join(settings.TEMP_FOLDER, f'{character_name}.output.json')
                with open(output_file, 'r', encoding='utf-8') as f:
                    pob_data = json.load(f)
                    return PoBDataSchema(**pob_data)
            else:
                raise Exception(f'POB process ended with status code: {returncode}. {proc.stderr.read()}')
