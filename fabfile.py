# -*- coding: utf-8 -*-
import os

from fabric.api import local, run, cd, prefix, env, sudo, settings, shell_env

env.use_ssh_config = True
env.user = 'pyconkr'
env.hosts = ['pythonkorea1']

def deploy(target='dev', sha1=None):
    if sha1 is None:
        # get current working git sha1
        sha1 = local('git rev-parse HEAD', capture=True)
    # server code reset to current working sha1
    home_dir = '/home/pyconkr/{target}.pycon.kr/pyconkr-2017'.format(target=target)

    if target == 'dev':
        python_env = '/home/pyconkr/.pyenv/versions/pyconkr-2017-dev'
    else:
        python_env = '/home/pyconkr/.pyenv/versions/pyconkr-2017'

    with settings(cd(home_dir), shell_env(DJANGO_SETTINGS_MODULE='pyconkr.settings_prod')):
        run('git fetch --all -p')
        run('git reset --hard ' + sha1)
        run('bower install')
        run('%s/bin/pip install -r requirements.txt' % python_env)
        run('%s/bin/python manage.py compilemessages' % python_env)
        run('%s/bin/python manage.py migrate' % python_env)
        run('%s/bin/python manage.py collectstatic --noinput' % python_env)
        # worker reload
        run('echo r > /var/run/pyconkr-2017-%s.fifo' % target)

