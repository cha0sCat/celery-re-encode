from subprocess import PIPE, run


class GitError(Exception):
    pass


def git_pull():
    result = run(
        ["git", "pull"],
        stdout=PIPE, stderr=PIPE
    )

    if result.returncode != 0:
        raise GitError(
            'git pull failed! \n'
            'stdout:{} \n'
            'stderr:{}'.format(
                result.stdout.decode(errors='ignore'),
                result.stderr.decode(errors='ignore')
            ))
