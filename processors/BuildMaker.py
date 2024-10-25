#!/usr/local/autopkg/python
"""
Runs `configure` and `make DESTDIR=' (both can be changed) on a downloaded source path.
The then compiled binary file/accompaning folders can be packaged up and used in a `.pkg` file.
"""

import os
import subprocess
import autopkglib

__all__ = ["BuildMaker"]


class BuildMaker(autopkglib.Processor):
    """Run configure and make"""

    description = __doc__
    input_variables = {
        "source_path": {
            "required": True,
            "description": "Path to the source to compile",
        },
        "alt_configure": {
            "required": False,
            "description": "Use alternative configure instead of ./configure",
        },
        "no_configure": {
            "required": False,
            "description": "Skip the configure step",
        },
        "alt_make_install": {
            "required": False,
            "description": "Use an alternative make install instead of make-redir",
        },
    }
    output_variables = {
        "buildmaker_configure_result": {
            "description": "True if the configure command ran successfully."
        },
        "buildmaker_make_result": {
            "description": "True if the make command ran successfully."
        },
    }

    def main(self):
        source_path = self.env["source_path"]
        pkg_root = self.env.get("pkgroot")

        # Ensure pkg_root is set
        if not pkg_root:
            self.output("No pkgroot defined. Exiting.")
            return

        # Configure command logic
        if self.env.get("no_configure"):
            configure_cmd = None
        elif self.env.get("alt_configure"):
            configure_cmd = self.env.get("alt_configure")
        else:
            configure_cmd = "./configure"

        # Make install command logic
        if self.env.get("alt_make_install"):
            make_install_cmd = self.env.get("alt_make_install")
        else:
            make_install_cmd = "make DESTDIR=%s install" % pkg_root

        os.chdir(source_path)

        # Run configure command if not skipped
        if configure_cmd:
            try:
                self.output(f"Running configure command: {configure_cmd}")
                result = subprocess.run(
                    configure_cmd,
                    shell=True,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                self.output(result.stdout)
                self.output(result.stderr)
                self.env["buildmaker_configure_result"] = True
            except subprocess.CalledProcessError as e:
                self.output(f"Configure command failed: {e}")
                self.output(e.stdout)
                self.output(e.stderr)
                self.env["buildmaker_configure_result"] = False
                return
        else:
            self.output("Skipping configure step.")
            self.env["buildmaker_configure_result"] = True

        # Run make install command
        try:
            self.output(f"Running make install command: {make_install_cmd}")
            result = subprocess.run(
                make_install_cmd, shell=True, check=True, text=True, capture_output=True
            )
            self.output(result.stdout)
            self.output(result.stderr)
            self.env["buildmaker_make_result"] = True
        except subprocess.CalledProcessError as e:
            self.output(f"Make install command failed: {e}")
            self.output(e.stdout)
            self.output(e.stderr)
            self.env["buildmaker_make_result"] = False

        os.chdir(os.environ.get("GITHUB_WORKSPACE", "/"))


if __name__ == "__main__":
    PROCESSOR = BuildMaker()
    PROCESSOR.execute_shell()
