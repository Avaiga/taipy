from __future__ import print_function, absolute_import
import argparse
import sys

from .slugify import slugify, DEFAULT_SEPARATOR


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Slug string")

    input_group = parser.add_argument_group(description="Input")
    input_group.add_argument("input_string", nargs='*',
                             help='Text to slugify')
    input_group.add_argument("--stdin", action='store_true',
                             help="Take the text from STDIN")

    parser.add_argument("--no-entities", action='store_false', dest='entities', default=True,
                        help="Do not convert HTML entities to unicode")
    parser.add_argument("--no-decimal", action='store_false', dest='decimal', default=True,
                        help="Do not convert HTML decimal to unicode")
    parser.add_argument("--no-hexadecimal", action='store_false', dest='hexadecimal', default=True,
                        help="Do not convert HTML hexadecimal to unicode")
    parser.add_argument("--max-length", type=int, default=0,
                        help="Output string length, 0 for no limit")
    parser.add_argument("--word-boundary", action='store_true', default=False,
                        help="Truncate to complete word even if length ends up shorter than --max_length")
    parser.add_argument("--save-order", action='store_true', default=False,
                        help="When set and --max_length > 0 return whole words in the initial order")
    parser.add_argument("--separator", type=str, default=DEFAULT_SEPARATOR,
                        help="Separator between words. By default " + DEFAULT_SEPARATOR)
    parser.add_argument("--stopwords", nargs='+',
                        help="Words to discount")
    parser.add_argument("--regex-pattern",
                        help="Python regex pattern for disallowed characters")
    parser.add_argument("--no-lowercase", action='store_false', dest='lowercase', default=True,
                        help="Activate case sensitivity")
    parser.add_argument("--replacements", nargs='+',
                        help="""Additional replacement rules e.g. "|->or", "%%->percent".""")
    parser.add_argument("--allow-unicode", action='store_true', default=False,
                        help="Allow unicode characters")

    args = parser.parse_args(argv[1:])

    if args.input_string and args.stdin:
        parser.error("Input strings and --stdin cannot work together")

    if args.replacements:
        def split_check(repl):
            SEP = '->'
            if SEP not in repl:
                parser.error("Replacements must be of the form: ORIGINAL{SEP}REPLACED".format(SEP=SEP))
            return repl.split(SEP, 1)
        args.replacements = [split_check(repl) for repl in args.replacements]

    if args.input_string:
        args.input_string = " ".join(args.input_string)
    elif args.stdin:
        args.input_string = sys.stdin.read()

    if not args.input_string:
        args.input_string = ''

    return args


def slugify_params(args):
    return dict(
        text=args.input_string,
        entities=args.entities,
        decimal=args.decimal,
        hexadecimal=args.hexadecimal,
        max_length=args.max_length,
        word_boundary=args.word_boundary,
        save_order=args.save_order,
        separator=args.separator,
        stopwords=args.stopwords,
        lowercase=args.lowercase,
        replacements=args.replacements,
        allow_unicode=args.allow_unicode
    )


def main(argv=None):  # pragma: no cover
    """ Run this program """
    if argv is None:
        argv = sys.argv
    args = parse_args(argv)
    params = slugify_params(args)
    try:
        print(slugify(**params))
    except KeyboardInterrupt:
        sys.exit(-1)


if __name__ == '__main__':  # pragma: no cover
    main()
