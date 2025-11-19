# antigravity-bin - Arch Linux Package

Автоматически обновляемый пакет для установки Google Antigravity на Arch Linux.

## Установка

### Из этого репозитория

```bash
git clone https://github.com/asychin/antigravity-arch.git
cd antigravity-arch
makepkg -si
```

## Обновление

Пакет автоматически проверяется на обновления каждый день через GitHub Actions. Когда выходит новая версия Antigravity, PKGBUILD автоматически обновляется.

Для обновления установленного пакета:

```bash
cd antigravity-arch
git pull
makepkg -si
```

## Структура репозитория

- `PKGBUILD` - Скрипт сборки пакета для Arch Linux
- `.SRCINFO` - Метаданные пакета (генерируется автоматически)
- `update_package.py` - Скрипт для автоматического обновления версии
- `.github/workflows/update.yml` - GitHub Actions workflow для автоматических проверок

## Как это работает

1. GitHub Actions запускается ежедневно или вручную
2. Скрипт `update_package.py` проверяет страницу загрузки Antigravity
3. Если обнаружена новая версия:
   - Загружается файл и вычисляется SHA256
   - Обновляется `PKGBUILD` с новой версией и контрольной суммой
   - Генерируется `.SRCINFO`
   - Изменения коммитятся в репозиторий

## Зависимости

Пакет требует следующие зависимости:
- gtk3
- nss
- alsa-lib
- libxss
- libxtst
- xdg-utils
- glibc
- nspr
- at-spi2-core
- libdrm
- mesa

## Лицензия

Antigravity является проприетарным ПО от Google.

