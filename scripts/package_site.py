#!/usr/bin/env python3
"""Prepara carpeta exclusivamente pública para hosting estático."""
import shutil
from pathlib import Path
from build import main as build
ROOT = Path(__file__).resolve().parent.parent

def main():
    build()
    target = ROOT / 'public'
    target.mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'index.html', target / 'index.html')
    (target / '.nojekyll').write_text('', encoding='utf-8')
    print(f'PUBLIC_ONLY={target}')

if __name__ == '__main__':
    main()
