#!/usr/local/autopkg/python
"""
A processor to, if required, trim everything after and including the last dot from a version_string.
"""
from autopkglib import Processor, ProcessorError
import json
import requests


class TrimVersion(Processor):
    """See Docstring"""

    description = __doc__
    input_variables = {
        "version_string": {
            "required": True,
            "description": "The version string to trim.",
        },
        "url": {
            "required": True,
            "description": "The URL to fetch the version from and compare.",
        },
    }
    output_variables = {
        "trimmed_version": {"description": "The version string after trimming."},
    }

    def fetch_version_from_url(self, url):
        try:
            response = requests.get(url)
            data = response.json()  # Use response.json() to parse JSON directly
            return data.get("versions", {}).get("stable", "").strip()
        except Exception as e:
            raise ProcessorError(f"Error fetching version from URL: {e}")

    def main(self):
        version_string = self.env.get("version_string")
        url = self.env.get("url")

        if not version_string:
            self.output("Version string is empty. No trimming needed.")
            self.env["trimmed_version"] = version_string
            return

        # fetch version
        url_version = self.fetch_version_from_url(url)

        # compare
        if version_string != url_version:
            self.output(
                f"Versions differ: {version_string} (input) vs {url_version} (URL)"
            )
            version_string = url_version

        # split
        version_parts = version_string.split(".")

        # at least two parts?
        if len(version_parts) >= 2:
            # join all parts except the last one
            trimmed_version = ".".join(version_parts[:-1])
            self.output("Version string has been trimmed.")
            self.env["trimmed_version"] = trimmed_version
        else:
            self.output(
                "Version string has less or equal to two parts. No trimming needed."
            )
            self.env["trimmed_version"] = version_string


if __name__ == "__main__":
    PROCESSOR = TrimVersion()
    PROCESSOR.execute_shell()
