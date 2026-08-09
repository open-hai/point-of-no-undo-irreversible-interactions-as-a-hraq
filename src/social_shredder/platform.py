"""Mock social-media feed and shredder controller (paper Section 3.2.1).

Paper: "We designed the experience prototype SocialShredder that irreversibly
alters a personal item -- a Polaroid picture of the participant -- whenever they
like images on a mock-up social media platform. [...] Via USB, the shredding
action was triggered whenever a like was given on the mock-up platform."
Condition A has the irreversible feedback, condition B has none (Section 3.2.2).

The paper gives no feed length, no image set, no shred step size, no total
number of likes needed to destroy the Polaroid, and no serial protocol. Every
number below is therefore an ASSUMPTION; see REPRODUCIBILITY.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ASSUMPTION: a Polaroid is ~88 mm tall in its image area and the shredder pulls
# a fixed strip per like. 30 likes destroy the picture completely; the paper
# only tells us that a complete destruction was reachable, because "four
# participants continued giving likes, even after the image was completely
# shredded" (Section 3.2.2).
SHRED_STEPS_TO_DESTROY = 30
FEED_LENGTH = 60  # ASSUMPTION: number of posts in the mock feed


class Irreversible(RuntimeError):
    pass


@dataclass
class Shredder:
    """Digitally controlled, monotone: it can only ever consume more picture."""

    steps_to_destroy: int = SHRED_STEPS_TO_DESTROY
    steps: int = 0
    events: list[tuple[float, str]] = field(default_factory=list)

    @property
    def destroyed_fraction(self) -> float:
        return min(1.0, self.steps / self.steps_to_destroy)

    @property
    def fully_destroyed(self) -> bool:
        return self.steps >= self.steps_to_destroy

    def shred(self, t: float) -> None:
        self.steps += 1
        self.events.append((t, "shred"))

    def restore(self) -> None:
        raise Irreversible(
            "the Polaroid cannot be un-shredded: 'once an image is liked and "
            "thus altered to ultimately destruction, it cannot be restored by "
            "disliking the content' (Section 3.2.1)"
        )


@dataclass
class MockFeed:
    """The like/unlike surface. Condition A wires likes to the shredder."""

    condition: str = "A"          # "A" = irreversible feedback, "B" = none
    n_posts: int = FEED_LENGTH
    shredder: Shredder = field(default_factory=Shredder)
    liked: set[int] = field(default_factory=set)
    actions: list[tuple[float, str, int]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.condition not in ("A", "B"):
            raise ValueError("condition must be 'A' or 'B'")

    def like(self, post_id: int, t: float = 0.0) -> None:
        if not 0 <= post_id < self.n_posts:
            raise ValueError(f"post {post_id} not in feed")
        if post_id in self.liked:
            return
        self.liked.add(post_id)
        self.actions.append((t, "like", post_id))
        if self.condition == "A":
            self.shredder.shred(t)

    def unlike(self, post_id: int, t: float = 0.0) -> None:
        """The like disappears from the interface; the shredding does not."""
        self.liked.discard(post_id)
        self.actions.append((t, "unlike", post_id))

    def like_count(self) -> int:
        return len(self.liked)

    def state(self) -> dict:
        return {
            "condition": self.condition,
            "likes_visible": self.like_count(),
            "likes_given": sum(1 for a in self.actions if a[1] == "like"),
            "shred_steps": self.shredder.steps,
            "destroyed_fraction": round(self.shredder.destroyed_fraction, 3),
            "fully_destroyed": self.shredder.fully_destroyed,
        }
