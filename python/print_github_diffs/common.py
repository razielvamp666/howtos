from github import Github
from conf import token, organization_name
from functools import cache


_org = Github(token).get_organization(organization_name)


@cache
def get_repo(name):
    return _org.get_repo(name)


@cache
def get_pull(id, repo):
    return repo.get_pull(id)


@cache
def get_data(data=None):

    if data is None:
        from conf import input_data
        data = input_data

    for repo_name in data.keys():
        data[repo_name]['repo'] = get_repo(repo_name)
        for pr_id in data[repo_name]['ids']:
            _pr = get_pull(pr_id, data[repo_name]['repo'])
            url = f'https://github.com/{organization_name}/{repo_name}/pull/{pr_id}'
            data[repo_name]['details'].append(
                {
                    'number:': _pr.number,
                    'title': _pr.title,
                    'url': url,
                    'user': _pr.user.login,
                    'label': f'- `{_pr.number}` [{_pr.title}]({url}) 【last change time：{_pr.updated_at.strftime("%Y/%m%/%d %H:%M:%S")}】＜num of files：{_pr.changed_files}＞',  # noqa: E501
                    'files': [f.filename for f in _pr.get_files()]
                }
            )

    return data


@cache
def get_files(pr):
    return pr.get_files()


def get_diffs(pr):

    diffs = {}

    if isinstance(pr, list):
        fls = list(get_files(get_pull(pr[0], get_repo(pr[1]))))
    else:
        fls = list(get_files(pr))
    group = fls[0].filename.split('/')[0]
    diffs[group] = []

    for f in fls:
        _g = f.filename.split('/')[0]
        if _g != group:
            group = _g
            diffs[group] = []
        diffs[group].append(
            {
                'filename': f.filename,
                'diff': f.patch
            }
        )
    return diffs


def print_diffs(pr, group=None):

    diffs = get_diffs(pr)

    if group is not None:
        diffs = {group: diffs[group]}

    for group, files in diffs.items():

        print()
        print(f'### `{group}`')
        print()

        for f in files:
            print(f'- `{f["filename"]}`')
            print()
            print('```')
            print(f['diff'])
            print('```')
            print()
