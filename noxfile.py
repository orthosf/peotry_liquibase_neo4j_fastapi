import nox

@nox.session
def tests(session):
    session.run('poetry', 'install', external=True)
    session.run('pytest')

@nox.session
def lint(session):
    session.run('poetry', 'install', external=True)
    session.run('flake8', 'src')

#@nox.session
#def mypy(session):
    #session.install('mypy')
    #session.run('mypy', 'your_project')