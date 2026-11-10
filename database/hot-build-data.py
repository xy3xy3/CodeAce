"""Rebuild original Hot100 metadata. This script never accesses the network."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
rows = []
def add(id, method, args, description, output, idea, complexity, cases, compare='json', tags=()):
    rows.append(dict(id=id, method=method, args=args.split(',') if args else [], description=description,
                     output=output, idea=idea, complexity=complexity,
                     cases=[dict(input=i, expected=o) for i,o in cases], compare=compare, tags=list(tags)))
add(1529,'subsets','nums','给定互不相同的整数数组 nums，返回它的全部子集（幂集），包括空集和数组本身。每个子集只能出现一次。子集内元素顺序以及各子集的排列顺序均不影响答案。','二维整数数组，包含所有子集。','从只含空集的结果开始。处理一个新元素时，将已有每个子集复制一份并加入该元素，再与原结果合并。','时间 O(n·2^n)，额外空间 O(n·2^n)（含结果）。',[
({'nums':[1,2]},[[],[1],[2],[1,2]]),({'nums':[0]},[[],[0]]),({'nums':[-1,0,2]},[[],[-1],[0],[-1,0],[2],[-1,2],[0,2],[-1,0,2]])], 'unordered_nested', ['回溯'])
add(1530,'letterCombinations','digits','电话按键 2 到 9 分别对应 abc、def、ghi、jkl、mno、pqrs、tuv、wxyz。给定数字字符串 digits，按数字原有顺序各选一个字母，返回全部可能字符串。每种组合返回一次，结果顺序不限。本练习也接受空字符串，此时返回空数组。','字符串数组。','逐个处理数字，把当前所有前缀分别与该按键的字母拼接。空输入单独返回空数组。','时间 O(L·4^L)，空间 O(L·4^L)（含结果），L 为数字个数。',[
({'digits':'23'},['ad','ae','af','bd','be','bf','cd','ce','cf']),({'digits':'2'},['a','b','c']),({'digits':''},[]),({'digits':'7'},['p','q','r','s'])], 'unordered_json',['回溯'])
add(1531,'combinationSum','candidates,target','给定互不相同的正整数 candidates 和正整数 target。每个候选数可以重复使用任意次，返回所有元素之和等于 target 的组合。同一组数的不同排列视为一个组合；不得重复返回。组合内以及组合之间的顺序不限。无法凑出时返回空数组。','二维整数数组。','先排序。回溯选择下标不小于上一次选择下标的数，允许继续选当前数；超过剩余目标即可剪枝，剩余为零时记录。','设最小候选数为 c，搜索深度至多 target/c；时间与枚举的搜索树和结果大小成正比，递归空间 O(target/c)。',[
({'candidates':[2,3,6,7],'target':7},[[2,2,3],[7]]),({'candidates':[2],'target':1},[]),({'candidates':[2,3,5],'target':8},[[2,2,2,2],[2,3,3],[3,5]])], 'unordered_nested',['回溯','剪枝'])
add(1532,'generateParenthesis','n','用 n 对圆括号组成字符串，返回全部合法括号串。合法指从左到右任何前缀中右括号数不超过左括号数，且总数相等。每个字符串仅返回一次，结果顺序不限。','字符串数组。','回溯维护已放入的左右括号数。左括号未用完可以放左括号；右括号少于左括号时可以放右括号。','设 Cn 为第 n 个卡特兰数，时间 O(n·Cn)，递归空间 O(n)，结果空间 O(n·Cn)。',[
({'n':1},['()']),({'n':2},['(())','()()']),({'n':3},['((()))','(()())','(())()','()(())','()()()'])], 'unordered_json',['回溯'])
add(1533,'partition','s','将字符串 s 切分成若干非空连续片段，要求每个片段都是回文（正着读与倒着读相同）。返回所有切分方案。一个方案中的片段必须按原字符串顺序排列，拼接后恰好等于 s；不同方案之间的顺序不限。','二维字符串数组，每一行是一种切分方案。','从尚未处理的位置枚举下一段的结束位置，只有该段为回文时才递归。到达末尾就保存完整方案。','最坏时间 O(n²·2^n)，递归空间 O(n)，结果最多 O(n·2^n)。',[
({'s':'aab'},[['a','a','b'],['aa','b']]),({'s':'a'},[['a']]),({'s':'aba'},[['a','b','a'],['aba']])], 'unordered_json',['回溯','回文'])
add(1534,'solveNQueens','n','在 n×n 棋盘上放置 n 个皇后，使任意两个皇后不在同一行、同一列或同一条对角线上。返回所有不同棋盘。每个棋盘是 n 个长度为 n 的字符串，Q 表示皇后，. 表示空格；棋盘的行顺序必须保留，各棋盘的顺序不限。无解时返回空数组。','三维结构：棋盘列表；每个棋盘是字符串数组。','逐行选列，用三个集合记录已占用列和两种对角线（行减列、行加列）。遇到冲突跳过，填满 n 行保存棋盘。','搜索时间 O(n·n!)（含候选检查，不含输出），递归及集合 O(n)，结果每个棋盘占 O(n²)。',[
({'n':1},[['Q']]),({'n':2},[]),({'n':4},[['.Q..','...Q','Q...','..Q.'],['..Q.','Q...','...Q','.Q..']])], 'unordered_json',['回溯'])
add(1535,'searchInsert','nums,target','给定严格递增整数数组 nums 和 target。如果 target 存在，返回其下标；否则返回保持数组升序时应插入的位置。下标从 0 开始，插在末尾时返回数组长度。请使用 O(log n) 时间算法。','一个整数下标。','二分寻找第一个不小于 target 的位置，使用左闭右开区间，答案自然涵盖插在末尾的情况。','时间 O(log n)，空间 O(1)。',[
({'nums':[1,3,5,6],'target':5},2),({'nums':[1,3,5,6],'target':2},1),({'nums':[1],'target':2},1),({'nums':[1,3],'target':0},0)], tags=['二分查找'])
add(1536,'searchRange','nums,target','给定非递减整数数组 nums 和 target，返回 target 第一次与最后一次出现的下标。没有出现时返回 [-1,-1]。允许空数组，要求时间复杂度 O(log n)。','长度为 2 的整数数组 [首次下标, 末次下标]。','分别用二分查找第一个大于等于 target 和第一个严格大于 target 的位置，先检查目标是否存在。','时间 O(log n)，空间 O(1)。',[
({'nums':[5,7,7,8,8,10],'target':8},[3,4]),({'nums':[],'target':0},[-1,-1]),({'nums':[2,2,2],'target':2},[0,2]),({'nums':[1,3],'target':2},[-1,-1])],tags=['二分查找'])
add(1537,'search','nums,target','一个严格递增数组在某个位置旋转后得到 nums，例如 [0,1,2,4,5] 可变成 [4,5,0,1,2]，也允许保持原顺序。元素互不相同。返回 target 在 nums 中的下标，不存在返回 -1。要求 O(log n) 时间。','一个整数下标或 -1。','每次二分至少有一半有序。判断 target 是否在这一有序半区的值域内，再缩小查找范围。','时间 O(log n)，空间 O(1)。',[
({'nums':[4,5,6,7,0,1,2],'target':0},4),({'nums':[4,5,6,7,0,1,2],'target':3},-1),({'nums':[1],'target':1},0),({'nums':[1,2,3],'target':3},2)],tags=['二分查找'])
add(1538,'findMin','nums','给定由严格递增数组旋转得到的非空数组 nums，各元素互不相同。旋转可以将末尾若干元素移到开头，也允许经过一整圈后顺序不变。返回数组最小元素，要求 O(log n) 时间。','最小整数值。','二分比较中间值与右端值。中间值更大说明最小值在其右边，否则最小值位于包含中点的左半区。','时间 O(log n)，空间 O(1)。',[
({'nums':[3,4,5,1,2]},1),({'nums':[1]},1),({'nums':[1,2,3,4]},1),({'nums':[2,1]},1)],tags=['二分查找'])
add(1539,'findMedianSortedArrays','nums1,nums2','给定两个非递减整数数组 nums1、nums2，至少一个数组非空。将全部元素合并排序后，奇数个元素的中位数是中间元素；偶数个元素的中位数是中间两个元素的平均值。返回此中位数，目标时间 O(log(m+n))。','一个数值，允许整数或小数表示相同数值。','在较短数组上二分分割位置，使两个数组左半部分共占一半且左侧最大值不超过右侧最小值。用无穷大处理边界，再按总长度奇偶取值。','时间 O(log(min(m,n)+1))，空间 O(1)。',[
({'nums1':[1,3],'nums2':[2]},2),({'nums1':[1,2],'nums2':[3,4]},2.5),({'nums1':[],'nums2':[0]},0),({'nums1':[-5,-3],'nums2':[-2,-1]},-2.5)], 'float_tokens',['二分查找'])
add(1540,'isValid','s','字符串 s 只包含 ()[]{} 六种字符。判断每个右括号是否与它之前最近的尚未匹配的左括号类型相同，并且全部括号最终都能成对匹配。','布尔值 true 或 false。','左括号入栈；遇到右括号，检查栈顶类型后弹出。中途失配或最终仍有左括号都不合法。','时间 O(n)，空间 O(n)。',[
({'s':'()[]{}'},True),({'s':'(]'},False),({'s':'([{}])'},True),({'s':'('},False)],tags=['栈'])
add(1541,'','', '实现 MinStack 类，支持 push(val) 入栈、pop() 移除栈顶、top() 读取栈顶、getMin() 读取当前栈的最小值。以上操作都应为 O(1)。构造函数无参数；pop、top、getMin 仅在非空时调用，push 和 pop 不返回值。输入用 operations 和 arguments 两个等长数组表示，首个操作必须为 MinStack，arguments[i] 是该操作的位置参数列表。','按调用顺序返回结果数组：构造、push、pop 对应 null，top、getMin 对应整数。','每个栈结点同时保存当前值以及从栈底到该结点的最小值。读取最小值只需看栈顶保存的第二项。','每次操作 O(1)，保存 n 个元素占 O(n) 空间。',[
({'operations':['MinStack','push','push','push','getMin','pop','top','getMin'],'arguments':[[],[-2],[0],[-3],[],[],[],[]]},[None,None,None,None,-3,None,0,-2]),({'operations':['MinStack','push','getMin','top'],'arguments':[[],[5],[],[]]},[None,None,5,5]),({'operations':['MinStack','push','push','pop','getMin'],'arguments':[[],[1],[1],[],[]]},[None,None,None,None,1])],tags=['栈','设计'])
add(1542,'decodeString','s','字符串采用 k[内容] 表示把内容重复 k 次，方括号内还可以嵌套相同编码；普通小写字母保持原样。例如 2[a3[b]] 解码为 abbbabbb。输入保证编码合法，数字只表示重复次数，不表示普通文本。返回完整解码后的字符串。','解码字符串。','遍历字符，维护当前片段和重复次数。左括号时把外层片段和次数压栈，右括号时弹出并将当前片段重复后接到外层。','设解码长度为 L，嵌套深度为 d，字符串拼接实现最坏时间 O(L·(输入长度+d))，空间 O(L+d)。',[
({'s':'3[a]2[bc]'},'aaabcbc'),({'s':'3[a2[c]]'},'accaccacc'),({'s':'abc'},'abc'),({'s':'10[a]'},'aaaaaaaaaa')],tags=['栈','字符串'])
add(1543,'dailyTemperatures','temperatures','temperatures[i] 表示第 i 天的温度。对每一天，求之后还需要等待多少天才第一次遇到严格更高温度；之后没有更高温度则为 0。相同温度不算升温。','与输入等长的整数数组。','用单调递减栈保存尚未找到更暖一天的下标。新温度较高时持续弹栈，天数差就是被弹出位置的答案。','时间 O(n)，空间 O(n)。',[
({'temperatures':[73,74,75,71,69,72,76,73]},[1,1,4,2,1,1,0,0]),({'temperatures':[30]},[0]),({'temperatures':[40,40,39]},[0,0,0]),({'temperatures':[30,40,50]},[1,1,0])],tags=['单调栈'])
add(1544,'largestRectangleArea','heights','柱状图由宽度均为 1、紧邻排列的柱子组成，heights 给出非负高度。选择一段连续柱子，在它们覆盖范围内画一个不超出柱状图的矩形，返回可能的最大矩形面积。','非负整数面积。','单调递增栈保存柱子下标。遇到更矮柱子时，弹出的柱子作为矩形最低高度，左右边界由当前下标和新栈顶确定。末尾补零清空栈。','时间 O(n)，空间 O(n)。',[
({'heights':[2,1,5,6,2,3]},10),({'heights':[0]},0),({'heights':[2,2]},4),({'heights':[1,2,3,4]},6)],tags=['单调栈'])
add(1545,'findKthLargest','nums,k','返回整数数组 nums 按从大到小排列后的第 k 个元素。重复元素分别占据排序位置；这里不是第 k 个不同的数。k 从 1 开始。','一个整数。','维护大小最多为 k 的最小堆。堆满后只保留比堆顶更大的元素，最终堆中是最大的 k 个数，堆顶就是答案。','时间 O(n log(k+1))，空间 O(k)。',[
({'nums':[3,2,1,5,6,4],'k':2},5),({'nums':[3,2,3,1,2,4,5,5,6],'k':4},4),({'nums':[-1],'k':1},-1),({'nums':[2,2,1],'k':2},2)],tags=['堆'])
add(1546,'topKFrequent','nums,k','统计整数数组 nums 中每个不同整数的出现次数，返回出现次数最高的 k 个不同整数。保证第 k 名和未选中元素之间不存在次数相同的歧义，所以答案集合唯一；输出顺序不限。','包含 k 个不同整数的数组。','用计数表汇总次数，再按次数用大小为 k 的堆选取最高频元素。','时间 O(n+u log(k+1))，空间 O(u+k)，u 为不同整数个数。',[
({'nums':[1,1,1,2,2,3],'k':2},[1,2]),({'nums':[1],'k':1},[1]),({'nums':[-1,-1,2,2,2,3],'k':1},[2]),({'nums':[4,4,5,5],'k':2},[4,5])], 'unordered_json',['哈希表','堆'])
add(1547,'','', '实现 MedianFinder 类：构造函数无参数，addNum(num) 向数据流添加一个整数，findMedian() 返回当前所有已添加元素的中位数。奇数个时取排序后中间值，偶数个时取中间两个值的平均数。调用 findMedian 前至少添加一个数。输入由 operations 和 arguments 两个等长数组组成，首个操作必须是 MedianFinder，每项 arguments 是相应操作的位置参数数组。','按操作顺序返回结果数组；构造和 addNum 对应 null，findMedian 对应数值。','较小一半用最大堆（负数模拟），较大一半用最小堆。每次插入后调整两个堆，保证前者大小等于后者或多一。中位数由堆顶取得。','addNum 时间 O(log n)，findMedian 时间 O(1)，空间 O(n)。',[
({'operations':['MedianFinder','addNum','addNum','findMedian','addNum','findMedian'],'arguments':[[],[1],[2],[],[3],[]]},[None,None,None,1.5,None,2]),({'operations':['MedianFinder','addNum','findMedian'],'arguments':[[],[-5],[]]},[None,None,-5]),({'operations':['MedianFinder','addNum','addNum','findMedian','addNum','findMedian'],'arguments':[[],[-1],[-1],[],[5],[]]},[None,None,None,-1,None,-1])],tags=['堆','设计'])
add(1548,'maxProfit','prices','prices[i] 是第 i 天一股股票的价格。你最多进行一次交易：先在某一天买入，再在之后某一天卖出。返回最大利润；如果任何交易都无法获利，可以不交易并返回 0。','非负整数。','扫描时维护此前最低价格，用当前价格减去最低价尝试更新利润，再更新最低价。','时间 O(n)，空间 O(1)。',[
({'prices':[7,1,5,3,6,4]},5),({'prices':[7,6,4,3,1]},0),({'prices':[5]},0),({'prices':[0,10]},10)],tags=['贪心'])
add(1549,'canJump','nums','你从数组 nums 的下标 0 出发，nums[i] 表示在位置 i 最多可以向右跳多少格，每次也可以跳更少的正整数格。判断能否到达最后一个下标。数组只有一个元素时已经到达终点。','布尔值。','从左到右维护已知可达的最远位置；如果当前下标超出最远位置则失败，否则利用当前跳跃能力扩展覆盖范围。','时间 O(n)，空间 O(1)。',[
({'nums':[2,3,1,1,4]},True),({'nums':[3,2,1,0,4]},False),({'nums':[0]},True),({'nums':[0,1]},False)],tags=['贪心'])
add(1550,'jump','nums','从 nums 的下标 0 出发，在位置 i 一次可以向右跳 1 到 nums[i] 格。输入保证最后一个下标可以到达。返回到达终点所需的最少跳跃次数；长度为 1 时返回 0。','非负整数次数。','把同样跳跃次数能到达的位置看作一层，扫描这一层时计算下一层的最远边界。到达当前边界才增加一次跳跃。','时间 O(n)，空间 O(1)。',[
({'nums':[2,3,1,1,4]},2),({'nums':[0]},0),({'nums':[1,1,1,1]},3),({'nums':[4,1,1,1,1]},1)],tags=['贪心'])
add(1551,'partitionLabels','s','把字符串 s 划分成尽可能多的非空连续片段，使每种字母最多只出现在其中一个片段里。返回各片段的长度，顺序与原字符串一致。所有片段连接后必须恰好还原 s。','整数数组。','记录每个字母最后出现的位置。扫描当前片段时扩展其最远结束下标，到达该边界即可切分，得到尽可能早的合法切点。','时间 O(n)，空间 O(字符集大小)。',[
({'s':'ababcbacadefegdehijhklij'},[9,7,8]),({'s':'eccbbbbdec'},[10]),({'s':'abc'},[1,1,1]),({'s':'a'},[1])],tags=['贪心'])
add(1552,'climbStairs','n','到楼顶共有 n 级台阶，每次只能上 1 级或 2 级。返回恰好到达楼顶的不同走法数量，步长顺序不同视为不同走法。','正整数。','到第 i 级的最后一步来自 i-1 或 i-2，故方案数为前两项之和。用两个变量滚动保存状态。','时间 O(n)，空间 O(1)。',[
({'n':1},1),({'n':3},3),({'n':5},8),({'n':45},1836311903)],tags=['动态规划'])
add(1553,'generate','numRows','返回杨辉三角的前 numRows 行。第一行只有数字 1，每行左右两端为 1，其余位置等于上一行左上与右上两个数字之和。','二维整数数组，按从第一行到最后一行的顺序。','逐行构造，先全部填 1，再由上一行计算本行中间元素。','时间与结果大小均为 O(numRows²)，辅助空间除结果外 O(numRows)。',[
({'numRows':1},[[1]]),({'numRows':3},[[1],[1,1],[1,2,1]]),({'numRows':5},[[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]])],tags=['动态规划'])
add(1554,'rob','nums','一排房屋的现金数量为 nums。你可以选择若干房屋获取现金，但不能同时选择相邻房屋。返回能够取得的最大金额，允许一个也不选。','非负整数。','处理一间房时比较跳过它的最优值与拿它加上前两间的最优值，滚动维护这两个状态。','时间 O(n)，空间 O(1)。',[
({'nums':[1,2,3,1]},4),({'nums':[2,7,9,3,1]},12),({'nums':[0]},0),({'nums':[2,1,1,2]},4)],tags=['动态规划'])
add(1555,'numSquares','n','给定正整数 n，使用若干个正完全平方数（1、4、9、16 等）相加得到 n，每种平方数可以重复使用。返回所需平方数的最少个数。','正整数。','令 dp[x] 为凑出 x 的最少个数。枚举不超过 x 的平方数 q，用 dp[x-q]+1 更新 dp[x]。','时间 O(n√n)，空间 O(n)。',[
({'n':12},3),({'n':13},2),({'n':1},1),({'n':16},1)],tags=['动态规划'])
add(1556,'coinChange','coins,amount','有面额为 coins 的硬币，每种可使用任意多枚。返回凑出总金额 amount 的最少硬币数。无法凑出时返回 -1，总金额为 0 时返回 0。','整数，无法达成时为 -1。','dp[x] 表示金额 x 所需最少硬币数，初始仅 dp[0]=0。依次枚举金额，再尝试最后使用每种硬币。','时间 O(amount·硬币种数)，空间 O(amount)。',[
({'coins':[1,2,5],'amount':11},3),({'coins':[2],'amount':3},-1),({'coins':[1],'amount':0},0),({'coins':[2,5,10,1],'amount':27},4)],tags=['动态规划'])
add(1557,'wordBreak','s,wordDict','判断能否将字符串 s 分割成一个或多个词典 wordDict 中的单词。词典中的同一单词可使用多次，片段必须连续且完全覆盖原字符串。','布尔值。','dp[i] 表示前 i 个字符是否可拆分。检查最后一段是否在词典中，以及前一段前缀是否可达；只需检查不超过最长词长的片段。','设词典最长词长 L，按 Python 切片计时间 O(n·L²+词典字符总数)，空间 O(n+词典大小)。',[
({'s':'leetcode','wordDict':['leet','code']},True),({'s':'applepenapple','wordDict':['apple','pen']},True),({'s':'catsandog','wordDict':['cats','dog','sand','and','cat']},False),({'s':'a','wordDict':['b']},False)],tags=['动态规划'])
add(1558,'lengthOfLIS','nums','返回 nums 中最长严格递增子序列的长度。子序列可以删除任意位置元素，但保留下标的相对顺序；相等元素不能连续增加子序列长度。请尝试 O(n log n) 的算法。','正整数长度。','tails[i] 保存长度为 i+1 的递增子序列能取得的最小末尾值。对每个数二分第一个不小于它的位置，替换或追加。','时间 O(n log n)，空间 O(n)。',[
({'nums':[10,9,2,5,3,7,101,18]},4),({'nums':[7,7,7]},1),({'nums':[4]},1),({'nums':[0,1,0,3,2,3]},4)],tags=['动态规划','二分查找'])
add(1559,'maxProduct','nums','在非空整数数组 nums 中选择一个非空连续子数组，返回其元素乘积的最大值。元素可能为负数或零，不能选择空数组。','一个整数乘积。','负数会交换最大与最小乘积，因此同时维护以当前位置结尾的最大乘积与最小乘积，并在每步更新全局答案。','时间 O(n)，空间 O(1)。',[
({'nums':[2,3,-2,4]},6),({'nums':[-2,0,-1]},0),({'nums':[-2]},-2),({'nums':[-2,3,-4]},24)],tags=['动态规划'])
add(1560,'canPartition','nums','给定正整数数组 nums，判断能否把所有元素分成两个子集，使两边元素总和相等。每个下标的元素必须恰好分到一边，元素值相同也视为不同元素。','布尔值。','总和为奇数直接失败，否则是能否选出总和一半的 0/1 背包。用整数的第 x 位表示和 x 可达，移位后取或实现一次选择。','设目标和为 T，位集占 O(T) 位；时间 O(n·T/w)，w 为大整数运算字宽。',[
({'nums':[1,5,11,5]},True),({'nums':[1,2,3,5]},False),({'nums':[1]},False),({'nums':[2,2]},True)],tags=['动态规划','背包'])
add(1561,'longestValidParentheses','s','字符串 s 只由圆括号组成，可以为空。返回其中最长合法括号连续子串的长度。合法括号串可以完整配对且没有交叉；没有非空合法子串则返回 0。','非负整数长度。','栈底保存最近的无效边界，其余保存尚未匹配的左括号下标。右括号弹栈，若栈空则设新边界，否则当前位置到栈顶的距离是当前合法长度。','时间 O(n)，空间 O(n)。',[
({'s':'(()'},2),({'s':')()())'},4),({'s':''},0),({'s':'()(())'},6)],tags=['栈','动态规划'])
add(1562,'uniquePaths','m,n','机器人位于 m 行 n 列网格的左上角，每步只能向右一格或向下一格。返回到达右下角的不同路径总数。网格没有障碍，只有一格时存在一条不移动的路径。','正整数路径数。','每格路径数是上方与左方路径数之和。第一行和第一列均为 1，用一维数组逐行更新。','时间 O(mn)，空间 O(n)。',[
({'m':3,'n':7},28),({'m':1,'n':1},1),({'m':3,'n':2},3),({'m':1,'n':5},1)],tags=['动态规划'])
add(1563,'minPathSum','grid','给定非空矩形网格 grid，元素都是非负整数。从左上角走到右下角，每步只能向右或向下一格。路径代价为经过的所有格子数值之和（包含起点和终点），返回最小代价。','非负整数。','逐行维护到达各列的最小路径和。本格最优代价等于本格值加上方、左方代价的较小值；用无穷大屏蔽网格外位置。','时间 O(mn)，空间 O(n)。',[
({'grid':[[1,3,1],[1,5,1],[4,2,1]]},7),({'grid':[[0]]},0),({'grid':[[1,2,3]]},6),({'grid':[[2],[3],[1]]},6)],tags=['动态规划'])
add(1564,'longestPalindrome','s','给定非空字符串 s，返回它的最长回文连续子串。回文指正序和倒序相同。本练习明确规定：如果有多个同样长度的最长回文，返回起始下标最小（最靠左）的那个。因此 babad 的答案是 bab。大小写字符按原样区分。','一个字符串，按最长且起点最靠左的规则唯一确定。','枚举每个字符中心以及相邻字符间中心，向两侧扩展。长度更长时更新；等长时保留起点更小的区间。','时间 O(n²)，空间 O(1)（不含返回字符串）。',[
({'s':'babad'},'bab'),({'s':'cbbd'},'bb'),({'s':'a'},'a'),({'s':'ac'},'a'),({'s':'aaaa'},'aaaa')],tags=['字符串','回文'])
add(1565,'longestCommonSubsequence','text1,text2','返回 text1 和 text2 的最长公共子序列长度。子序列允许删除任意位置字符，但必须保留相对顺序；不要求连续。没有公共字符则长度为 0。','非负整数。','dp[i][j] 表示两个前缀的最长公共子序列。末字符相同则取左上角加一，否则取上方和左方较大值。用滚动数组和一个变量保存左上角。','时间 O(mn)，空间 O(n)，m、n 分别为两个字符串长度。',[
({'text1':'abcde','text2':'ace'},3),({'text1':'abc','text2':'def'},0),({'text1':'abc','text2':'abc'},3),({'text1':'aaaa','text2':'aa'},2)],tags=['动态规划'])
add(1566,'minDistance','word1,word2','把字符串 word1 变为 word2，可以每次插入一个字符、删除一个字符或替换一个字符，每次操作代价为 1。返回最少操作次数，允许任一字符串为空。','非负整数。','dp[i][j] 是两个前缀的编辑距离。末字符相同继承左上角，否则从删除、插入、替换三种前驱取最小值加一。空前缀距离等于另一前缀长度。','时间 O(mn)，空间 O(n)。',[
({'word1':'horse','word2':'ros'},3),({'word1':'','word2':'abc'},3),({'word1':'abc','word2':''},3),({'word1':'same','word2':'same'},0),({'word1':'intention','word2':'execution'},5)],tags=['动态规划'])
add(1567,'singleNumber','nums','非空整数数组 nums 中恰有一个整数只出现一次，其他整数均出现两次。返回只出现一次的整数。要求线性时间且只使用常量额外空间。','一个整数。','利用异或满足 x^x=0、x^0=x 且可交换结合，依次异或全部元素，成对的元素抵消。','时间 O(n)，空间 O(1)。',[
({'nums':[2,2,1]},1),({'nums':[4,1,2,1,2]},4),({'nums':[-1]},-1),({'nums':[-3,0,0]},-3)],tags=['位运算'])
add(1568,'majorityElement','nums','给定非空整数数组 nums，保证存在一个元素出现次数严格大于数组长度的一半。返回这个多数元素。请尝试线性时间和常量额外空间。','一个整数。','Boyer–Moore 投票：计数为零时选择新候选；相同元素加一，不同元素减一。不同元素相互抵消后多数元素仍会留下。','时间 O(n)，空间 O(1)。',[
({'nums':[3,2,3]},3),({'nums':[2,2,1,1,1,2,2]},2),({'nums':[-1]},-1),({'nums':[0,0,1]},0)],tags=['贪心'])
add(1569,'sortColors','nums','数组 nums 的元素只有 0、1、2，分别表示三种颜色。请原地修改 nums，使所有 0 在前、1 在中、2 在后。不要调用内置排序。方法无需返回值，判题器读取调用结束后的 nums；要求 O(n) 时间、O(1) 额外空间。','修改后的 nums 数组，由判题器自动输出。','维护左侧已确认的 0 区、右侧已确认的 2 区和中间待处理区。遇 0 换到左侧，遇 2 换到右侧且继续检查换来的元素，遇 1 前进。','时间 O(n)，空间 O(1)。',[
({'nums':[2,0,2,1,1,0]},[0,0,1,1,2,2]),({'nums':[0]},[0]),({'nums':[2,2,2]},[2,2,2]),({'nums':[2,1,0]},[0,1,2])],tags=['双指针'])
add(1570,'nextPermutation','nums','原地把整数数组 nums 改为按字典序紧接着的下一个不同排列。如果当前已是最大的排列，则改为最小的升序排列。允许重复元素。方法无需返回值，判题器读取修改后的 nums。要求只用 O(1) 额外空间。','修改后的 nums 数组，由判题器自动输出。','从右找第一个上升位置作枢轴，和右侧最小的更大元素交换，再反转非递增后缀。没有枢轴说明当前最大，直接反转整个数组。','时间 O(n)，空间 O(1)。',[
({'nums':[1,2,3]},[1,3,2]),({'nums':[3,2,1]},[1,2,3]),({'nums':[1,1,5]},[1,5,1]),({'nums':[1]},[1]),({'nums':[1,3,2]},[2,1,3])],tags=['双指针'])
add(1571,'findDuplicate','nums','数组 nums 长度为 n+1，每个元素都在 1 到 n 之间。只有一种数出现两次或更多次，其余数最多出现一次（允许某些数未出现）。返回重复的数。不得修改输入数组，要求 O(1) 额外空间；请尝试 O(n) 时间算法。','重复的整数。','把下标到 nums[下标] 看作链表指针。由下标 0 出发一定进入环，重复数是环入口。先用快慢指针相遇，再将一根指针放回起点，同步移动到入口。','时间 O(n)，空间 O(1)。',[
({'nums':[1,3,4,2,2]},2),({'nums':[3,1,3,4,2]},3),({'nums':[1,1]},1),({'nums':[2,2,2,2,2]},2)],tags=['快慢指针'])
slugs = '''subsets letter-combinations-of-a-phone-number combination-sum generate-parentheses palindrome-partitioning n-queens search-insert-position find-first-and-last-position-of-element-in-sorted-array search-in-rotated-sorted-array find-minimum-in-rotated-sorted-array median-of-two-sorted-arrays valid-parentheses min-stack decode-string daily-temperatures largest-rectangle-in-histogram kth-largest-element-in-an-array top-k-frequent-elements find-median-from-data-stream best-time-to-buy-and-sell-stock jump-game jump-game-ii partition-labels climbing-stairs pascals-triangle house-robber perfect-squares coin-change word-break longest-increasing-subsequence maximum-product-subarray partition-equal-subset-sum longest-valid-parentheses unique-paths minimum-path-sum longest-palindromic-substring longest-common-subsequence edit-distance single-number majority-element sort-colors next-permutation find-the-duplicate-number'''.split()
assert len(slugs) == 43
inventory = {p['id']:p for p in json.loads((ROOT/'database/sources/codeky.json').read_text())['inventory']}
for row in rows:
    row['sourceUrl'] = 'https://leetcode.com/problems/' + slugs[row['id']-1529] + '/'
    original = inventory[row['id']]
    row['title'] = original['title']
    row['difficulty'] = original['difficulty']
    row['constraints'] = re.sub('</?mark>', '', original['data_range'])
    if row['id'] == 1530:
        row['constraints'] = row['constraints'].replace('1 <= digits.length', '0 <= digits.length')
    if row['id'] == 1542:
        row['constraints'] += '\n- 本练习限制解码后的字符串长度不超过 100000。'
    if row['id'] == 1571:
        row['constraints'] = '- 1 <= n <= 10^5；nums.length == n+1\n- 1 <= nums[i] <= n\n- 恰有一种数出现至少两次，其他数最多出现一次。'
assert len(rows) == 43
(ROOT/'database/hot-data.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
