import subprocess


def get_version(version=None):
    "Returns a PEP 386-compliant version number from VERSION."

    if version is None:
        from geventwebsocket import VERSION as version
    else:
        assert len(version) == 5
        assert version[3] in ('alpha', 'beta', 'rc', 'final')

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases

    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        hg_changeset = get_hg_changeset()
        if hg_changeset:
            sub = '.dev{0}'.format(hg_changeset)

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return str(main + sub)


def get_hg_changeset():
    rev, err = subprocess.Popen(
        'hg id -i',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ).communicate()

    if err:
        return None
    else:
        return rev.strip().replace('+', '')
