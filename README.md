# 🔒 基于 Web 的端对端加密云存储系统

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-green)](https://flask.palletsprojects.com/)
[![Vue](https://img.shields.io/badge/Vue.js-3.x-4FC08D)](https://vuejs.org/)
[![Element Plus](https://img.shields.io/badge/Element_Plus-2.x-409EFF)](https://element-plus.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

这是一个基于 **Python Flask** (后端) 和 **Vue 3 + Element Plus** (前端) 构建的安全云存储系统。该系统采用了**端对端加密 (E2EE)** 技术，确保用户数据在上传到服务器之前已经在本地完成加密，服务器无法获取用户的原始文件内容，实现了真正的隐私保护。

## ✨ 功能特性

*   **🛡️ 端对端加密**: 
    *   文件在浏览器端使用 **AES-256-GCM** 算法进行加密。
    *   AES 密钥由用户的 **RSA-2048** 公钥加密保护。
    *   所有加密过程均在客户端完成，明文文件从未离开用户设备。
*   **🚫 零知识隐私**: 
    *   服务器仅存储加密后的文件块和加密后的密钥。
    *   管理员无法查看或解密用户的文件内容。
*   **🔐 安全身份验证**: 
    *   使用密码哈希进行身份验证。
    *   私钥在客户端使用密码派生的密钥解密，不在网络上传输明文私钥。
*   **💻 现代化界面**: 
    *   基于 Vue 3 和 Element Plus 构建的响应式用户界面。
    *   提供文件上传、下载、预览（支持部分格式）、分享等功能。
    *   直观的仪表盘展示存储使用情况。
*   **📂 文件管理**: 
    *   支持文件夹管理。
    *   支持断点续传（部分实现）。
    *   回收站功能。

## 🛠️ 技术栈

### 后端 (Backend)
*   **语言**: Python 3.8+
*   **框架**: Flask
*   **数据库**: MySQL (推荐) 或 SQLite (开发环境)
*   **ORM**: SQLAlchemy
*   **其他**: Flask-Login (用户认证), Flask-CORS (跨域支持)

### 前端 (Frontend)
*   **框架**: Vue 3 (Composition API)
*   **构建工具**: Vite
*   **UI 组件库**: Element Plus
*   **HTTP 客户端**: Axios
*   **加密库**: Web Crypto API (浏览器原生)
*   **路由**: Vue Router

## 🚀 快速开始

### 1. 环境准备
确保您的系统已安装以下软件：
*   [Python 3.8+](https://www.python.org/downloads/)
*   [Node.js 16+](https://nodejs.org/) (推荐使用 LTS 版本)
*   [MySQL 5.7+](https://dev.mysql.com/downloads/mysql/) (可选，也可使用 SQLite)

### 2. 后端设置

1.  进入项目根目录：
    ```bash
    cd "c:\Users\liuji\Desktop\fff"
    ```

2.  创建并激活虚拟环境 (可选但推荐)：
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

4.  配置数据库：
    打开 `app.py`，找到数据库配置部分：
    ```python
    # 使用 MySQL (推荐)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/cloud_storage'
    
    # 或者使用 SQLite (无需安装 MySQL)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
    ```
    *如果使用 MySQL，请确保先创建数据库 `cloud_storage`。*

5.  初始化数据库：
    ```bash
    python migrate_db.py
    # 或者如果代码中有 db.create_all()，直接运行 app.py 即可
    ```

6.  启动后端服务：
    ```bash
    python app.py
    ```
    服务将默认运行在 `http://127.0.0.1:5000`。

### 3. 前端设置

1.  打开新的终端窗口，进入 `frontend` 目录：
    ```bash
    cd frontend
    ```

2.  安装依赖：
    ```bash
    npm install
    ```

3.  启动开发服务器：
    ```bash
    npm run dev
    ```
    服务将默认运行在 `http://localhost:5173`。

### 4. 访问系统
打开浏览器访问前端地址：[http://localhost:5173](http://localhost:5173)

## 📁 项目结构

```
主目录/
├── app.py              # 后端 Flask 主程序
├── requirements.txt    # 后端依赖列表
├── instance/           # 存放 SQLite 数据库 (如果使用)
├── uploads/            # 存放用户上传的加密文件
├── frontend/           # 前端 Vue 项目目录
│   ├── src/
│   │   ├── components/ # Vue 组件
│   │   ├── views/      # 页面视图 (Login, Dashboard 等)
│   │   ├── utils/      # 工具函数 (crypto.js 加密核心)
│   │   ├── router/     # 路由配置
│   │   ├── App.vue     # 根组件
│   │   └── main.js     # 入口文件
│   ├── package.json    # 前端依赖配置
│   └── vite.config.js  # Vite 配置文件
└── README.md           # 项目说明文档
```

## 🔒 核心加密流程详解

1.  **注册**:
    *   客户端生成 RSA-2048 密钥对。
    *   公钥发送给服务器存储。
    *   私钥使用用户密码派生的 AES 密钥加密后，发送给服务器存储。
2.  **登录**:
    *   用户输入密码，客户端从服务器下载加密的私钥。
    *   使用密码派生的密钥解密出 RSA 私钥，保存在内存中（页面刷新即失效）。
3.  **文件上传**:
    *   客户端生成随机 AES-256 密钥。
    *   使用 AES 密钥加密文件内容。
    *   使用 RSA 公钥加密 AES 密钥。
    *   将加密后的文件和加密后的 AES 密钥上传至服务器。
4.  **文件下载**:
    *   下载加密的文件和加密的 AES 密钥。
    *   使用内存中的 RSA 私钥解密 AES 密钥。
    *   使用 AES 密钥解密文件内容。
    *   在浏览器中合成文件供用户保存。

## ⚠️ 注意事项

*   **请勿丢失密码**: 由于采用了端对端加密，服务器无法重置您的密码。如果忘记密码，您将无法解密您的私钥，从而永久丢失所有文件。
*   **HTTPS**: 在生产环境中部署时，**必须**使用 HTTPS，否则 Web Crypto API 可能无法在某些浏览器中正常工作。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进本项目！

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。
