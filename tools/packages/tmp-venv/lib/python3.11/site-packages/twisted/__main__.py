# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

# Make the twisted module executable with the default behaviour of
# running twist.
# This is not a docstring to avoid changing the string output of twist.


import sys

if __name__ == "__main__":
    from twisted.application.twist._twist import Twist

    sys.exit(Twist.main())
