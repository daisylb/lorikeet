import nox
from os import environ

nox.options.sessions = ('tests',)
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = True


@nox.session(python=('3.5', '3.6', '3.7'))
@nox.parametrize('django', ('1.11', '2.0', '2.1', '2.2'))
def tests(session, django):
    session.install('poetry')
    session.run('poetry', 'install', '-Estripe', '-Eemail_invoice', '-Estarshipit',
                # this is necessary to prevent poetry from creating
                # its own virtualenv
                env={'VIRTUAL_ENV': session.virtualenv.location})
    session.install(f'django>={django},<{django}.999')
    test_env = {'STRIPE_API_KEY': environ['STRIPE_API_KEY']} if 'STRIPE_API_KEY' in environ else {}
    session.run('pytest', *session.posargs, env=test_env)
