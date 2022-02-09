from common import get_data

for branch_name in get_data().keys():
    _b = get_data()[branch_name]['details']
    for r in _b:
        print(r['label'])
