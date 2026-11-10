import { test, expect, type Page } from '@playwright/test'
async function login(page: Page) {
  await page.goto('/login')
  await page.locator('html[data-codeace-ready="true"]').waitFor()
  await page.getByLabel('用户名', { exact: true }).fill(process.env.ADMIN_USERNAME || 'admin')
  await page.getByLabel('密码', { exact: true }).fill(process.env.ADMIN_PASSWORD!)
  await page.getByRole('button', { name: '进入学习空间' }).click()
  await expect(page).toHaveURL(/\/$/)
  await expect(page.getByRole('heading', { name: /把每一次练习/ })).toBeVisible()
}
async function editor(page: Page, code: string) {
  const content = page.getByRole('textbox', { name: '代码编辑器' })
  await expect(content).toBeVisible()
  await content.click()
  await page.keyboard.press('ControlOrMeta+A')
  await page.keyboard.insertText(code)
}
test('single user practice, drafts, notes, real submissions and records', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  await login(page)
  await page.getByLabel('搜索题目', { exact: true }).fill('两整数求和')
  await page.getByRole('link', { name: '两整数求和', exact: true }).click()
  await expect(page.getByRole('heading', { name: '两整数求和', exact: true })).toBeVisible()
  await page.getByLabel('输入模式', { exact: true }).selectOption('acm')
  await editor(page, 'a,b=map(int,input().split())\nprint(a+b)')
  await page.getByRole('button', { name: '运行', exact: true }).click()
  await expect(page.locator('.judge-result .status-badge')).toHaveText('AC', { timeout: 45000 })
  await page.getByRole('button', { name: '提交代码', exact: true }).click()
  await expect(page.locator('.judge-result .status-badge')).toHaveText('AC', { timeout: 45000 })
  const removeFavorite = page.getByRole('button', { name: '取消收藏', exact: true })
  if (await removeFavorite.isVisible()) await removeFavorite.click()
  await page.getByRole('button', { name: '收藏题目', exact: true }).click()
  await page.getByRole('tab', { name: '我的笔记', exact: true }).click()
  await page.getByLabel('个人笔记').fill('## 我的思路\n先读入两个整数，再相加。')
  await page.getByRole('button', { name: '保存笔记', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('笔记已保存')
  await page.reload()
  await page.locator('html[data-codeace-ready="true"]').waitFor()
  await expect(page.getByRole('textbox', { name: '代码编辑器' })).toContainText('print(a+b)')
  await page.getByRole('tab', { name: '我的笔记', exact: true }).click()
  await expect(page.getByLabel('个人笔记')).toHaveValue(/我的思路/)
  await page.getByRole('tab', { name: '提交记录', exact: true }).click()
  await expect(page.locator('.record-row').first()).toContainText('AC')
  await expect(page.locator('.record-row').first()).toContainText('ACM 模式')
  await expect(page.locator('.record-row').first()).toContainText('MB')
  await expect(page.locator('.record-row .record-case-count').first()).toHaveText('3 / 3 个用例')
  await page.locator('.record-row').first().click()
  await expect(page.getByRole('heading', { name: '提交代码', exact: true })).toBeVisible()
  await expect(page.locator('.code-block').last()).toContainText('print(a+b)')
  await page.goto('/submissions')
  await expect(page.locator('.submission-case-count').first()).toHaveText('3 / 3')
  await page.goto('/progress')
  await expect(page.getByRole('heading', { name: '看见每一步成长' })).toBeVisible()
  expect(errors).toEqual([])
})
test('function mode, Python-only restrictions and saved filter context', async ({ page }) => {
  await login(page)
  await page.getByRole('button', { name: /LeetCode Hot 100/ }).click()
  await page.getByLabel('搜索题目', { exact: true }).fill('两数之和')
  await page.getByRole('link', { name: '两数之和', exact: true }).click()
  await expect(page.locator('.sample-explanation').first()).toContainText('nums[1] + nums[2] == 6')
  await expect(page.getByLabel('代码语言')).toHaveValue('python3')
  await expect(page.getByLabel('代码语言').locator('option')).toHaveCount(1)
  await page.getByLabel('输入模式').selectOption('function')
  await editor(
    page,
    'class Solution:\n def twoSum(self,nums,target):\n  seen={}\n  for i,n in enumerate(nums):\n   if target-n in seen:return [seen[target-n],i]\n   seen[n]=i',
  )
  await page.getByRole('button', { name: '运行', exact: true }).click()
  await expect(page.locator('.judge-result .status-badge')).toHaveText('AC', { timeout: 45000 })
  await page.getByRole('tab', { name: '自定义输入', exact: true }).click()
  await page.getByLabel('自定义测试输入').fill('nums = [1,2,3], target = 5')
  await page.getByRole('button', { name: '运行', exact: true }).click()
  await expect(page.locator('.judge-result .status-badge')).toHaveText('FINISHED', {
    timeout: 45000,
  })
  await expect(page.locator('.case-result')).toContainText('[1, 2]')
  await page.getByRole('link', { name: '返回题库', exact: true }).click()
  await expect(page.getByLabel('搜索题目', { exact: true })).toHaveValue('两数之和')
})
test('admin import validation, editing, publish and source coverage', async ({ page }) => {
  await login(page)
  await page.goto('/admin')
  await page.locator('html[data-codeace-ready="true"]').waitFor()
  await page.getByRole('button', { name: 'API / 批量导入', exact: true }).click()
  const title = '浏览器导入 ' + Date.now(),
    problem = {
      source: 'e2e',
      sourceId: title,
      title,
      category: '通用算法',
      difficulty: '简单',
      description: '输入一个整数，输出它本身。',
      published: true,
      modes: {
        acm: { templates: { python3: 'print(input())' }, cases: [{ input: '8', expected: '8' }] },
      },
    }
  await page.getByLabel('导入 JSON').fill(JSON.stringify({ problems: [problem] }))
  await page.getByRole('button', { name: '检查格式', exact: true }).click()
  await expect(page.getByLabel('导入结果')).toContainText('"created": 1')
  await page.getByRole('checkbox', { name: '仅预检查，不写入数据库' }).uncheck()
  await page.getByRole('button', { name: '执行导入', exact: true }).click()
  await expect(page.getByLabel('导入结果')).toContainText('"dryRun": false')
  await page.getByRole('button', { name: '题目管理', exact: true }).click()
  await page.getByLabel('管理题目搜索').fill(title)
  await page.getByRole('link', { name: title, exact: true }).click()
  await page.getByRole('button', { name: '题面与题解', exact: true }).click()
  await page.getByLabel('题解', { exact: true }).fill('这是我的个人题解。')
  await page.getByRole('button', { name: '保存题目', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('题目已保存')
  await page.goto('/admin')
  await page.locator('html[data-codeace-ready="true"]').waitFor()
  await page.getByRole('button', { name: '来源同步报告', exact: true }).click()
  await expect(page.getByText(/目标目录 168 道/)).toBeVisible()
  await expect(page.getByText(/源站在线采集已停用/)).toBeVisible()
  await expect(page.getByText(/不会发起 CodeKy 请求/)).toBeVisible()
})
test('mobile layout and unauthorized access', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/admin')
  await page.locator('html[data-codeace-ready="true"]').waitFor()
  await expect(page).toHaveURL(/\/login/)
  await login(page)
  await expect(page.locator('.mobile-nav')).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  await page.getByLabel('搜索题目', { exact: true }).fill('Log-Softmax')
  await page.getByRole('link', { name: 'Log-Softmax', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Log-Softmax', exact: true })).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
})
