#!/usr/local/autopkg/python
"""
Applies a patch to a .c file in source code if required.

Currently required to build libgpg-error on macOS, but might get deprecated soon.
"""
import subprocess
import autopkglib
import os

__all__ = ["ApplyPatch"]


class ApplyPatch(autopkglib.Processor):
    """Applies a patch to a binary source code if required."""

    description = "Applies a patch to a binary source code file."
    input_variables = {
        "source_path": {
            "required": True,
            "description": "Full Path to the source to patch",
        },
        "patch_file": {
            "required": True,
            "description": "Full Path to the patch file. Should be outside of the downloaded dir",
        },
    }
    output_variables = {}

    def main(self):
        source_path = self.env["source_path"]
        patch_file = self.env["patch_file"]

        # Debug statement for source_path
        print(f"Changing directory to: {source_path}")

        if not os.path.exists(source_path):
            raise autopkglib.ProcessorError(
                f"Source path does not exist: {source_path}"
            )

        os.chdir(source_path)

        # Debug statement for current working directory
        print(f"Current directory: {os.getcwd()}")

        # Construct the patch command as a string and use shell=True
        patch_cmd = f"patch -p0 < {patch_file}"

        # Debug statement for patch command
        print(f"Running patch command: {patch_cmd}")

        try:
            subprocess.check_call(patch_cmd, shell=True)
        except subprocess.CalledProcessError as err:
            raise autopkglib.ProcessorError(f"Failed to apply patch: {err}")

        os.chdir(os.environ.get("GITHUB_WORKSPACE", "/"))
        print(f"Changed back to original directory: {os.getcwd()}")


if __name__ == "__main__":
    processor = ApplyPatch()
    processor.execute_shell()
