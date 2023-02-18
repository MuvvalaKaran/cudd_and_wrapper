from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

setup(
    name = "PyDD",
    version = "1.0.0",
    description = "Python wrapper for the CUDD decision diagram library",
    author = "Fabio Somenzi",
    author_email = "Fabio@Colorado.EDU",
    url = "http://vlsi.colorado.edu/~fabio",
    ext_modules = cythonize([
        Extension("cudd", ["cudd.pyx"],
                  libraries=["cudd"])])
)
