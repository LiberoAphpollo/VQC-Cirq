# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys


class FakeMock:

    class Mock:
        pass


if sys.version_info < (3,):
    mock = FakeMock
else:
    from unittest import mock


def python3_mock_test(target, method):
    """A decorator for tests that need to mock.patch.object() which is not
     supported in Python 2.7. The test only executes if running Python 3.

    Args:
        target: Target to patch.
        method: The name of the method to mock.
    """
    if sys.version_info >= (3,):
        return mock.patch.object(target, method)
    else:
        def nothing(f):
            pass
        return nothing
