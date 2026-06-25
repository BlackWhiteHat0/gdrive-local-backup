# Phone Data To Compute System

一個自動把 Google 雲端硬碟指定資料夾的檔案下載到本機、並刪除雲端原檔的小工具。
支援開機時與每 10 分鐘自動執行（透過 Windows 工作排程器）。

## 功能

- 檢查 Google Drive 指定資料夾是否有檔案
- 一般檔案直接下載；Google 文件 / 試算表 / 簡報自動匯出成 .docx / .xlsx / .pptx
- 自動遞迴進入子資料夾
- 下載完成後刪除雲端原始檔案
- 可設定為開機啟動與每 10 分鐘自動執行

## 需求

- Windows
- Python 3.10 以上
- 一個 Google 帳號與 Google Cloud 專案（用來取得 API 憑證）

## 安裝

1. 複製專案並進入資料夾：

```bash
   git clone <repo 網址>
   cd Phone_Data_To_Compute_System
```

2. 建立並啟動虛擬環境：

```bash
   python -m venv venv
   venv\Scripts\activate
```

3. 安裝相依套件：

```bash
   python -m pip install -r requirements.txt
```

## 設定 Google API 憑證

1. 前往 [Google Cloud Console](https://console.cloud.google.com/) 建立專案
2. 啟用 **Google Drive API**
3. 建立 **OAuth 用戶端 ID**（類型：桌面應用程式），下載憑證檔
4. 將下載的檔案改名為 `credentials.json`，放到專案根目錄
5. 在「OAuth 同意畫面」的「測試使用者」中，加入你自己的 Google 帳號

## 設定環境變數

複製範本並填入自己的值：

```bash
copy .env.example .env
```

然後編輯 `.env`：

- `FOLDER_ID`：來源資料夾 ID（在瀏覽器打開該資料夾，網址後面那串）
- `DOWNLOAD_DIR`：本機下載目的地（路徑用 `/` 或 `\\`）

## 使用

第一次執行會跳出瀏覽器要求授權，完成後會自動產生 `token.json`，之後就不會再要求登入：

```bash
python main.py
```

或直接執行 `start.bat`（會自動啟動虛擬環境並執行）。

## 設定自動執行（Windows 工作排程器）

1. 開啟「工作排程器」，建立工作
2. 動作：程式設為 `start.bat` 的完整路徑，起始位置設為專案資料夾
3. 觸發器一：「登入時」
4. 觸發器二：「依排程」→ 每天 → 重複間隔 10 分鐘 → 持續時間「無限期」

## 注意事項

- 刪除為**永久刪除**（不進垃圾桶）。如需保留在垃圾桶，請改用 trash 方式。
- Google 文件匯出成 Office 格式時，複雜排版可能略有跑版；若需保真可改匯出為 PDF。
- 所有檔案目前下載到同一個資料夾，不保留原本的子資料夾結構。

