from collections.abc import Callable, Iterable

from attrs import field, frozen

from .dataclasses import Bucket, Member


type BucketHook = Callable[[Member], Bucket | None]
type MemberHook = Callable[[type], Iterable[Member]]


def to_tuple[T](hooks: Iterable[T]) -> tuple[T, ...]:
    return tuple(hooks)


@frozen
class Hooks:
    """
    Functions to let a caller influence different areas of classify

    Callers of classify() can spcecify a Hook() instance with functions that
    influence how classify manages difference parts of its inspection.
    """

    # the converter stores a tuple, but ty types __init__ from the annotation
    # rather than the converter, so this describes what callers may pass
    buckets: Iterable[BucketHook] = field(default=(), converter=to_tuple)
    members: Iterable[MemberHook] = field(default=(), converter=to_tuple)

    def __or__(self, other: "Hooks") -> "Hooks":
        return Hooks(
            members=[*self.members, *other.members],
            buckets=[*self.buckets, *other.buckets],
        )


NO_HOOKS = Hooks()
