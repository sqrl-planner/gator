"""Data-related functions for the CLI."""
import typer
import textwrap

from tabulate import tabulate
from gator.extensions import repolist

app = typer.Typer()
repo_app = typer.Typer()
app.add_typer(repo_app, name='repo')


@app.command('pull')
def data_pull() -> None:
    """Pull data from the repository registry."""


@repo_app.command('list')
def repos_list() -> None:
    """List all registered repositories."""
    headers = ['SLUG', 'ROUTE', 'NAME', 'DESCRIPTION']
    rows = []
    for repo, route in repolist.repos:
        wrapped_desc = '\n'.join(textwrap.wrap(repo.description))
        rows.append([repo.slug, route, repo.name, wrapped_desc])

    print(tabulate(rows, headers=headers, tablefmt='plain'))


@repo_app.command('add')
def repos_add(repo: str = typer.Argument(
        ..., help='Repo route to add to repolist.')) -> None:
    """Add a repo by route."""
    registry = repolist._registry
    if registry.has_match(repo):
        # repo is a pattern
        repolist.add(repo)
    else:
        print('Could not find a repository matching '
              f'the slug or pattern "{repo}"')


@repo_app.command('remove')
def repos_remove(repo: str = typer.Argument(
        ..., help='Repo route to remove from repolist.')) -> None:
    """Remove a repo by route."""
    registry = repolist._registry
    if registry.has_match(repo):
        # repo is a pattern
        repolist.remove(repo)
    else:
        print('Could not find a repository matching '
              f'the slug or pattern "{repo}"')