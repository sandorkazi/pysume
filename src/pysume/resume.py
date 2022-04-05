import os
import jinja2
import pysume
import pysume.template as template
import pysume.static as static
import shutil
from jinja2 import Template
from pathlib import PurePath
from pysume.config.config import Config
from typing import Dict, Collection, Union, Any

DEFAULTS = dict(headshot="headshot.jpg")
DEFAULT_CONFIG_FILE = "config.yml"
DEFAULT_FORMAT_NAME = "html"
DEFAULT_INPUT_PATH = PurePath(pysume.__file__).parent.parent / "input"
DEFAULT_OUTPUT_PATH = PurePath(pysume.__file__).parent.parent / "output"


class Resume:

    def __init__(
        self,
        input_path: PurePath = DEFAULT_INPUT_PATH,
        config_file: str = DEFAULT_CONFIG_FILE,
        output_path: PurePath = DEFAULT_OUTPUT_PATH,
    ):
        self._input_path = input_path
        self._config_file = input_path / config_file
        self._output_path = output_path
        self._config = Config(self._config_file, defaults=DEFAULTS)

    def render_file(self, source: PurePath, destination: PurePath) -> None:
        with open(destination, "w") as fout:
            with open(source) as fin:
                rendered = Template(fin.read()).render(**self._config)
                fout.write(rendered)

    def render_contents(self, contents: Union[str, Collection[str], Collection[Collection[str]]]) -> str:
        if isinstance(contents, str):
            return Template(
                """
                    <p>{{ contents.rstrip().replace("\n", "<br/>") }}</p>
                """
            ).render(contents=contents)
        elif isinstance(contents, Collection):
            if all((isinstance(x, str) for x in contents)):
                return Template(
                    """
                        <ul class="keySkills">{% for item in contents %}
                            <li>{{ item.rstrip().replace("\n", "<br/>") }}</li>
                        {%- endfor %}
                        </ul>
                    """
                ).render(contents=contents)
            elif all((isinstance(x, Collection) for x in contents)):
                return Template(
                    """
                        {% for item in contents %}
                            <article>
                                <h2>{{ item.get("title", "") }}</h2>
                                <p class="subDetails">{{ item.get("subtitle", "") }}</p>
                                <p>{{ item.get("contents", "").rstrip().replace("\n", "<br/>") }}</p>
                            </article>
                        {% endfor %}
                    """
                ).render(contents=contents)
            raise ValueError("Each item in `sections` with lists as contents should either list strings or dicts.")
        raise ValueError("Each item in `sections` should either be strings or lists.")

    def render_section(self, section: Dict[str, str]) -> str:
        contents = section.get("contents", "")
        contents = self.render_contents(contents)
        section["contents"] = contents
        return jinja2.Template(
            """
                <section>
                    <div class="sectionTitle">
                        <h1>{{ title }}</h1>
                    </div>
                    <div class="sectionContent">
                        {{ contents.rstrip() }}
                    </div>
                    <div class="clear"></div>
                </section>
            """
        ).render(
            **section,
        )

    def render(self, format_name: str) -> None:
        static_in = PurePath(static.__file__).parent / format_name
        src_root = PurePath(template.__file__).parent / format_name
        dest_root = self._output_path / format_name
        try:
            shutil.rmtree(dest_root)
        except FileNotFoundError:
            pass
        shutil.copytree(static_in, dest_root)
        headshot = self._config.get("headshot")
        sections: Collection[Any] = self._config.get("sections", [])
        sections_str = "\n\n".join([self.render_section(section) for section in sections])
        self._config["sections"] = sections_str
        if headshot:
            shutil.copyfile(self._input_path / headshot, dest_root / headshot)
        for dir_path, dir_names, filenames in os.walk(src_root):
            src_path = PurePath(dir_path)
            dest_path = dest_root / PurePath(src_path).relative_to(src_root)
            for d in dir_names:
                os.mkdir(dest_path / d)
            for f in filenames:
                self.render_file(source=src_path / f, destination=dest_path / f)


if __name__ == "__main__":
    import click  # noqa

    @click.command()
    @click.argument("input_path")
    @click.argument("output_path")
    @click.option("-c", "--config_file", default=DEFAULT_CONFIG_FILE)
    @click.option("-f", "--format_name", default=DEFAULT_FORMAT_NAME)
    def main(input_path: str, output_path: str, config_file: str, format_name: str) -> None:
        Resume(
            input_path=PurePath(input_path),
            config_file=config_file,
            output_path=PurePath(output_path),
        ).render(
            format_name=format_name,
        )
    main()
