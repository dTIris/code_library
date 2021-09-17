# -*- coding:utf-8 -*-

from typing import List


def bubbling(arr: List):
    for i in range(len(arr)-1):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]:
                arr[i], arr[j] = arr[j], arr[i]


def get_mid(arr: List, left: int, right: int):
    key = arr[left]
    while left < right:
        while left < right and arr[right] < key:
            right -= 1
        while left < right and arr[left] > key:

def fast(arr: List, left: int, right: int):
    if left < right:
        mid = get_mid(arr, left, right)
        fast(arr, left, mid+1)
        fast(arr, mid-1, right)


def main():
    arr = [3,1,8,4,6,2]
    bubbling(arr)
    print(arr)

if __name__ == "__main__":
    main()