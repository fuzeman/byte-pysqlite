from __future__ import absolute_import, division, print_function

import os
import subprocess


def detect_environment():
    if os.environ.get('TRAVIS_BUILD_ID'):
        return 'travis'

    return 'release'


def install():
    environment = os.environ.get('BYTE_ENVIRONMENT') or detect_environment()

    if not environment:
        raise Exception('Unable to detect environment, and no environment was provided')

    if environment == 'development':
        return install_development()

    if environment == 'release':
        return install_release()

    if environment == 'travis':
        return install_travis()

    raise Exception('Unknown environment: %s' % (environment,))


def install_development():
    # Install byte packages
    pip_upgrade(
        os.path.abspath('../byte'),
        os.path.abspath('../byte-sqlite')
    )

    # Install additional requirements
    pip_install(
        '-rrequirements.txt',
        '-rtests/requirements.txt'
    )


def install_release():
    # Install requirements
    pip_install(
        '-rrequirements.txt',
        '-rtests/requirements.txt'
    )


def install_travis():
    branch = os.environ.get('TRAVIS_BRANCH')

    if not branch:
        raise Exception('"TRAVIS_BRANCH" environment variable hasn\'t been defined')

    if branch != 'master':
        branch = 'develop'

    # Install byte packages
    pip_upgrade(
        'git+https://github.com/fuzeman/byte.git@%s' % (branch,),
        'git+https://github.com/fuzeman/byte-sqlite.git@%s' % (branch,)
    )

    # Install additional requirements
    pip_install(
        '-rrequirements.txt',
        '-rtests/requirements.txt'
    )


def pip_install(*args):
    execute('pip', 'install', *args)


def pip_upgrade(*args):
    execute('pip', 'install', '--upgrade', *args)


def execute(*args):
    p = subprocess.Popen(list(args), shell=False)
    p.communicate()


if __name__ == '__main__':
    install()
