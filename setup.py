from setuptools import find_packages, setup

setup(
    name='lorikeet',
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
)
