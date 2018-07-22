from setuptools import find_packages, setup

setup(
    name='django-lorikeet',
    description='A simple, generic, API-only shopping cart framework for Django',
    author='Adam Brenecki',
    author_email='adam@brenecki.id.au',
    license='MIT',
    setup_requires=["setuptools_scm>=1.11.1"],
    use_scm_version=True,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'djangorestframework>=3.5.3,<3.6',
        'django-model-utils>=2.6,<3',
    ],
    extras_require={
        'stripe': [
            'stripe>=1.44.0,<2',
        ],
        'email_invoice': [
            'premailer>=3.0.1,<4',
        ],
        'starshipit': [
            'requests>=2.13.0,<3',
        ],
        'docs': [
            'sphinx>=1.5.1,<1.6',
            'sphinx-rtd-theme>=0.2.4,<0.3',
            'sphinx-js>=1.3,<1.4',
            'sphinxcontrib_httpdomain>=1.5.0,<2',
        ],
        'dev': [
            'django<=1.10.999',
            'factory-boy',
            'tox',
        ]
    },
)
