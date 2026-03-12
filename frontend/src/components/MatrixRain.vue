<template>
  <canvas ref="canvas" class="matrix-rain"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvas = ref(null)
let ctx = null
let animationId = null

// 字符集：日文片假名 + 拉丁字母 + 数字
const chars = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
const charArray = chars.split('')

const fontSize = 16
let drops = []

const initMatrix = () => {
  if (!canvas.value) return
  
  canvas.value.width = window.innerWidth
  canvas.value.height = window.innerHeight
  ctx = canvas.value.getContext('2d')
  
  const columns = canvas.value.width / fontSize
  drops = []
  
  for (let i = 0; i < columns; i++) {
    drops[i] = 1
  }
}

const draw = () => {
  // 半透明黑色背景，形成拖尾效果
  ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
  ctx.fillRect(0, 0, canvas.value.width, canvas.value.height)
  
  ctx.fillStyle = '#0F0' // 经典的黑客绿
  ctx.font = fontSize + 'px monospace'
  
  for (let i = 0; i < drops.length; i++) {
    const text = charArray[Math.floor(Math.random() * charArray.length)]
    
    // 随机颜色变化，增加神秘感
    if (Math.random() > 0.98) {
        ctx.fillStyle = '#FFF' // 偶尔闪烁白色
    } else {
        ctx.fillStyle = '#0F0'
    }

    ctx.fillText(text, i * fontSize, drops[i] * fontSize)
    
    // 随机重置
    if (drops[i] * fontSize > canvas.value.height && Math.random() > 0.975) {
      drops[i] = 0
    }
    
    drops[i]++
  }
  
  animationId = requestAnimationFrame(draw)
}

const handleResize = () => {
  initMatrix()
}

onMounted(() => {
  initMatrix()
  draw()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.matrix-rain {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  background-color: black;
}
</style>
