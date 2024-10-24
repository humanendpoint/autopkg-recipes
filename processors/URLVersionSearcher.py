import re
from autopkglib import ProcessorError
from autopkglib.URLGetter import URLGetter

"""Downloads a URL using curl and performs a regular expression match
on the text.

Requires version 1.4."""

MATCH_MESSAGE = "Found matching text"
NO_MATCH_MESSAGE = "No match found on URL"

__all__ = ["URLVersionSearcher"]


class URLVersionSearcher(URLGetter):
    """Downloads a URL using curl and performs a regular expression match
    on the text.
    """

    input_variables = {
        "re_pattern": {
            "description": "Regular expression (Python) to match against page.",
            "required": True,
        },
        "url": {"description": "URL to download", "required": True},
        "result_output_var_name": {
            "description": (
                "The name of the output variable that is returned "
                "by the match. If not specified then a default of "
                '"match" will be used.'
            ),
            "required": False,
            "default": "match",
        },
        "request_headers": {
            "description": (
                "Optional dictionary of headers to include with "
                "the download request."
            ),
            "required": False,
        },
        "curl_opts": {
            "description": (
                "Optional array of curl options to include with "
                "the download request."
            ),
            "required": False,
        },
        "re_flags": {
            "description": (
                "Optional array of strings of Python regular "
                "expression flags. E.g. IGNORECASE."
            ),
            "required": False,
        },
    }
    output_variables = {
        "result_output_var_name": {
            "description": (
                "Highest matched sub-pattern from input found on the fetched "
                "URL. Note the actual name of variable depends on the input "
                'variable "result_output_var_name" or is assigned a default of '
                '"match."'
            )
        }
    }

    description = __doc__

    def prepare_curl_cmd(self):
        """Assemble curl command and return it."""
        curl_cmd = super().prepare_curl_cmd()
        self.add_curl_common_opts(curl_cmd)
        curl_cmd.append(self.env["url"])
        return curl_cmd

    def prepare_re_flags(self):
        """Create flag varible for re.compile"""
        flag_accumulator = 0
        for flag in self.env.get("re_flags", {}):
            if flag in re.__dict__:
                flag_accumulator += re.__dict__[flag]
        return flag_accumulator

    def re_search(self, content):
        """Search for re_pattern in content"""

        re_pattern = re.compile(self.env["re_pattern"], flags=self.prepare_re_flags())
        matches = re_pattern.finditer(content)

        highest_version = None

        for match in matches:
            version = match.group(match.lastindex or 0)
            if highest_version is None or version > highest_version:
                highest_version = version

        if highest_version is None:
            raise ProcessorError(f"{NO_MATCH_MESSAGE}: {self.env['url']}")

        return highest_version

    def main(self):
        output_var_name = self.env["result_output_var_name"]

        # Prepare curl command
        curl_cmd = self.prepare_curl_cmd()

        # Execute curl command and search in content
        content = self.download_with_curl(curl_cmd)
        highest_version = self.re_search(content)

        self.env[output_var_name] = highest_version
        self.output(f"{MATCH_MESSAGE} ({output_var_name}): {highest_version}")

        self.output_variables = {
            output_var_name: {"description": "Highest matched version number"}
        }


if __name__ == "__main__":
    PROCESSOR = URLVersionSearcher()
    PROCESSOR.execute_shell()
