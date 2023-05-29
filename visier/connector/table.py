# This file is part of visier-connector-python.
#
# visier-connector-python is free software: you can redistribute it and/or modify
# it under the terms of the Apache License, Version 2.0 (the "License").
#
# visier-connector-python is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License, Version 2.0 for more details.
#
# You should have received a copy of the Apache License, Version 2.0
# along with visier-connector-python. If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""
Table respresentation of a Visier Query API result set.
"""

import json
import dataclasses

@dataclasses.dataclass
class ResultTable:
    """Tabular result set

    Keyword args:
    jsonlines -- JSON Lines representation of the entire result set.
                 This is an array of strings, where each line will be
                 parsed independently.

    Class members:
    header -- Array of column header strings.
    rows() -- Row tuple generator
    """
    header = []

    def __init__(self, gen_f) -> None:
        self.header = json.loads(next(gen_f))
        self._generator = gen_f


    def rows(self):
        """Returns a row tuple generator"""
        for line in self._generator:
            yield json.loads(line)
