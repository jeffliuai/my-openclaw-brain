# PRD: OpenClaw (AI Agent) Secure Local Deployment

## 1. 專案概述 (Executive Summary)
本專案目標是在一台專屬的蘋果電腦 (MacBook Pro) 上，部署開源的 AI 代理助理 **OpenClaw**。此部署旨在打造一個安全、自動化且能替使用者處理日常雜務（如：資訊爬取、網頁操作、筆記整理）的 24 小時全天候「數位管家」。

為確保最高級別的資料安全與系統穩定性，本專案將採用**「主從式實體隔離架構」**，將 OpenClaw 與使用者的「主力工作機」徹底分開，並實施嚴格的防護網。

---

## 2. 核心架構設計 (Architecture Design)

1.  **實體隔離 (Physical Isolation)**：
    *   **Agent Machine (代理伺服器)**：一台獨立的 MacBook Pro，專職運行 OpenClaw。不存放私人機密照片、不登入個人主要銀行或社群帳號（除專用機器人帳號外）。
    *   **Primary Workstation (主力工作站)**：使用者日常辦公、寫作的電腦。兩台電腦之間僅透過特定且受控的管道（如：Git、Telegram Bot、共用資料夾）溝通。

2.  **溝通介面 (Interface)**：
    *   **遠端控制端**：透過通訊軟體 (Telegram 或 Discord) 傳送指令給 OpenClaw。
    *   **資料同步端**：使用 Git 進行 Obsidian 筆記庫 (Vault) 的版本控制與同步，確保每一次 AI 修改都能被追蹤與復原。

3.  **瀏覽器操作分流 (Browser Profile Segregation)**：
    *   在 Agent Machine 上建立專屬的 Google Chrome 設定檔 (Profile)，名為 `OpenClaw_Worker`。
    *   此設定檔僅登入免費或付費版的 AI 服務網頁（如 ChatGPT Plus, Claude Pro, Google AI Studio），**嚴禁**儲存個人信用卡資訊或使用主要密碼管理員。

---

## 3. 功能配置與安全性設定 (Functional & Security Requirements)

安裝完成後，必須進行以下關鍵設定，以確保系統安全（即上一階段討論的防護措施）：

### 3.1 權限控制 (Permissions & Sandboxing)
*   [ ] **macOS 系統權限**：僅授予 OpenClaw macOS Companion App 必要的「輔助使用 (Accessibility)」及「螢幕錄製 (Screen Recording)」權限。不給予「全磁碟取用權限 (Full Disk Access)」。
*   [ ] **Obsidian 目錄存取**：OpenClaw 僅被允許存取特定的 Obsidian Vault 目錄（建議切分出一個 `AI_Inbox` 或 `AI_Output` 的子資料夾，避免 AI 隨意更改全庫結構）。
*   [ ] **Git 防護網設定**：在 Obsidian Vault 初始化 Git 儲存庫。設定自動腳本：OpenClaw 在每次讀寫該目錄的 Markdown 檔案前後，必須執行 `git commit`。

### 3.2 阻斷風險操作 (Risk Mitigation)
*   [ ] **Human-in-the-Loop (HITL) 審批機制**：在 OpenClaw 的 `config.yaml` 或設定介面中，強制開啟「危險指令確認」。舉凡：刪除檔案 (`rm`)、寄發電子郵件、執行未知的終端機指令等，都必須發送通知至使用者的 Telegram/Discord，待使用者點擊 "Approve" 後才可執行。
*   [ ] **封鎖特定指令**：在環境變數或系統層級，限制 OpenClaw 執行 `sudo` 權限。

### 3.3 成本最佳化 (Cost Optimization)
*   [ ] **連接現有訂閱**：透過 Chrome Extension 或 Playwright 自動化，讓 OpenClaw 優先使用已登入的 ChatGPT/Claude 網頁版本，節省 API 呼叫費用。
*   [ ] **配置免免費/廉價模型**：在 OpenClaw 後台配置 Google AI Studio Key (Gemini Flash) 或是安裝本地端模型 (Ollama)，將整理格式、摘要分析等輕量級任務路由給免費模型。

---

## 4. 階段性安裝步驟 (Implementation Plan)

### Phase 1: 環境準備 (Agent Machine Setup)
1. 將專屬 MacBook Pro 系統更新至最新 macOS 版本。
2. 建立一個全新的「一般使用者 (Standard User)」帳號供 OpenClaw 運行（非 Administrator 權限）。
3. 安裝 Homebrew、Node.js、Python (如適用) 等基礎開發環境。
4. 安裝 Google Chrome，建立 `OpenClaw_Worker` 專屬設定檔。

### Phase 2: OpenClaw 部署與配置 (Deployment)
1. 依照官方文件（Clone GitHub repo 或下載安裝包），在專用帳號下安裝 OpenClaw 核心程式。
2. 安裝 macOS Companion App 以獲取必要的系統操作權限。
3. 綁定通訊軟體 (Telegram Bot Token 或 Discord Bot Token)，建立專屬的對話頻道。
4. 設定 API Keys（如 Google AI Studio Key）並配置模型路由規則 (Smart Routing)。

### Phase 3: Obsidian 整合與測試 (Obsidian & Git Integration)
1. 在 Agent Machine 上安裝 Git。
2. Clone 主力工作站的 Obsidian Vault 儲存庫。
3. 給予 OpenClaw 讀寫該 Vault 特定資料夾的權限。
4. **測試項目**：
    * 傳送一條網址至 Telegram，要求 OpenClaw 擷取內容並存入 Obsidian Inbox，驗證自動化流程。
    * 要求 OpenClaw 刪除某個測試檔案，驗證 HITL 審批機制是否有跳出警告提示。

---

## 5. 未來擴充性 (Future Scalability)
*   建置輕量級向量資料庫 (ChromaDB)，讓 OpenClaw 成為個人專屬的 RAG 檢索助理。
*   部署定時任務 (Cronjobs)，實現全自動的每日/每週摘要報告。
