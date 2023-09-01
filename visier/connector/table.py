# Copyright 2023 Visier Solutions Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
