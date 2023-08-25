def all_equal(iterator):
    first = iterator[0]
    return all(first == x for x in iterator)

a = ["1", "1", "1", "2"]
print (all_equal(a))
