from functools import total_ordering


@total_ordering
class BeatModsVersion:
    """
    Represents a BeatSaber version as represented by BeatMods.
    """

    def __init__(self, version: str, alias: str):
        """
        Creates a new a BeatModsVersion.
        :param version: The BeatMods version number. The lowest Beat Saber version for each group of aliases
                        with compatible mods.
        :param alias: The Beat Saber version number. May be the same as version.
        """
        self._version = version
        self._alias = alias

    def __str__(self):
        return f"Beat Saber v{self.alias} (BeatMods v{self.version})"

    def __repr__(self):
        return f"<{str(self)}>"

    def __gt__(self, other):
        # compare version first, then alias
        for a, b in zip(self.version.split('.'), other.version.split('.')):
            # these are string comparisons, so if one is longer it's always a higher number (more digits)
            if len(a) != len(b):
                return len(a) > len(b)
            if a != b:
                return a > b
        for a, b in zip(self.alias.split('.'), other.alias.split('.')):
            if len(a) != len(b):
                return len(a) > len(b)
            if a != b:
                return a > b
        # if we've gotten here, we that means we're equal
        return False

    def __eq__(self, other):
        if not isinstance(other, BeatModsVersion):
            return False

        if (self is None and other is not None) or (self is not None and other is None):
            return False

        return self.version == other.version and self.alias == other.alias

    @property
    def alias(self) -> str:
        """
        The Beat Saber version number. May be the same as version
        """
        return self._alias

    @property
    def version(self) -> str:
        """
        The BeatMods version number. The lowest Beat Saber version for each group of aliases with compatible mods.
        """
        return self._version
