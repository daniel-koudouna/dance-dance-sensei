# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['src\\main.py'],
             pathex=[],
             binaries=[],
             datas=[('default_config.toml', '.'), ('version.txt', '.'), ('Roboto-Regular.ttf', '.'), ('logo.png', '.'), ('logo.ico', '.'), ('img', 'img'), ('sound', 'sound')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
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
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='sensei-debug',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , uac_admin=True, icon='logo.ico')
