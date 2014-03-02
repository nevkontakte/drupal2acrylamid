def gen_dict(cur):
    names = [x[0].lower() for x in cur.description]
    for row in cur:
        yield dict(zip(names, row))
