#!/usr/bin/python3
import sys
import os
import shutil
import subprocess
import tempfile
import venv
import argparse

OMIT = ('__pycache__', 'PyInstaller', 'pip', 'setuptools', 'pkg_resources', '__pycache__', 'dist-info', 'egg-info')


def parse():
    '''
    Parse the cli args
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
            'name',
            help='The name of the script to build from the run.py')
    args = parser.parse_args()
    return args.__dict__


class Builder:
    def __init__(self):
        self.opts = parse()
        self.name = self.opts['name']
        self.cwd = os.getcwd()
        self.run = os.path.join(self.cwd, 'run.py')
        self.venv_dir = tempfile.mkdtemp(prefix='pop_', suffix='_venv')
        self.python_bin = os.path.join(self.venv_dir, 'bin', 'python')
        self.vroot = os.path.join(self.venv_dir, 'lib')
        self.all_paths = set()
        self.imports = set()
        self.datas = set()
        self.cmd = f'{self.python_bin} -B -OO -m PyInstaller '
        self.s_path = os.path.join(self.venv_dir, 'bin', self.name)
        self.pyi_args = [
              self.s_path,
              '--log-level=INFO',
              '--noconfirm',
              '--onefile',
              '--clean',
            ]

    def create(self):
        '''
        Make a virtual environment based on the version of python used to call this script
        '''
        venv.create(self.venv_dir, clear=True, with_pip=True)
        pip_bin = os.path.join(self.venv_dir, 'bin', 'pip')
        subprocess.call([pip_bin, 'install', '-r', 'requirements.txt'])
        subprocess.call([pip_bin, 'install', 'PyInstaller'])
        subprocess.call([pip_bin, '-v', 'install', self.cwd])

    def omit(self, test):
        for bad in OMIT:
            if bad in test:
                return True
        return False

    def scan(self):
        '''
        Scan the new venv for files and imports
        '''
        for root, dirs, files in os.walk(self.vroot):
            if self.omit(root):
                continue
            for d in dirs:
                full = os.path.join(root, d)
                if self.omit(full):
                    continue
                self.all_paths.add(full)
            for f in files:
                full = os.path.join(root, f)
                if self.omit(full):
                    continue
                self.all_paths.add(full)

    def to_import(self, path): 
        ret = path[path.index('site-packages') + 14:].replace(os.sep, '.')
        if ret.endswith('.py'):
            ret = ret[:-3]
        return ret

    def to_data(self, path):
        dest = path[path.index('site-packages') + 14:]
        src = path
        if not dest.strip():
            return None
        ret = f'{src}{os.pathsep}{dest}'
        return ret

    def mk_adds(self):
        '''
        make the imports and datas for pyinstaller
        '''
        for path in self.all_paths:
            if not 'site-packages' in path:
                continue
            if os.path.isfile(path):
                if not path.endswith('.py'):
                    continue
                if path.endswith('__init__.py'):
                    # Skip it, we will get the dir
                    continue
                imp = self.to_import(path)
                if imp:
                    self.imports.add(imp)
            if os.path.isdir(path):
                data = self.to_data(path)
                imp = self.to_import(path)
                if imp:
                    self.imports.add(imp)
                if data:
                    self.datas.add(data)

    def mk_cmd(self):
        '''
        Create the pyinstaller command
        '''
        for imp in self.imports:
            self.pyi_args.append(f'--hidden-import={imp}')
        for data in self.datas:
            self.pyi_args.append(f'--add-data={data}')
        for arg in self.pyi_args:
            self.cmd += f'{arg} '

    def pyinst(self):
        shutil.copy(self.run, self.s_path)
        subprocess.call(self.cmd, shell=True)

    def report(self):
        art = os.path.join(self.cwd, 'dist', self.name)
        print(f'Executable created in {art}')
        print('To create a more portable and fully static binary install run staticx against your new build')

    def clean(self):
        shutil.rmtree(self.venv_dir)
        shutil.rmtree(os.path.join(self.cwd, 'build'))
        os.remove(os.path.join(self.cwd, f'{self.name}.spec'))

    def build(self):
        self.create()
        self.scan()
        self.mk_adds()
        self.mk_cmd()
        self.pyinst()
        self.report()
        self.clean()


if __name__ == '__main__':
    builder = Builder()
    builder.build()
