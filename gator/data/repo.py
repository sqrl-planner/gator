import uuid
from pathlib import Path
from pydoc import locate
from functools import wraps
from dataclasses import dataclass, field
from typing import Optional, Any, get_type_hints

import yaml
from routes import Mapper

from gator.data.utils import without_keys
from gator.data.pipeline.datasets import Dataset


@dataclass
class Repository:
    """A repository of one or more datasets.

    Instance Attributes:
        datasets: A list of datasets that are available in this repository.
        slug: A short string that uniquely identifies this repository.
        name: A human-readable name for this repository.
        description: A short description of this repository.
        metadata: Any additional metadata that is relevant to this repository.
    """
    datasets: list[Dataset]
    slug: str
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class RepositoryRegistry:
    """A collection of repositories that are accessible to the app."""

    def __init__(self) -> None:
        self._routes = Mapper()
        self._route_metadata = {}

    def route(self, pattern: str, **kwargs: Any) -> callable:
        """A decorator that is used to register a repo function for a
        given rule. This does the same thing as the `add_rule` method
        but is intended for decorator usage::

            @registry.route('/books/:batch')
            def book_repo(batch: int) -> Repository:
                return Repository(
                    [Dataset(batch=batch)],
                    slug=f'books-{batch}',
                    name=f'Books for batch {batch}'
                )

        Args:
            pattern: The rule pattern as string.
            **kwargs: Additional keyword arguments that will be used when
                creating the Repository.
        """
        def decorator(f: callable) -> callable:
            self.add_rule(pattern, f, **kwargs)
            return f
        return decorator

    def add_rule(self, pattern: str, f: callable, **repo_kwargs: Any) -> None:
        """Register a repo function for a given rule.

        Args:
            pattern: The rule pattern as string.
            f: The function to be registered. This function should return
                a single Repository instance. Pattern parameters will be
                passed to the function as keyword arguments.

                Argument type annotations will be used to infer the types of
                the parameters and convert them accordingly.
            **repo_kwargs: Additional keyword arguments that will be used when
                creating the Repository. Valid keyword arguments are any of
                the attributes of the Repository class.

                NOTE: String values can use the format syntax to access
                parameters from the pattern. For example, if the pattern is
                '/books/:batch', then some valid repo kwarg dicts are:

                    - `{'slug': 'books-{batch}'}`
                    - `{'description': 'Books for batch {batch}'}
        """
        if 'slug' not in repo_kwargs:
            repo_kwargs['slug'] = f'{f.__name__}-{uuid.uuid4()}'

        route_uuid = str(uuid.uuid4())
        self._routes.connect(
            pattern,
            __uuid__=route_uuid,  # used to identify the route
        )
        self._route_metadata[route_uuid] = dict(f=f, type_hints=get_type_hints(f))

    def has_match(self, query: str) -> bool:
        """Check if a query matches a route.

        Args:
            query: The query string.

        Returns:
            True if a match was found, False otherwise.
        """
        return self._routes.match(query) is not None

    def match(self, query: str) -> Optional[Repository]:
        """Match a query against registered routes.

        Args:
            query: The query string.

        Returns:
            A Repository instance if a match was found, None otherwise.
        """
        match = self._routes.match(query)
        if match:
            route_uuid = match.get('__uuid__')
            metadata = self._route_metadata[route_uuid]

            params = without_keys(match, '__uuid__')
            self._try_convert_params(params, metadata['type_hints'])

            repo = metadata['f'](**params)
            if isinstance(repo, Repository):
                return repo
            else:
                raise TypeError(f'{query}: Expected Repository, got {type(repo)}')
        else:
            return None

    @staticmethod
    def _try_convert_params(params: dict, type_hints: dict) -> None:
        """Try to convert parameters according to type hints.
        Mutate the params argument.
        """
        for k, v in params.items():
            if k in type_hints:
                # Try to convert the value to the correct type
                # If it fails, then just leave it as a string.
                try:
                    t = locate(type_hints[k])
                    params[k] = t(v)
                except ValueError:
                    pass


def _ensure_initialised(f: callable) -> callable:
    """A decorator to ensure the repolist has been initted."""
    @wraps(f)
    def wrapper(self: 'RepositoryRegistry', *args: Any, **kwargs: Any) -> Any:
        assert self._fp is not None and self._registry is not None,\
            'RepositoryList not initialised. Call RepositoryList.__init__ first.'
        return f(self, *args, **kwargs)
    return wrapper


class RepositoryList:
    """Monitors a repolist yml file."""

    def __init__(self, fp: Optional[Path] = None,
                 registry: Optional[RepositoryRegistry] = None) -> None:
        self._fp = fp
        self._registry = registry

    @property
    @_ensure_initialised
    def repos(self) -> list[tuple[Repository, str]]:
        """Return a list of tuples of the form (repo, route) giving all the
        repositories in this repolist along with their registry route."""
        repos = []
        for pattern in self.routes:
            repo = self._registry.match(pattern)
            if repo is not None:
                repos.append((repo, pattern))

        return repos

    @property
    @_ensure_initialised
    def routes(self) -> list[str]:
        """Return a list of all routes in this repolist."""
        with open(self._fp, 'r') as f:
            return yaml.safe_load(f)

    @_ensure_initialised
    def add(self, pattern: str) -> None:
        """Add a new repository to the list.

        Args:
            pattern: The pattern to match the repository.
        """
        if self._registry.has_match(pattern):
            # Add to the list
            with open(self._fp, 'r') as f:
                repolist = yaml.safe_load(f)
            # Check if the pattern is already in the list
            if pattern not in repolist:
                repolist.append(pattern)
                with open(self._fp, 'w') as f:
                    yaml.dump(repolist, f)
        else:
            raise ValueError(f'{pattern}: No such repository')

    @_ensure_initialised
    def remove(self, pattern: str) -> None:
        """Remove a repository from the list.

        Args:
            pattern: The pattern to match the repository.
        """
        if self._registry.has_match(pattern):
            # Remove from the list
            with open(self._fp, 'r') as f:
                repolist = yaml.safe_load(f)
            # Check if the pattern is already in the list
            if pattern in repolist:
                repolist.remove(pattern)
                with open(self._fp, 'w') as f:
                    yaml.dump(repolist, f)
        else:
            raise ValueError(f'{pattern}: No such repository')
