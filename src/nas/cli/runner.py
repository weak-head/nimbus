from argparse import Namespace

from nas.factory.command import CommandFactory


def up(args: Namespace, factory: CommandFactory):
    factory.create_up().execute(args.selectors)


def down(args: Namespace, factory: CommandFactory):
    factory.create_down().execute(args.selectors)


def backup(args: Namespace, factory: CommandFactory):
    factory.create_backup().execute(args.selectors)
