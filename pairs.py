def pairs(items):
    i = 0
    count = len(items)

    while i < count:

        k = i + 1

        while k < count:

            yield items[i], items[k]

            k += 1

        i += 1