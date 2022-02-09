from os import environ as e


with open('token.txt', 'r') as f:
    token = f.read().strip('\n\r\t ')

organization_name = e.get('ORG_NAME', 'some_default_org')

input_data = {
    'repo_name_1': {
        # pull request ids
        'ids': [1, 2, 3],
        'repo': None,
        'details': []
    },
    'repo_name_2': {
        'ids': [11, 12, 13],
        'repo': None,
        'details': []
    }
}
