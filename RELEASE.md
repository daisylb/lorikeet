# Performing a Release

- Update the version in `package.json`
- Commit
- Tag the release in Git
- `python setup.py bdist_wheel`
- `twine upload dist/django_lorikeet-x.y-py3-none-any.whl`
- `npm publish`
