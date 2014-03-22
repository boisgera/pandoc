# coding: utf-8

__project__ = "pandoc"
__author__  = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>"
__version__ = "1.0.0-alpha"
__license__ = "MIT License"
__url__     = "https://github.com/boisgera/pandoc"

export = "project author version license url".split()
__all__ = ["__" + name + "__" for name in export]

