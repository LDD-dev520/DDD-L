# 智能问答助手 Web 版

这是一个基于Vue 3开发的智能问答系统前端，支持与后端API连接进行智能问答。
智能问答助手Web版是一个基于Vue 3开发的现代化聊天应用，提供了简洁美观的用户界面，支持与AI助手进行对话交流。该应用
采用前后端分离架构，前端使用Vue 3框架实现，后端预留了API对接接口，可连接Ollama或其他AI服务。

## 功能特点

- **简洁用户界面**：提供直观的聊天交互界面，包括用户/AI消息区分、思考状态动画等
- **历史记录功能**：自动保存聊天历史，支持查看和再次提问
- **响应式设计**：适配不同屏幕尺寸，提供良好的移动端体验
- **本地存储**：使用localStorage保存对话内容，无需登录即可使用
- **模块化开发**：使用Vue组件化开发，代码结构清晰，易于维护和扩展

## 安装和运行

### 安装依赖
- **前端框架**：Vue 3（使用Composition API和script setup语法）
- **构建工具**：Vite 5.0.8
- **路由管理**：Vue Router 4.2.5
- **HTTP请求**：Axios 1.6.2
- **样式方案**：原生CSS（使用Flexbox布局）
- **数据存储**：浏览器localStorage
## 项目结构

```
zhinengweb-vue3/
├── public/                # 静态资源
│   ├── images/            # 图片资源
│   │   ├── ai-avatar.jpg  # AI头像
│   │   └── user-avatar.jpg# 用户头像
│   └── favicon.ico        # 网站图标
├── src/                   # 源代码
│   ├── assets/            # 资源文件
│   │   └── main.css       # 全局样式
│   ├── components/        # 组件
│   │   ├── ChatInput.vue  # 聊天输入组件
│   │   └── ChatMessage.vue# 聊天消息组件
│   ├── views/             # 页面
│   │   ├── HomeView.vue   # 主页/聊天页面
│   │   └── HistoryView.vue# 历史记录页面
│   ├── App.vue            # 根组件
│   ├── main.js            # 入口文件
│   └── router.js          # 路由配置
├── index.html             # HTML模板
├── vite.config.js         # Vite配置
└── package.json           # 项目配置和依赖

```bash
npm install
```

### 开发环境运行

```bash
npm run dev
```

### 打包生产环境

```bash
npm run build
```

### 预览生产环境构建

```bash
npm run preview
```

## 后端API连接配置

前端通过API服务连接到后端，默认连接到`http://localhost:8000`。可以通过修改`src/utils/api.js`文件中的`baseURL`来更改API服务器地址：

```javascript
const api = axios.create({
  baseURL: 'http://localhost:8000', // 更改为你的后端API地址
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});
```

## 后端API服务启动

1. 进入后端服务目录：`cd ../ollama_server`
2. 安装依赖：`pip install -r requirements.txt`
3. 启动服务：`python start_server.py`

确保后端API服务正常运行，前端才能正常连接和使用。

## API接口说明

前端使用以下API接口与后端通信：
技术栈
前端框架：Vue 3（使用最新的 Composition API 和 script setup 语法）
构建工具：Vite 5.0.8（现代化的快速构建和开发工具）
路由管理：Vue Router 4.2.5（处理页面路由）
HTTP 请求：Axios 1.6.2（处理API通信）
CSS 方案：原生 CSS（使用 scoped CSS 和全局样式表）
数据存储：浏览器 localStorage（存储聊天历史和消息）
开发环境：Node.js 环境
项目重点
聊天界面实现：实现了类似聊天应用的用户界面，包括消息气泡、用户/AI头像区分
组件化设计：将功能拆分为可复用组件（ChatMessage、ChatInput）
响应式布局：适应不同屏幕尺寸的布局设计
消息持久化：使用 localStorage 保存聊天历史
状态管理：通过 Vue 3 的 ref 和 computed 管理应用状态
模拟 AI 集成：使用 mockAIProcess 模拟 AI 处理功能（实际项目中会连接到 Ollama API）
思考状态动画：实现了 AI 思考中的加载动画效果
难点与技术挑战
状态同步：在不同组件间同步消息状态和历史记录
Vue 2 到 Vue 3 的迁移：从原始 uni-app（Vue 2）项目迁移到 Vue 3，涉及 API 更改
消息流处理：处理用户输入、思考状态和 AI 响应的连续流程
历史记录管理：组织和管理聊天历史，并支持再次提问功能
头像和样式处理：确保头像和样式在不同环境正确加载和显示
页面路由：实现主页和历史记录页面之间的无缝导航
代理配置：Vite 配置中设置 API 代理，准备与后端服务集成
事件传递：从 Vue 2 的事件总线模式迁移到 Vue 3 推荐的 props/emits 模式
这个项目是一个现代化的 AI 聊天应用前端，使用了 Vue 3 的最新特性，保留了原 uni-app 项目的核心功能，但使用了更现
代的技术栈和开发方式。项目结构清晰，代码组织良好，适合作为小型到中型聊天应用的基础。
- `GET /api/status` - 检查API服务状态
- `POST /api/chat/ask` - 发送聊天请求
- `POST /api/knowledge/search` - 搜索知识库
- `GET /api/knowledge/stats` - 获取知识库统计信息

## 项目结构
package-lock.json 是 npm 包管理系统自动生成的文件，主要用途如下：
精确锁定依赖版本 - 记录了项目中所有依赖包的确切版本号、依赖关系、下载地址和完整性哈希值，确保在不同环境中安装相同
的依赖版本
加速安装过程 - 由于已经详细记录了所有依赖的信息，npm 可以直接根据这个文件快速安装依赖，而不需要重新解析依赖树
解决版本冲突 - 明确记录了依赖之间的关系和层级结构，避免版本冲突问题
团队协作保障 - 确保所有开发人员使用完全相同的依赖版本，避免"在我的机器上能运行"的问题
项目稳定性 - 防止因为依赖包小版本更新导致的不可预期问题
这个文件应该提交到版本控制系统中，以确保所有开发者和部署环境使用完全一致的依赖版本
- `src/components/` - Vue组件
  - `ChatInput.vue` - 聊天输入组件
  - `ChatMessage.vue` - 聊天消息组件
- `src/views/` - 页面视图
  - `HomeView.vue` - 主页（聊天界面）
  - `HistoryView.vue` - 历史记录页面
- `src/utils/` - 工具函数
  - `api.js` - API服务连接
- `src/App.vue` - 应用根组件
- `src/router.js` - 路由配置
- `src/main.js` - 应用入口


这个虚拟滚动没有真正的实现，只是用手动的代码才实现，倒是可以永专门的插件来实现