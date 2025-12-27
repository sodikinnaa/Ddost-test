#!/bin/bash
# gitpush.sh
# Skrip otomatis untuk add, commit, dan push ke branch tertentu

# Panduan penggunaan:
# ./gitpush.sh "<pesan commit>" <nama_branch>
# Contoh:
#   ./gitpush.sh "update fitur login" dev
#   ./gitpush.sh "perbaiki bug fetch data" main

# Pastikan ada pesan commit dan nama branch
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "⚠️  Penggunaan: $0 \"<pesan commit>\" <nama_branch>"
  echo "Contoh: $0 \"update fitur\" dev"
  exit 1
fi

COMMIT_MSG="$1"
BRANCH="$2"

# Pindah ke folder tempat skrip berada (root project)
cd "$(dirname "$0")"

# Tampilkan status
echo "📦 Status repository:"
git status

# Tambahkan semua perubahan
echo "➕ Menambahkan semua perubahan..."
git add .

# Commit hanya jika ada perubahan staged
if git diff --cached --quiet; then
  echo "ℹ️  Tidak ada perubahan yang perlu di-commit."
else
  echo "📝 Melakukan commit dengan pesan: \"$COMMIT_MSG\""
  git commit -m "$COMMIT_MSG"
fi

# Cek apakah branch yang dimaksud ada secara lokal
if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  # Pull dulu agar branch up to date (opsional keamanan)
  echo "⬇️  Menarik update terbaru dari branch \"$BRANCH\" sebelum push..."
  git pull origin "$BRANCH"
else
  echo "⚠️  Branch \"$BRANCH\" belum ada lokal. Membuat dan mengecek ke branch..."
  git checkout -b "$BRANCH"
  git pull origin "$BRANCH" || true
fi

# Push ke branch yang ditentukan user
echo "🚀 Mengirim ke branch \"$BRANCH\"..."
if ! git push origin "$BRANCH"; then
  echo "❌ Gagal push ke branch \"$BRANCH\". Pastikan branch sudah ada di remote atau periksa pesan error di atas."
  exit 1
fi

echo "✅ Selesai! Semua perubahan sudah dikirim ke remote repository di branch \"$BRANCH\"."
