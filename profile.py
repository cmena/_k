def load(path):
    """load the user's profile by evaling the contents of path in the profile.py
    namespace.

    """
    with open(path) as infile:
        exec(infile.read(), globals())
