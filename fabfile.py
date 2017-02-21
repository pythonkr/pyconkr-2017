# -*- coding: utf-8 -*-
import os

from fabric.api import local, run, cd, prefix, env, sudo, settings, shell_env
from deploy import server

env.host_string = '{user}@{host}:{port}'.format(
                                            user=env.pycon_user,
                                            host=env.pycon_host,
                                            port=env.pycon_port
                                            )


def deploy(target='dev', sha1=None):
    if sha1 is None:
        # get current working git sha1
        sha1 = local('git rev-parse HEAD', capture=True)
    # server code reset to current working sha1
    home_dir = '/home/pyconkr/{target}.pycon.kr/pyconkr-2016'.format(target=target)

    if target == 'dev':
        python_env = '/home/pyconkr/.pyenv/versions/pyconkr-2016-dev'
    else:
        python_env = '/home/pyconkr/.pyenv/versions/pyconkr-2016'

    with settings(cd(home_dir), shell_env(DJANGO_SETTINGS_MODULE='pyconkr.settings_prod')):
        sudo('git fetch --all -p', user='pyconkr')
        sudo('git reset --hard ' + sha1, user='pyconkr')
        sudo('bower install', user='pyconkr')
        sudo('%s/bin/pip install -r requirements.txt' % python_env, user='pyconkr')
        sudo('%s/bin/python manage.py compilemessages' % python_env, user='pyconkr')
        sudo('%s/bin/python manage.py migrate' % python_env, user='pyconkr')
        sudo('%s/bin/python manage.py collectstatic --noinput' % python_env, user='pyconkr')
        # worker reload
        run('echo r > /var/run/pyconkr-2016-%s.fifo' % target)

def flatpages_mig(direction='www'):
    dev_env = '/home/pyconkr/.pyenv/versions/pyconkr-2016-dev/bin/python'
    www_env = '/home/pyconkr/.pyenv/versions/pyconkr-2016/bin/python'
    from_env, to_env = (dev_env, www_env) if direction=='www' else (www_env, dev_env)
    dev_dir = '/home/pyconkr/dev.pycon.kr/pyconkr-2016'
    www_dir = '/home/pyconkr/www.pycon.kr/pyconkr-2016'
    from_dir, to_dir = (dev_dir, www_dir) if direction=='www' else (www_dir, dev_dir)
    with settings(cd(from_dir),
            shell_env(DJANGO_SETTINGS_MODULE='pyconkr.settings_prod')
            ):
        sudo('{python} manage.py dumpdata --indent 2 flatpages -o {fixture_to}'.format(
            fixture_to=os.path.join(to_dir, 'pyconkr', 'fixtures', 'flatpages.json'),
            python=from_env))
    with settings(cd(to_dir),
            shell_env(DJANGO_SETTINGS_MODULE='pyconkr.settings_prod')
            ):
        sudo('{python} manage.py loaddata flatpages'.format(
             python=to_env))
