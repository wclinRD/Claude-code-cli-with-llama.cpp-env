#!/bin/bash
# Obscura 安裝腳本
# 自動檢測系統並安裝對應的二進制文件

echo "🔧 檢測系統架構..."

ARCH=$(uname -m)
OS=$(uname)

echo "📦 檢測結果:"
echo "  - OS: $OS"
echo "  - Architecture: $ARCH"

echo ""
echo "📥 下載 Obscura..."

case "$OS" in
  "Darwin")
    if [[ "$ARCH" == "arm64" ]]; then
      PLATFORM="aarch64-macos"
    elif [[ "$ARCH" == "x86_64" ]]; then
      PLATFORM="x86_64-macos"
    else
      echo "❌ 暫不支持的架構：$ARCH"
      exit 1
    fi
    ;;
  "Linux")
    if [[ "$ARCH" == "x86_64" ]]; then
      PLATFORM="x86_64-linux"
    else
      echo "❌ 暫不支持的架構：$ARCH"
      exit 1
    fi
    ;;
  *)
    echo "❌ 暫不支持的作業系統：$OS"
    exit 1
    ;;
esac

CURL_URL="https://github.com/h4ckf0r0day/obscura/releases/latest/download/obscura-${PLATFORM}.tar.gz"

if ! command -v curl &> /dev/null; then
  echo "❌ 需要安裝 curl"
  exit 1
fi

if ! command -v tar &> /dev/null; then
  echo "❌ 需要安裝 tar"
  exit 1
fi

echo "📥 下載檔案..."
curl -L -o /tmp/obscura-${PLATFORM}.tar.gz "$CURL_URL"

if [[ $? -ne 0 ]]; then
  echo "❌ 下載失敗"
  exit 1
fi

echo "📦 解壓..."
tar xzf /tmp/obscura-${PLATFORM}.tar.gz

if [[ $? -ne 0 ]]; then
  echo "❌ 解壓失敗"
  exit 1
fi

echo "📍 安裝到當前目錄..."
if [[ -f ./obscura ]]; then
  echo "✅ Obscura 已存在，跳過安裝步驟"
else
  cp -n obscura ./obscura
fi

rm -f /tmp/obscura-${PLATFORM}.tar.gz

echo ""
echo "✅ Obscura 安裝完成!"
echo ""
echo "📋 可用命令:"
echo "  obscura serve --port 9222"
echo "  obscura fetch https://example.com --dump html"
echo "  obscura scrape url1 url2 url3 --concurrency 25"
echo ""
echo "🧪 測試安裝..."
if command -v obscura &> /dev/null; then
  obscura --verbose
else
  ./obscura --verbose
fi
