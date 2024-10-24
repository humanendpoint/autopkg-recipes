#!/usr/local/autopkg/python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Signs binaries.
"""

import subprocess
import os

from autopkglib import Processor, ProcessorError


__all__ = ["BinarySigner"]


class BinarySigner(Processor):
    description = (
        "Signs a binary file with codesign.",
        "Warning from PkgSigner, which works the same:",
        "The keychain that contains the signing certificate and key",
        "MUST be unlocked. Run the cmd once manually so that you can",
        "give it access to the correct key so that autopkg can run",
        "without manual intervention.",
    )
    input_variables = {
        "binary_path": {
            "required": True,
            "description": "Path to the binary file to be signed",
        },
        "signing_identity": {
            "required": True,
            "description": "Signing identity used to sign the binary. Must be an EXACT match.",
        },
    }
    output_variables = {
        "signed_binary_path": {"description": "Path to the signed binary file."}
    }

    __doc__ = description

    def main(self):
        binary_path = os.path.dirname(self.env["binary_path"])
        # sign a binary
        command_line_list = [
            "/usr/bin/codesign",
            "--sign",
            self.env["signing_identity"],
            "--force",
            "--timestamp",
            "-o",
            "runtime",
            binary_path,
        ]
        print(command_line_list)
        subprocess.call(command_line_list)

        self.env["signed_binary_path"] = binary_path


if __name__ == "__main__":
    processor = BinarySigner()
    processor.execute_shell()
