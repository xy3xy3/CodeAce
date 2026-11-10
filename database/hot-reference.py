# Original CodeAce reference implementations. Each section is independently runnable.
# @1529
class Solution:
    def subsets(self, nums):
        ans = [[]]
        for x in nums:
            ans += [part + [x] for part in ans]
        return ans
# @1530
class Solution:
    def letterCombinations(self, digits):
        if not digits:
            return []
        letters = {'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}
        ans = ['']
        for digit in digits:
            ans = [prefix + c for prefix in ans for c in letters[digit]]
        return ans
# @1531
class Solution:
    def combinationSum(self, candidates, target):
        values = sorted(candidates)
        ans = []
        def visit(start, remain, path):
            if remain == 0:
                ans.append(path[:])
                return
            for i in range(start, len(values)):
                x = values[i]
                if x > remain:
                    break
                path.append(x)
                visit(i, remain - x, path)
                path.pop()
        visit(0, target, [])
        return ans
# @1532
class Solution:
    def generateParenthesis(self, n):
        ans = []
        def visit(s, opened, closed):
            if len(s) == n * 2:
                ans.append(s)
                return
            if opened < n:
                visit(s + '(', opened + 1, closed)
            if closed < opened:
                visit(s + ')', opened, closed + 1)
        visit('', 0, 0)
        return ans
# @1533
class Solution:
    def partition(self, s):
        ans = []
        def visit(start, path):
            if start == len(s):
                ans.append(path[:])
                return
            for end in range(start + 1, len(s) + 1):
                part = s[start:end]
                if part == part[::-1]:
                    path.append(part)
                    visit(end, path)
                    path.pop()
        visit(0, [])
        return ans
# @1534
class Solution:
    def solveNQueens(self, n):
        ans, cols, diag1, diag2, board = [], set(), set(), set(), []
        def visit(row):
            if row == n:
                ans.append(board[:])
                return
            for col in range(n):
                if col in cols or row-col in diag1 or row+col in diag2:
                    continue
                cols.add(col); diag1.add(row-col); diag2.add(row+col)
                board.append('.' * col + 'Q' + '.' * (n-col-1))
                visit(row + 1)
                board.pop()
                cols.remove(col); diag1.remove(row-col); diag2.remove(row+col)
        visit(0)
        return ans
# @1535
class Solution:
    def searchInsert(self, nums, target):
        left, right = 0, len(nums)
        while left < right:
            mid = (left + right) // 2
            if nums[mid] < target:
                left = mid + 1
            else:
                right = mid
        return left
# @1536
class Solution:
    def searchRange(self, nums, target):
        from bisect import bisect_left, bisect_right
        left = bisect_left(nums, target)
        if left == len(nums) or nums[left] != target:
            return [-1, -1]
        return [left, bisect_right(nums, target) - 1]
# @1537
class Solution:
    def search(self, nums, target):
        left, right = 0, len(nums)-1
        while left <= right:
            mid = (left + right) // 2
            if nums[mid] == target:
                return mid
            if nums[left] <= nums[mid]:
                if nums[left] <= target < nums[mid]:
                    right = mid - 1
                else:
                    left = mid + 1
            else:
                if nums[mid] < target <= nums[right]:
                    left = mid + 1
                else:
                    right = mid - 1
        return -1
# @1538
class Solution:
    def findMin(self, nums):
        left, right = 0, len(nums)-1
        while left < right:
            mid = (left + right) // 2
            if nums[mid] > nums[right]:
                left = mid + 1
            else:
                right = mid
        return nums[left]
# @1539
class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        a, b = nums1, nums2
        if len(a) > len(b):
            a, b = b, a
        m, n = len(a), len(b)
        left, right = 0, m
        half = (m+n+1)//2
        while left <= right:
            i = (left+right)//2
            j = half-i
            al = a[i-1] if i else float('-inf')
            ar = a[i] if i < m else float('inf')
            bl = b[j-1] if j else float('-inf')
            br = b[j] if j < n else float('inf')
            if al > br:
                right = i-1
            elif bl > ar:
                left = i+1
            elif (m+n) % 2:
                return max(al, bl)
            else:
                return (max(al, bl)+min(ar, br))/2
# @1540
class Solution:
    def isValid(self, s):
        stack = []
        pairs = {')':'(', ']':'[', '}':'{'}
        for c in s:
            if c in '([{':
                stack.append(c)
            elif not stack or stack.pop() != pairs[c]:
                return False
        return not stack
# @1541
class MinStack:
    def __init__(self):
        self.stack = []
    def push(self, val):
        minimum = min(val, self.stack[-1][1]) if self.stack else val
        self.stack.append((val, minimum))
    def pop(self):
        self.stack.pop()
    def top(self):
        return self.stack[-1][0]
    def getMin(self):
        return self.stack[-1][1]
# @1542
class Solution:
    def decodeString(self, s):
        stack, current, number = [], '', 0
        for c in s:
            if c.isdigit():
                number = number * 10 + int(c)
            elif c == '[':
                stack.append((current, number))
                current, number = '', 0
            elif c == ']':
                prefix, count = stack.pop()
                current = prefix + current * count
            else:
                current += c
        return current
# @1543
class Solution:
    def dailyTemperatures(self, temperatures):
        ans, stack = [0]*len(temperatures), []
        for i, value in enumerate(temperatures):
            while stack and temperatures[stack[-1]] < value:
                previous = stack.pop()
                ans[previous] = i-previous
            stack.append(i)
        return ans
# @1544
class Solution:
    def largestRectangleArea(self, heights):
        stack, ans = [-1], 0
        values = heights + [0]
        for i, height in enumerate(values):
            while stack[-1] != -1 and values[stack[-1]] > height:
                h = values[stack.pop()]
                ans = max(ans, h * (i-stack[-1]-1))
            stack.append(i)
        return ans
# @1545
class Solution:
    def findKthLargest(self, nums, k):
        import heapq
        heap = []
        for x in nums:
            if len(heap) < k:
                heapq.heappush(heap, x)
            elif x > heap[0]:
                heapq.heapreplace(heap, x)
        return heap[0]
# @1546
class Solution:
    def topKFrequent(self, nums, k):
        from collections import Counter
        import heapq
        counts = Counter(nums)
        return heapq.nlargest(k, counts, key=counts.get)
# @1547
class MedianFinder:
    def __init__(self):
        self.low, self.high = [], []
    def addNum(self, num):
        import heapq
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))
    def findMedian(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0]+self.high[0])/2
# @1548
class Solution:
    def maxProfit(self, prices):
        lowest, ans = prices[0], 0
        for price in prices:
            ans = max(ans, price-lowest)
            lowest = min(lowest, price)
        return ans
# @1549
class Solution:
    def canJump(self, nums):
        farthest = 0
        for i, jump in enumerate(nums):
            if i > farthest:
                return False
            farthest = max(farthest, i+jump)
            if farthest >= len(nums)-1:
                return True
        return True
# @1550
class Solution:
    def jump(self, nums):
        steps, end, farthest = 0, 0, 0
        for i in range(len(nums)-1):
            farthest = max(farthest, i+nums[i])
            if i == end:
                steps += 1
                end = farthest
        return steps
# @1551
class Solution:
    def partitionLabels(self, s):
        last = {c:i for i,c in enumerate(s)}
        start, end, ans = 0, 0, []
        for i,c in enumerate(s):
            end = max(end, last[c])
            if i == end:
                ans.append(end-start+1)
                start = i+1
        return ans
# @1552
class Solution:
    def climbStairs(self, n):
        a, b = 1, 1
        for _ in range(n):
            a, b = b, a+b
        return a
# @1553
class Solution:
    def generate(self, numRows):
        ans = []
        for i in range(numRows):
            row = [1]*(i+1)
            for j in range(1, i):
                row[j] = ans[-1][j-1]+ans[-1][j]
            ans.append(row)
        return ans
# @1554
class Solution:
    def rob(self, nums):
        previous, current = 0, 0
        for value in nums:
            previous, current = current, max(current, previous+value)
        return current
# @1555
class Solution:
    def numSquares(self, n):
        squares = [i*i for i in range(1, int(n**0.5)+1)]
        dp = [0]+[n+1]*n
        for value in range(1, n+1):
            for square in squares:
                if square > value:
                    break
                dp[value] = min(dp[value], dp[value-square]+1)
        return dp[n]
# @1556
class Solution:
    def coinChange(self, coins, amount):
        dp = [0]+[amount+1]*amount
        for value in range(1, amount+1):
            for coin in coins:
                if coin <= value:
                    dp[value] = min(dp[value], dp[value-coin]+1)
        return dp[amount] if dp[amount] <= amount else -1
# @1557
class Solution:
    def wordBreak(self, s, wordDict):
        words, dp = set(wordDict), [True]+[False]*len(s)
        max_length = max(map(len, words), default=0)
        for end in range(1, len(s)+1):
            dp[end] = any(dp[start] and s[start:end] in words
                          for start in range(max(0, end-max_length), end))
        return dp[-1]
# @1558
class Solution:
    def lengthOfLIS(self, nums):
        from bisect import bisect_left
        tails = []
        for value in nums:
            i = bisect_left(tails, value)
            if i == len(tails):
                tails.append(value)
            else:
                tails[i] = value
        return len(tails)
# @1559
class Solution:
    def maxProduct(self, nums):
        low = high = ans = nums[0]
        for value in nums[1:]:
            low, high = min(value, low*value, high*value), max(value, low*value, high*value)
            ans = max(ans, high)
        return ans
# @1560
class Solution:
    def canPartition(self, nums):
        total = sum(nums)
        if total % 2:
            return False
        target = total//2
        bits = 1
        mask = (1 << (target+1))-1
        for value in nums:
            bits = (bits | (bits << value)) & mask
        return bool(bits & (1 << target))
# @1561
class Solution:
    def longestValidParentheses(self, s):
        stack, ans = [-1], 0
        for i,c in enumerate(s):
            if c == '(':
                stack.append(i)
            else:
                stack.pop()
                if not stack:
                    stack.append(i)
                else:
                    ans = max(ans, i-stack[-1])
        return ans
# @1562
class Solution:
    def uniquePaths(self, m, n):
        dp = [1]*n
        for _ in range(1, m):
            for j in range(1, n):
                dp[j] += dp[j-1]
        return dp[-1]
# @1563
class Solution:
    def minPathSum(self, grid):
        dp = [float('inf')]*len(grid[0])
        dp[0] = 0
        for row in grid:
            for j, value in enumerate(row):
                dp[j] = value + min(dp[j], dp[j-1] if j else float('inf'))
        return dp[-1]
# @1564
class Solution:
    def longestPalindrome(self, s):
        best_start, best_length = 0, 0
        for center in range(len(s)):
            for left, right in ((center,center),(center,center+1)):
                while left >= 0 and right < len(s) and s[left] == s[right]:
                    length = right-left+1
                    if length > best_length or (length == best_length and left < best_start):
                        best_start, best_length = left, length
                    left -= 1
                    right += 1
        return s[best_start:best_start+best_length]
# @1565
class Solution:
    def longestCommonSubsequence(self, text1, text2):
        dp = [0]*(len(text2)+1)
        for a in text1:
            diagonal = 0
            for j,b in enumerate(text2, 1):
                old = dp[j]
                dp[j] = diagonal+1 if a == b else max(dp[j], dp[j-1])
                diagonal = old
        return dp[-1]
# @1566
class Solution:
    def minDistance(self, word1, word2):
        dp = list(range(len(word2)+1))
        for i,a in enumerate(word1, 1):
            diagonal, dp[0] = dp[0], i
            for j,b in enumerate(word2, 1):
                old = dp[j]
                dp[j] = diagonal if a == b else 1+min(diagonal, dp[j], dp[j-1])
                diagonal = old
        return dp[-1]
# @1567
class Solution:
    def singleNumber(self, nums):
        ans = 0
        for value in nums:
            ans ^= value
        return ans
# @1568
class Solution:
    def majorityElement(self, nums):
        candidate, count = None, 0
        for value in nums:
            if count == 0:
                candidate = value
            count += 1 if value == candidate else -1
        return candidate
# @1569
class Solution:
    def sortColors(self, nums):
        left, i, right = 0, 0, len(nums)-1
        while i <= right:
            if nums[i] == 0:
                nums[left], nums[i] = nums[i], nums[left]
                left += 1
                i += 1
            elif nums[i] == 2:
                nums[right], nums[i] = nums[i], nums[right]
                right -= 1
            else:
                i += 1
# @1570
class Solution:
    def nextPermutation(self, nums):
        i = len(nums)-2
        while i >= 0 and nums[i] >= nums[i+1]:
            i -= 1
        if i >= 0:
            j = len(nums)-1
            while nums[j] <= nums[i]:
                j -= 1
            nums[i], nums[j] = nums[j], nums[i]
        left, right = i+1, len(nums)-1
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1
# @1571
class Solution:
    def findDuplicate(self, nums):
        slow = fast = nums[0]
        while True:
            slow, fast = nums[slow], nums[nums[fast]]
            if slow == fast:
                break
        slow = nums[0]
        while slow != fast:
            slow, fast = nums[slow], nums[fast]
        return slow
