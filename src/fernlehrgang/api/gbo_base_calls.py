import requests


def get_it(url, headers):
    result = requests.get(url, headers=headers)
    #if result.status_code not in (201, 409):
    #    raise "Not Correct Response Code"
    return result


def set_it(url, data, headers):
    result = requests.post(url, json=data, headers=headers)
    return result


def success(job, connection, result, *args, **kwargs):
    import pdb; pdb.set_trace()
