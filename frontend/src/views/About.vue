<template>
  <div class="about-container">
    <el-card class="about-card">
      <template #header>
        <div class="header-content">
          <div class="header-logo">
            <el-icon :size="48" color="#409EFF"><Lock /></el-icon>
          </div>
          <div class="header-text">
            <h1>基于 Web 的端对端加密云存储系统</h1>
            <p class="subtitle">E2EE Secure Cloud Storage System</p>
          </div>
        </div>
      </template>

      <div class="content">
        <section class="intro-section">
          <h3><el-icon><InfoFilled /></el-icon> 系统概述</h3>
          <p>
            本系统是一个高安全性的分布式云存储平台，核心采用<strong>端对端加密 (End-to-End Encryption, E2EE)</strong> 架构。
            与传统网盘不同，本系统确数据的加密过程完全在客户端（浏览器）进行，服务器仅负责存储密文数据。
            这一架构从根本上杜绝了服务商、管理员或任何第三方非法访问用户数据的可能性，真正实现了“数据隐私权归用户所有”。
          </p>
        </section>

        <section class="architecture-section">
          <h3><el-icon><Connection /></el-icon> 核心安全架构</h3>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <template #header>
                  <div class="feature-header">
                    <el-icon color="#67C23A"><Key /></el-icon>
                    <span>混合加密机制</span>
                  </div>
                </template>
                <div class="feature-desc">
                  结合 <strong>AES-GCM-256</strong> 对称加密的高效性与 <strong>RSA-OAEP-2048</strong> 非对称加密的灵活性，实现文件内容的秒级加密与安全分发。
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <template #header>
                  <div class="feature-header">
                    <el-icon color="#E6A23C"><Lock /></el-icon>
                    <span>零知识证明</span>
                  </div>
                </template>
                <div class="feature-desc">
                  服务器不存储用户明文密码，仅存储 PBKDF2 哈希值。私钥由用户密码在本地派生解密，服务器永远无法获取用户私钥明文。
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <template #header>
                  <div class="feature-header">
                    <el-icon color="#F56C6C"><Share /></el-icon>
                    <span>安全密钥交换</span>
                  </div>
                </template>
                <div class="feature-desc">
                  文件分享基于接收者的公钥进行密钥重加密（Proxy Re-encryption 思想），确保只有指定的接收者能解密文件，撤销权限立即生效。
                </div>
              </el-card>
            </el-col>
          </el-row>
        </section>

        <section class="process-section">
            <h3><el-icon><Operation /></el-icon> 数据流转全景图</h3>
            <div class="process-steps">
                <el-steps :active="5" align-center finish-status="success">
                    <el-step title="密钥生成" description="浏览器生成 RSA 密钥对，私钥经 AES 加密后存储"></el-step>
                    <el-step title="文件加密" description="随机生成 AES 密钥加密文件，再用公钥加密 AES 密钥"></el-step>
                    <el-step title="加密传输" description="通过 HTTPS 通道上传密文数据与加密密钥"></el-step>
                    <el-step title="云端存储" description="服务器持久化存储密文，无法解析内容"></el-step>
                    <el-step title="解密还原" description="下载时在浏览器端用私钥解密密钥，再还原文件"></el-step>
                </el-steps>
            </div>
        </section>

        <section class="tech-section">
          <h3><el-icon><Cpu /></el-icon> 技术栈与标准</h3>
          <div class="tech-grid">
            <div class="tech-item">
                <span class="label">前端框架</span>
                <el-tag effect="dark">Vue 3 + Composition API</el-tag>
            </div>
            <div class="tech-item">
                <span class="label">UI 组件库</span>
                <el-tag effect="plain" type="primary">Element Plus</el-tag>
            </div>
            <div class="tech-item">
                <span class="label">加密标准</span>
                <el-tag type="warning">Web Crypto API (W3C Standard)</el-tag>
            </div>
            <div class="tech-item">
                <span class="label">后端服务</span>
                <el-tag type="success">Python Flask RESTful API</el-tag>
            </div>
            <div class="tech-item">
                <span class="label">数据持久化</span>
                <el-tag type="info">SQLite / SQLAlchemy</el-tag>
            </div>
          </div>
        </section>
      </div>
    </el-card>

    <footer class="footer">
        <p>&copy; 2026 基于 Web 的端对端加密云存储系统 | 苏昊毕业设计作品</p>
    </footer>
  </div>
</template>

<script setup>
import { Lock, Key, Share, InfoFilled, Connection, Operation, Cpu } from '@element-plus/icons-vue'
</script>

<style scoped>
.about-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}
.about-card {
    border-radius: 8px;
    overflow: hidden;
}
.header-content {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 10px 0;
}
.header-text h1 {
    margin: 0;
    font-size: 24px;
    color: #303133;
}
.subtitle {
    margin: 5px 0 0;
    color: #909399;
    font-size: 14px;
    font-family: 'Consolas', monospace;
}

.content {
  padding: 10px;
}

section {
    margin-bottom: 40px;
}

h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  color: #303133;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.intro-section p {
    line-height: 1.8;
    color: #606266;
    text-align: justify;
}

.feature-card {
    height: 100%;
    border: none;
    background: #fcfcfc;
}
.feature-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: bold;
    color: #303133;
}
.feature-desc {
    font-size: 13px;
    color: #606266;
    line-height: 1.6;
}

.process-steps {
    padding: 20px 0;
    background: #f9f9f9;
    border-radius: 8px;
}

.tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}
.tech-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.tech-item .label {
    font-size: 12px;
    color: #909399;
}

.footer {
    text-align: center;
    margin-top: 40px;
    color: #c0c4cc;
    font-size: 12px;
}
</style>
