# coding: utf-8

# Python 3 Standard Library
import argparse
import collections
import io
import json
import os.path
import subprocess
import shutil
import sys
import warnings

from collections.abc import Callable
from types import ModuleType
from typing import Any, cast, Dict, IO, List, Optional, Tuple, Union

# Pandoc
from . import about
from . import utils


# Configuration
# ------------------------------------------------------------------------------
_configuration = None


def _get_configuration() -> Dict[str, Any]:
    """Gets configuration, does initialization if necessary"""
    configuration = configure(read=True)
    if configuration is None:
        configuration = configure(auto=True, read=True)
    assert configuration is not None
    return configuration


def import_types() -> ModuleType:
    """Loads the types module and returns it"""
    from . import types  # this also sets pandoc.types

    return types


def configure(
    auto: bool = False,
    path: Optional[str] = None,
    version: Optional[str] = None,
    pandoc_types_version: Optional[str] = None,
    read: bool = False,
    reset: bool = False,
) -> Optional[Dict[str, Any]]:
    global _configuration

    default = (
        auto is False
        and path is None
        and version is None
        and pandoc_types_version is None
        and read is False
        and reset is False
    )
    if default:
        error_msg = "configure expects at least one argument"
        raise ValueError(error_msg)

    if reset is True:
        _configuration = None  # TODO: clean the types
        return

    read_only = (
        read
        and auto is False
        and path is None
        and version is None
        and pandoc_types_version is None
    )

    if auto:
        found_path = shutil.which("pandoc")
        if found_path is None:
            raise RuntimeError("cannot find the pandoc program")

        if path is None:
            path = found_path
        elif path != found_path:
            error_msg = (
                f"found path {found_path!r} with auto=True "
                f"but it doesn't match path={path!r}"
            )
            raise ValueError(error_msg)

    if path is not None:
        result = subprocess.run([path, "--version"], capture_output=True)
        found_version = result.stdout.decode("utf-8").splitlines()[0].split(" ")[1]
        if version is None:
            version = found_version
        elif version != found_version:
            error_msg = (
                f"the version of the pandoc program is {found_version!r} "
                f"but it doesn't match version={version!r}"
            )
            raise ValueError(error_msg)

    if version is not None:
        found_pandoc_types_versions = utils.resolve(version, warn=True)
        if pandoc_types_version is None:
            if len(found_pandoc_types_versions) >= 1:
                # pick latest (ignore the real one that may be unknown)
                pandoc_types_version = found_pandoc_types_versions[-1]
            else:
                error_msg = (
                    "cannot find a version of pandoc-types "
                    f"matching pandoc {version}"
                )
                raise ValueError(error_msg)
        elif pandoc_types_version not in found_pandoc_types_versions:
            error_msg = (
                f"the version of the pandoc program is {version!r} "
                f"but it doesn't match pandoc_types_version={pandoc_types_version!r}"
            )
            raise ValueError(error_msg)

    if not read_only:  # set the configuration, update pandoc.types
        _configuration = {
            "auto": auto,
            "path": path,
            "version": version,
            "pandoc_types_version": pandoc_types_version,
        }
        import_types().make_types(pandoc_types_version)

    if read:
        return _configuration


# JSON Reader / Writer
# ------------------------------------------------------------------------------
def read(
    source: Optional[Union[str, bytes, bytearray]] = None,
    file: Optional[Union[str, IO]] = None,
    format: Optional[str] = None,
    options: Optional[List[str]] = None,
) -> Any:
    configuration = _get_configuration()

    if options is None:
        options = []

    filename = None
    if source is None and file is None:
        raise ValueError("one of source or file must be defined.")
    elif source is not None and file is not None:
        raise ValueError("only one of source or file must be defined, not both.")
    elif file is not None:
        if isinstance(file, io.IOBase):
            source = file.read()
        elif isinstance(file, str):
            filename = file
            with open(filename, "rb") as f:
                source = f.read()
        else:
            raise ValueError("file must be a string or file like object")

    if format is None and filename is not None:
        format = format_from_filename(filename)
        if format is None:
            warnings.warn(
                "Could not infer format from file extension, defaulting to markdown"
            )
            format = "markdown"
    elif format is None:
        format = "markdown"

    if format != "json" and configuration["path"] is None:
        error_msg = f"reading the {format!r} format requires the pandoc program"
        raise RuntimeError(error_msg)

    if format == "json":
        if isinstance(source, (bytes, bytearray)):
            json_str = source.decode("utf-8")
        else:
            json_str = cast(str, source)
    else:
        if isinstance(source, str):
            source = source.encode("utf-8")

        pandoc_path = configuration["path"]
        options = ["-t", "json"] + options + ["-f", format]
        result = subprocess.run(
            [pandoc_path] + options, input=source, capture_output=True
        )

        if result.returncode != 0:
            raise RuntimeError("pandoc error: " + result.stderr.decode("utf-8"))
        if len(result.stdout) == 0:
            raise RuntimeError("pandoc did not write any output to stdout")

        json_str = result.stdout.decode("utf-8")

    json_ = json.loads(json_str)

    if utils.version_key(configuration["pandoc_types_version"]) < [1, 17]:
        return read_json_v1(json_)
    else:
        return read_json_v2(json_)


# ------------------------------------------------------------------------------
_ext_to_file_format = {
    ".adoc": "asciidoc",
    ".asciidoc": "asciidoc",
    ".context": "context",
    ".ctx": "context",
    ".db": "docbook",
    ".doc": "doc",  # pandoc will generate an "unknown reader"
    ".docx": "docx",
    ".dokuwiki": "dokuwiki",
    ".epub": "epub",
    ".fb2": "fb2",
    ".htm": "html",
    ".html": "html",
    ".icml": "icml",
    ".json": "json",
    ".latex": "latex",
    ".lhs": "markdown+lhs",
    ".ltx": "latex",
    ".markdown": "markdown",
    ".mkdn": "markdown",
    ".mkd": "markdown",
    ".mdwn": "markdown",
    ".mdown": "markdown",
    ".Rmd": "markdown",
    ".md": "markdown",
    ".ms": "ms",
    ".muse": "muse",
    ".native": "native",
    ".odt": "odt",
    ".opml": "opml",
    ".org": "org",
    ".pdf": "pdf",  # pandoc will generate an "unknown reader"
    ".pptx": "pptx",
    ".roff": "ms",
    ".rst": "rst",
    ".rtf": "rtf",
    ".s5": "s5",
    ".t2t": "t2t",
    ".tei": "tei",
    ".tei.xml": "tei",  # won't work, see https://github.com/jgm/pandoc/issues/7630>
    ".tex": "latex",
    ".texi": "texinfo",
    ".texinfo": "texinfo",
    ".text": "markdown",
    ".textile": "textile",
    ".txt": "markdown",
    ".wiki": "mediawiki",
    ".xhtml": "html",
    ".ipynb": "ipynb",
    ".csv": "csv",
    ".bib": "biblatex",
}

for _i in range(1, 10):
    _ext_to_file_format[f".{_i}"] = "man"


def format_from_filename(filename: str) -> Optional[str]:
    ext = os.path.splitext(filename)[1].lower()
    return _ext_to_file_format.get(ext)


_binary_formats = ["docx", "epub", "epub2", "epub3", "odt", "pdf", "pptx"]


# TODO: better management for pdf "format" which is not a format according
#       to pandoc ... ("latex" or "beamer" are, pdf is hidden in the filename
#       extension)


def write(
    doc: Any,
    file: Optional[Union[str, IO]] = None,
    format: Optional[str] = None,
    options: Optional[List[str]] = None,
) -> Union[str, bytes]:
    configuration = _get_configuration()

    if options is None:
        options = []

    elt = doc

    # wrap/unwrap Inline or MetaInlines into [Inline]
    if isinstance(elt, types.Inline):
        inline = elt
        elt = [inline]
    elif isinstance(elt, types.MetaInlines):
        meta_inlines = elt
        elt = meta_inlines[0]

    # wrap [Inline] into a Plain element
    if isinstance(elt, list) and all(isinstance(elt_, types.Inline) for elt_ in elt):
        inlines = elt
        elt = types.Plain(inlines)

    # wrap/unwrap Block or MetaBlocks into [Block]
    if isinstance(elt, types.Block):
        block = elt
        elt = [block]
    elif isinstance(elt, types.MetaBlocks):
        meta_blocks = elt
        elt = meta_blocks[0]

    # wrap [Block] into a Pandoc element
    if isinstance(elt, list) and all(isinstance(elt_, types.Block) for elt_ in elt):
        blocks = elt
        elt = types.Pandoc(types.Meta({}), blocks)

    if not isinstance(elt, types.Pandoc):
        raise TypeError(f"{elt!r} is not a Pandoc, Block, or Inline instance.")

    doc = elt

    filename = file if isinstance(file, str) else None

    if format is None and filename is not None:
        format = format_from_filename(filename)
        if format is None:
            warnings.warn(
                "Could not infer format from file extension, defaulting to markdown"
            )
            format = "markdown"
    elif format is None:
        format = "markdown"

    if format != "json" and configuration["path"] is None:
        error_msg = f"writing the {format!r} format requires the pandoc program"
        raise RuntimeError(error_msg)

    if utils.version_key(configuration["pandoc_types_version"]) < [1, 17]:
        json_ = write_json_v1(doc)
    else:
        json_ = write_json_v2(doc)

    json_str = json.dumps(json_)

    if format == "json":
        output = json_str
    else:
        pandoc_path = configuration["path"]
        options = ["-t", format] + options + ["-f", "json"]
        result = subprocess.run(
            [pandoc_path] + options, input=json_str.encode("utf-8"), capture_output=True
        )

        if result.returncode != 0:
            raise RuntimeError("pandoc error: " + result.stderr.decode("utf-8"))
        if len(result.stdout) == 0:
            raise RuntimeError("pandoc did not write any output to stdout")

        if format in _binary_formats:
            output = result.stdout
        else:
            output = result.stdout.decode("utf-8")

    if isinstance(file, str):
        mode = "wb" if isinstance(output, bytes) else "w"
        with open(file, mode) as f:
            f.write(output)
    elif isinstance(file, io.IOBase):
        file.write(output)

    return output


# JSON Reader v1
# ------------------------------------------------------------------------------
def read_json_v1(json_: Any, type_=None) -> Any:
    import_types()

    if type_ is None:
        type_ = types.Pandoc
    if isinstance(type_, str):
        type_ = getattr(types, type_)
    if not isinstance(type_, list):  # not a type def (yet).
        if issubclass(type_, types.Type):
            type_ = type_._def
        else:  # primitive type
            return type_(json_)

    if type_[0] == "type":  # type alias
        type_ = type_[1][1]
        return read_json_v1(json_, type_)
    if type_[0] == "list":
        item_type = type_[1][0]
        return [read_json_v1(item, item_type) for item in json_]
    if type_[0] == "tuple":
        tuple_types = type_[1]
        return tuple(
            read_json_v1(item, item_type)
            for (item, item_type) in zip(json_, tuple_types)
        )
    if type_[0] == "map":
        key_type, value_type = type_[1]
        return types.map(
            [
                (read_json_v1(k, key_type), read_json_v1(v, value_type))
                for (k, v) in json_.items()
            ]
        )

    data_type = None
    constructor = None
    if type_[0] in ("data", "newtype"):
        data_type = type_
        constructors = data_type[1][1]
        if len(constructors) == 1:
            constructor = constructors[0]
        else:
            constructor = getattr(types, json_["t"])._def
    elif type_[0][0].isupper():
        constructor = type_
        constructor_type = getattr(types, constructor[0])
        data_type = constructor_type.__bases__[1]._def

    single_type_constructor = len(data_type[1][1]) == 1
    single_constructor_argument = len(constructor[1][1]) == 1
    is_record = constructor[1][0] == "map"

    json_args = None
    args = None
    if not is_record:
        if single_type_constructor:
            json_args = json_
        else:
            json_args = json_["c"]
        if single_constructor_argument:
            json_args = [json_args]
        args = [read_json_v1(jarg, t) for jarg, t in zip(json_args, constructor[1][1])]
    else:
        keys = [k for k, t in constructor[1][1]]
        types_ = [t for k, t in constructor[1][1]]
        json_args = [json_[k] for k in keys]
        args = [read_json_v1(jarg, t) for jarg, t in zip(json_args, types_)]
    C = getattr(types, constructor[0])
    return C(*args)


# JSON Writer v1
# ------------------------------------------------------------------------------
def write_json_v1(object_: Any) -> Any:
    import_types()

    odict = collections.OrderedDict

    if not isinstance(object_, types.Type):
        if isinstance(object_, (list, tuple)):
            json_ = [write_json_v1(item) for item in object_]
        elif isinstance(object_, dict):
            json_ = odict((k, write_json_v1(v)) for k, v in object_.items())
        else:  # primitive type
            json_ = object_
    else:
        constructor = type(object_)._def
        data_type = type(object_).__bases__[1]._def
        single_type_constructor = len(data_type[1][1]) == 1
        single_constructor_argument = len(constructor[1][1]) == 1
        is_record = constructor[1][0] == "map"

        json_ = odict()
        if not single_type_constructor:
            json_["t"] = type(object_).__name__

        if not is_record:
            c = [write_json_v1(arg) for arg in object_]
            if single_constructor_argument:
                c = c[0]
            if single_type_constructor:
                json_ = c
            else:
                json_["c"] = c
        else:
            keys = [kt[0] for kt in constructor[1][1]]
            for key, arg in zip(keys, object_):
                json_[key] = write_json_v1(arg)
    return json_


# JSON Reader v2
# ------------------------------------------------------------------------------
def read_json_v2(json_, type_=None) -> Any:
    import_types()

    if type_ is None:
        type_ = types.Pandoc
    elif isinstance(type_, str):
        type_ = getattr(types, type_)

    if not isinstance(type_, list):  # not a type def (yet).
        if issubclass(type_, types.Type):
            type_ = type_._def
        else:  # primitive type
            return type_(json_)

    if type_[0] == "type":  # type alias
        type_ = type_[1][1]
        return read_json_v2(json_, type_)
    if type_[0] == "list":
        item_type = type_[1][0]
        return [read_json_v2(item, item_type) for item in json_]
    if type_[0] == "tuple":
        tuple_types = type_[1]
        return tuple(
            read_json_v2(item, item_type)
            for (item, item_type) in zip(json_, tuple_types)
        )
    if type_[0] == "map":
        key_type, value_type = type_[1]
        return types.map(
            [
                (read_json_v2(k, key_type), read_json_v2(v, value_type))
                for (k, v) in json_.items()
            ]
        )
    if type_[0] == "maybe":
        if json_ is None:
            return None
        else:
            value_type = type_[1][0]
            return read_json_v2(json_, value_type)

    data_type = None
    constructor = None
    if type_[0] in ("data", "newtype"):
        data_type = type_
        constructors = data_type[1][1]
        if len(constructors) == 1:
            constructor = constructors[0]
        else:
            constructors_names = [constructor[0] for constructor in constructors]
            constructor_name = json_["t"]
            if constructor_name not in constructors_names:  # shadowed
                constructor_name = constructor_name + "_"
                assert constructor_name in constructors_names
            constructor = getattr(types, constructor_name)._def
    elif type_[0][0].isupper():
        constructor = type_
        constructor_type = getattr(types, constructor[0])
        data_type = constructor_type.__bases__[1]._def

    single_type_constructor = len(data_type[1][1]) == 1
    single_constructor_argument = len(constructor[1][1]) == 1
    is_record = constructor[1][0] == "map"

    json_args = None
    args = None
    if constructor[0] == "Pandoc":
        # TODO; check API version compat
        meta = read_json_v2(json_["meta"], types.Meta)
        blocks = read_json_v2(json_["blocks"], ["list", ["Block"]])
        return types.Pandoc(meta, blocks)
    elif constructor[0] == "Meta":
        type_ = ["map", ["String", "MetaValue"]]
        return types.Meta(read_json_v2(json_, type_))
    elif not is_record:
        if single_type_constructor:
            json_args = json_
        else:
            json_args = json_.get("c", [])
        if single_constructor_argument:
            json_args = [json_args]
        args = [read_json_v2(jarg, t) for jarg, t in zip(json_args, constructor[1][1])]
    else:
        keys = [k for k, _ in constructor[1][1]]
        types_ = [t for _, t in constructor[1][1]]
        json_args = [json_[k] for k in keys]
        args = [read_json_v2(jarg, t) for jarg, t in zip(json_args, types_)]
    C = getattr(types, constructor[0])
    return C(*args)


# JSON Writer v2
# ------------------------------------------------------------------------------
def write_json_v2(object_: Any) -> Any:
    import_types()

    odict = collections.OrderedDict

    if not isinstance(object_, types.Type):
        if isinstance(object_, (list, tuple)):
            json_ = [write_json_v2(item) for item in object_]
        elif isinstance(object_, dict):
            json_ = odict((k, write_json_v2(v)) for k, v in object_.items())
        else:  # primitive type (including None used by Maybes)
            json_ = object_
    elif isinstance(object_, types.Pandoc):
        version = configure(read=True)["pandoc_types_version"]
        metadata = object_[0]
        blocks = object_[1]
        json_ = odict()
        json_["pandoc-api-version"] = [int(n) for n in version.split(".")]
        json_["meta"] = write_json_v2(metadata[0])
        json_["blocks"] = write_json_v2(blocks)
    else:
        constructor = type(object_)._def
        data_type = type(object_).__bases__[1]._def
        single_type_constructor = len(data_type[1][1]) == 1
        has_constructor_arguments = len(constructor[1][1]) >= 1
        single_constructor_argument = len(constructor[1][1]) == 1
        is_record = constructor[1][0] == "map"

        json_ = odict()
        if not single_type_constructor:
            type_name = type(object_).__name__
            # If an underscore was used to in the type name to avoid a name
            # collision between a constructor and its parent, remove it for
            # the json representation.
            json_["t"] = type_name.removesuffix("_")
        if not is_record:
            c = [write_json_v2(arg) for arg in object_]
            if single_constructor_argument:
                c = c[0]
            if single_type_constructor:
                json_ = c
            elif has_constructor_arguments:
                json_["c"] = c
        else:
            keys = [kt[0] for kt in constructor[1][1]]
            for key, arg in zip(keys, object_):
                json_[key] = write_json_v2(arg)
    return json_


# Iteration
# ------------------------------------------------------------------------------
def iter(
    elt: Any, path: Union[bool, List[Any]] = False
) -> Union[Any, Tuple[Any, List[Any]]]:
    if path is True:
        path = []
    elif path is not False and not isinstance(path, list):
        warnings.warn(f"Invalid path={path!r}, defaulting to []")
        path = []

    if path is False:
        yield elt
    else:
        yield elt, path

    if isinstance(elt, dict):
        elt = elt.items()

    if hasattr(elt, "__iter__") and not isinstance(elt, types.String):
        for i, child in enumerate(elt):
            if path is False:
                child_path = False
            else:
                child_path = path + [(elt, i)]
            for subelt in iter(child, path=child_path):
                yield subelt


# Functional Transformation Patterns (Scrap-Your-Boilerplate-ish)
# ------------------------------------------------------------------------------
def _apply_post_order(f: Callable[[Any], Any], elt: Any) -> Any:
    if isinstance(elt, types.Type):
        new_children = [_apply_post_order(f, child) for child in elt]
        return f(type(elt)(*new_children))
    elif isinstance(elt, dict):
        new_children = [_apply_post_order(f, child) for child in elt.items()]
        return f(dict(new_children))
    elif hasattr(elt, "__iter__") and not isinstance(elt, types.String):
        assert isinstance(elt, list) or isinstance(elt, tuple)
        new_children = [_apply_post_order(f, child) for child in elt]
        return f(type(elt)(new_children))
    else:
        return f(elt)


def apply(f: Callable[[Any], Any], elt: Any = None) -> Any:
    """apply the transform f bottom-up"""
    import_types()

    def f_(elt):  # sugar: no return value means no change
        return new_elt if (new_elt := f(elt)) is not None else elt

    return _apply_post_order(f_, elt)


# Main Entry Point
# ------------------------------------------------------------------------------
# TODO: use argparse.FileType and access the filename attribute when needed.
#       see https://stackoverflow.com/questions/19656426/how-to-get-filename-with-argparse-while-specifying-type-filetype-for-this-a
def main():
    prog = "python -m pandoc"
    description = "Read/write pandoc documents with Python"
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.set_defaults(command=None)
    subparsers = parser.add_subparsers()
    read_parser = subparsers.add_parser("read")
    read_parser.set_defaults(command="read")
    read_parser.add_argument(
        "file", nargs="?", metavar="FILE", default=None, help="input file"
    )
    read_parser.add_argument(
        "-f", "--format", nargs="?", default=None, help="input format"
    )
    read_parser.add_argument(
        "-o", "--output", nargs="?", default=None, help="output file"
    )
    write_parser = subparsers.add_parser("write")
    write_parser.set_defaults(command="write")
    write_parser.add_argument(
        "file", nargs="?", metavar="FILE", default=None, help="input file"
    )
    write_parser.add_argument(
        "-f", "--format", nargs="?", default=None, help="output format"
    )
    write_parser.add_argument(
        "-o", "--output", nargs="?", default=None, help="output file"
    )
    args = parser.parse_args()
    if args.command == "read":
        if args.file is None:
            file = sys.stdin
        else:
            file = args.file
        doc = read(file=file, format=args.format)
        content = str(doc) + "\n"
        if args.output is None:
            output = sys.stdout.buffer
        else:
            output = open(args.output, "wb")
        assert "b" in output.mode
        content = content.encode("utf-8")
        output.write(content)
    elif args.command == "write":
        if args.file is None:
            # We always interpret the standard input stream as utf-8 ;
            # see <https://pandoc.org/MANUAL.html#character-encoding>
            file = sys.stdin.buffer  # sys.stdin may not be utf-8.
            assert "b" in file.mode
            doc_bytes = file.read()
            doc_string = doc_bytes.decode("utf-8")
        else:
            file = open(args.file, mode="r", encoding="utf-8")
            doc_string = file.read()
        import_types()
        globs = types.__dict__.copy()
        doc = eval(doc_string, globs)
        if args.output is None:
            output = sys.stdout.buffer
        else:
            output = args.output
        write(doc, file=output, format=args.format)
