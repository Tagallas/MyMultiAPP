

def sort_task(table):
    merge_sort(table, 0, len(table)-1)


def merge_sort(A, p, r):
    if p >= r:
        return
    q = int((p + r) / 2)
    merge_sort(A, p, q)
    merge_sort(A, q + 1, r)
    merge(A, p, q, r)


def merge(A, p, q, r):
    n1 = q - p + 1
    n2 = r - q

    L = A[p:p+n1]
    M = A[q+1:q+1+n2]

    i = 0
    j = 0
    k = p

    while i < n1 and j < n2:
        if L[i].value()[0] < M[j].value()[0]:
            A[k] = L[i]
            i += 1
        elif L[i].value()[0] > M[j].value()[0]:
            A[k] = M[j]
            j += 1
        else:
            if L[i].value()[1] <= M[j].value()[1]:
                A[k] = L[i]
                i += 1
            else:
                A[k] = M[j]
                j += 1
        k += 1

    while i < n1:
        A[k] = L[i]
        i += 1
        k += 1

    while j < n2:
        A[k] = M[j]
        j += 1
        k += 1
