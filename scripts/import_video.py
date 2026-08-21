"""
Утилита импорта и загрузки видео Беслана для мгновенного воспроизведения
"""

import sys
import os
import shutil

DEST_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'public', 'assets', 'beslan.mp4'
)

def import_local_file(source_path):
    if not os.path.exists(source_path):
        print(f"❌ Файл не найден: {source_path}")
        return False
    
    os.makedirs(os.path.dirname(DEST_FILE), exist_ok=True)
    shutil.copy2(source_path, DEST_FILE)
    print(f"✅ Успешно скопировано в: {DEST_FILE}")
    print(f"📊 Размер файла: {os.path.getsize(DEST_FILE) / 1024 / 1024:.2f} МБ")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        source = sys.argv[1]
        import_local_file(source)
    else:
        print("Использование:")
        print("  python scripts/import_video.py <путь_к_вашему_видео.mp4>")
        print(f"\nТекущее назначение: {DEST_FILE}")
