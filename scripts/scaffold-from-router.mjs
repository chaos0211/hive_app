import fs from 'node:fs'
import path from 'node:path'

const routerFile = path.resolve('src/router/index.ts')
const content = fs.readFileSync(routerFile, 'utf-8')

// 匹配 import('@/xxx.vue') 和 "from '@/xxx.vue'"
const regex = /import\((['"])(@\/.+?\.vue)\1\)|from\s+(['"])(@\/.+?\.vue)\3/g
const files = new Set()
let m
while ((m = regex.exec(content))) {
  const p = m[2] || m[4]
  if (p) files.add(p.replace(/^@\//, 'src/'))
}

const tpl = (title) => `
<template>
  <div class="p-4">
    <h1 class="text-xl font-semibold">${title}</h1>
    <p class="text-gray-500">（占位页面，待实现）</p>
  </div>
</template>
<script setup lang="ts"></script>
<style scoped></style>
`

let created = 0
for (const f of files) {
  const abs = path.resolve(f)
  if (!fs.existsSync(abs)) {
    fs.mkdirSync(path.dirname(abs), { recursive: true })
    fs.writeFileSync(abs, tpl(path.basename(f, '.vue')))
    console.log('created:', f)
    created++
  } else {
    console.log('exists :', f)
  }
}
console.log('Done. created', created, 'file(s).')