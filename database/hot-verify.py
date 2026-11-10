"""Deterministic independent oracle checks for trusted, authored references only.

Run: python3 database/hot-verify.py
No user submissions, external calls, or credentials are involved.
"""
import bisect
import itertools
import random
import re
from pathlib import Path

source = Path(__file__).with_name('hot-reference.py').read_text()
def solution(id):
    code = re.search(rf'# @{id}\n([\s\S]*?)(?=\n# @|$)', source)[1]
    scope = {}
    exec(compile(code, '<trusted-hot-reference>', 'exec'), scope)
    return scope['Solution']()

rng = random.Random(20261110)
checks = 0
for _ in range(200):
    nums = [rng.randrange(-4, 5) for _ in range(rng.randrange(1, 8))]
    # Exhaustively enumerate subsequences and contiguous intervals independently.
    lis = max(len(part) for size in range(1, len(nums)+1)
              for part in itertools.combinations(nums, size)
              if all(a < b for a,b in zip(part, part[1:])))
    assert solution(1558).lengthOfLIS(nums) == lis
    products = []
    for start in range(len(nums)):
        product = 1
        for end in range(start, len(nums)):
            product *= nums[end]
            products.append(product)
    assert solution(1559).maxProduct(nums) == max(products)
    assert solution(1545).findKthLargest(nums, 1) == max(nums)
    assert solution(1545).findKthLargest(nums, len(nums)) == min(nums)
    heights = [abs(value) for value in nums]
    area = max(min(heights[i:j])*(j-i) for i in range(len(nums)) for j in range(i+1,len(nums)+1))
    assert solution(1544).largestRectangleArea(heights) == area
    permutations = sorted(set(itertools.permutations(nums)))
    current = tuple(nums)
    expected = permutations[(permutations.index(current)+1) % len(permutations)]
    copy = nums[:]
    solution(1570).nextPermutation(copy)
    assert tuple(copy) == expected
    s = ''.join(rng.choice('abc') for _ in range(8))
    candidates = [(s[i:j],i) for i in range(len(s)) for j in range(i+1,len(s)+1) if s[i:j] == s[i:j][::-1]]
    expected = min(candidates, key=lambda item: (-len(item[0]),item[1]))[0]
    assert solution(1564).longestPalindrome(s) == expected
    checks += 7

for _ in range(500):
    nums = sorted(rng.sample(range(-30,30),rng.randrange(1,20)))
    split = rng.randrange(len(nums))
    rotated = nums[split:] + nums[:split]
    target = rng.randrange(-32,32)
    assert solution(1537).search(rotated,target) == (rotated.index(target) if target in rotated else -1)
    assert solution(1538).findMin(rotated) == min(nums)
    assert solution(1535).searchInsert(nums,target) == bisect.bisect_left(nums,target)
    a = sorted(rng.choices(range(-9,10),k=rng.randrange(8)))
    b = sorted(rng.choices(range(-9,10),k=rng.randrange(1,8)))
    combined = sorted(a+b)
    expected = (combined[(len(combined)-1)//2]+combined[len(combined)//2])/2
    assert solution(1539).findMedianSortedArrays(a,b) == expected
    n = rng.randrange(1,30)
    duplicate = rng.randrange(1,n+1)
    values = list(range(1,n+1))+[duplicate]
    rng.shuffle(values)
    assert solution(1571).findDuplicate(values) == duplicate
    checks += 5

print(f'{checks} independent deterministic oracle checks passed')
