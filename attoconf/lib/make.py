#   Copyright 2013 Ben Longbons <b.r.longbons@gmail.com>
#
#   This file is part of attoconf.
#
#   attoconf is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   attoconf is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with attoconf.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, division, absolute_import

import os

from ..classy import ClassyProject
from ..version import string as version_string

blacklist = frozenset(''.join(chr(i) for i in range(0x20)) + '#$')
def validate(s):
    return s == s.strip() and not frozenset(s) & blacklist


class MakeHook(object):
    __slots__ = ('infile', 'outfile')
    def __init__(self, infile, outfile):
        self.infile = infile
        self.outfile = outfile

    def __call__(self, build):
        if self.outfile is None:
            # if there are multiple backends
            print('Skipping generation of a makefile')
            return
        with open(os.path.join(build.builddir, self.outfile), 'w') as out:
            print('Generating a makefile ...')
            out.write('# This part was generated by %s\n' % version_string)
            out.write('SRC_DIR = %s\n' % build.relative_source())
            out.write('\n')
            # TODO preserve *original* order?
            for var, (val, origin) in sorted(build.vars.iteritems()):
                if val is None:
                    if origin == 'default':
                        continue
                    # is it a good idea for Nones to survive this long?
                    # especially conditional ones ...
                    var = '# ' + var
                    val = 'not defined'
                out.write('%s = %s # %s\n' % (var, val, origin))
            if self.infile is not None:
                out.write('\n# The rest was copied from %s\n' % self.infile)
                infile = os.path.join(build.project.srcdir, self.infile)
                with open(infile) as in_:
                    for line in in_:
                        assert line.endswith('\n')
                        out.write(line)


class Make(ClassyProject):
    ''' Post hook to generate a Makefile from Makefile.in
    '''
    __slots__ = ()
    @classmethod
    def slots(cls):
        return super(Make, cls).slots() + ('make_in', 'make_out')

    def __init__(self, srcdir):
        super(Make, self).__init__(srcdir)
        self.set_make_infile('Makefile.in')
        self.set_make_outfile('Makefile') # relative to build dir

    def set_make_infile(self, ipath):
        self.make_in = ipath

    def set_make_outfile(self, opath):
        self.make_out = opath

    def post(self):
        super(Make, self).post()
        self.checks.append(MakeHook(self.make_in, self.make_out))
