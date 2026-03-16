# OpenClaw 設計指引與願景 (Design Guidelines & Vision)

我已經為你下載了 OpenClaw 的 GitHub 官方原始碼 (至 `/Users/jeffliu/my-claude-skills/openclaw-docs`)，並深度閱讀了其核心文件 `VISION.md` 與 `AGENTS.md`。

以下是 OpenClaw 官方定義的核心設計理念與技術指引分類總結：

## 1. 核心產品願景 (Core Vision)
* **「The AI that actually does things」**：OpenClaw 的定位不是一個單純聊天的機器人，而是一個**「真正能幫你做事」**的 AI 代理。它能在你的設備上運行、在你的通訊軟體裡聽命，並且遵循「你的規則」。
* **階段性優先級 (Current Priorities)**：
  1. 安全性與安全的預設防護 (Security and safe defaults)
  2. 修復 Bug 與系統穩定性 (Bug fixes and stability)
  3. 初始設定的可靠性與使用者體驗 (Setup reliability and first-run UX)
* **未來發展方向**：支援所有主流大模型 (如 Claude, OpenAI, Gemini 等)、增強跨平台的終端 App (如 macOS, iOS, Windows)、強化網頁前端與 CLI 的操作體驗。

## 2. 安全性哲學 (Security Philosophy)
* **「在強大與安全之間取得刻意的平衡」**：OpenClaw 的目標是保持強大 (能執行 Shell 指令、存取檔案)，但**將高危險操作的決策權交還給人類 (Operator-controlled)**。
* **終端機優先 (Terminal-first setup by design)**：雖然這增加了入門門檻，但官方刻意保留終端機設定，是為了確保每一位使用者在安裝時，都能「明確看到並同意」所有的權限授予、資安設定與認證步驟。官方**拒絕**為了方便而隱藏關鍵安全決策的「傻瓜包」。

## 3. 架構設計：核心輕量化與外掛生態系 (Plugins & MCP)
* **保持核心純粹 (Core stays lean)**：OpenClaw 的核心架構被定義為一個「高度極簡的協調器 (Orchestration system)」。任何非必備的進階功能，都應該被做成擴充插件 (Plugins/Skills)。
* **ClawHub 技能市集**：新的技能應該優先發布到 ClawHub，而不是塞進 OpenClaw 核心。這類似 Obsidian 的社群外掛機制。
* **支援 MCP (Model Context Protocol)**：官方透過獨立的 `mcporter` 橋接器來支援 MCP，藉此將 MCP 伺服器與 OpenClaw 的核心運行時 (Runtime) 脫鉤，避免 MCP 的頻繁變動影響系統穩定性。

## 4. 技術與程式碼規範 (Technical & Coding Style)
* **TypeScript 極致運用**：選擇 TypeScript 的原因是為了保持專案的「高可駭客性 (Hackable by default)」，讓開發者能快速迭代、修改與擴充。
* **嚴格的模組分離與動態載入**：文件明定不允許隨意修改 Prototype；要求嚴格的 TypeScript 型別檢查；並且針對檔案大小（建議於 500~700 行以內）有明確的重構建議。
* **Multi-Agent 安全性 (多重代理並行防護)**：考量到未來可能會有多個 AI Agent 同時在電腦裡運作，指引中特別強調在自動化操作 Git 或檔案時，絕對不能隨意丟棄 (drop/stash) 其他人的進度，且操作必須嚴格限制在專屬的 Session 當中。

---

### 💡 總結
OpenClaw 的設計指引非常清晰：它正在建立一個像 **Linux 或 Obsidian** 一樣的生態系——**極致輕量、高度開放、強調隱私安全，並將所有花俏的進階功能全部交給 Plugin 外掛系統來實現。**
