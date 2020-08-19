# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['run_dist.py'],
             pathex=['/Users/jaredsimons/Desktop/Projects/Variant-Scope/VScope'],
             binaries=[('./env/lib/python3.8/site-packages/_cffi_backend.cpython-38-darwin.so', '.')],
             datas=[('./webapp/static/', './webapp/static/'), ('./webapp/templates/', './webapp/templates/'), ('./LICENSE', '.'), ('./README.md', '.'), ('/Users/jaredsimons/Desktop/Projects/Variant-Scope_Resources/extensions/', './extensions/')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='VScope',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='VScope')
