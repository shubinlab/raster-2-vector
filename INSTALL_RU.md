# Установка и использование raster-2-vector

Этот Agent Skill для Codex/Claude Code восстанавливает типографические SVG из растра, упрощает существующие SVG и измеряет расхождения с оригиналом. Нужны Python 3.10+ и зависимости из `requirements.txt`. Для команды `trace` нужна нативная библиотека Potrace.

## Установка: Ubuntu / Debian / Windows WSL2

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip libpotrace0
git clone https://github.com/shubinlab/raster-2-vector.git
cd raster-2-vector
bash install.sh codex
```

Аргумент `codex` устанавливает навык в `~/.agents/skills/raster-2-vector`, `claude` в `~/.claude/skills/raster-2-vector`, `both` в оба расположения. Установщик не перезаписывает существующие каталоги.

## macOS

Установите Python 3.10+ и Potrace (`brew install potrace`). Затем клонируйте репозиторий и запустите `bash install.sh codex` или `bash install.sh claude`. На некоторых конфигурациях macOS `ctypes` не найдёт нативную библиотеку Potrace: в таком случае `trace` может быть недоступен до настройки пути, а `refine` и `audit` работают без неё.

## Windows

Рекомендуется Windows Subsystem for Linux 2 (WSL2) с Ubuntu и приведённой выше инструкцией. Нативный Windows без WSL2 не тестировался.

## Ручная установка в проект

Скопируйте каталог репозитория с `SKILL.md`, `scripts/`, `tests/`, `references/` в `.agents/skills/raster-2-vector/` (Codex) или `.claude/skills/raster-2-vector/` (Claude Code) вашего проекта и из установленного каталога запустите:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/r2v.py doctor
.venv/bin/python -m unittest discover -s tests -v
```

## Проверка установки после install.sh

```bash
~/.agents/skills/raster-2-vector/.venv/bin/python ~/.agents/skills/raster-2-vector/scripts/r2v.py doctor
~/.agents/skills/raster-2-vector/.venv/bin/python -m unittest discover -s ~/.agents/skills/raster-2-vector/tests -v
```

Откройте новую сессию Codex/Claude Code после установки, чтобы агент обнаружил навык.

## CLI

Запускайте команды из установленного каталога с виртуальным окружением:

```bash
# Растр -> SVG + PNG + наложение
.venv/bin/python scripts/r2v.py trace /path/source.png --out /path/result.svg --goal balanced --min-iou 0.95

# Оптимизация существующего SVG относительно исходника
.venv/bin/python scripts/r2v.py refine /path/current.svg --source /path/source.png --out /path/refined.svg --min-iou 0.95

# Только проверка SVG
.venv/bin/python scripts/r2v.py audit /path/source.png /path/current.svg --out /path/verified.svg --min-iou 0.95
```

На одну проверку выдаются **три файла**: `result.svg`, `result.png`, `result_overlay.png`. Метрики выводятся в JSON в терминал.

## Особенности и ограничения

- Приоритет: прямые штрихи должны оставаться прямыми; круги и дуги должны быть геометрически регулярными; сопряжения гладкими.
- Автоматическая метрика IoU не заменяет визуальную и типографическую экспертизу. Исключение ниже 95% требует явного решения и измерения.
- Предназначен прежде всего для одноцветных логотипов/букв, не для фотографий.
- Неизвестный SVG с внешними ресурсами, шрифтами, группами, трансформациями или градиентами может быть не поддержан. Сохраняйте оригинал отдельно и используйте новый путь `--out`.
- Код запускается локально. Приватный ChatGPT-плагин не устанавливает зависимости Python на устройство.
- Для публичного распространения библиотеки и исполняемый код необходимо самостоятельно проверить. В репозитории пока нет LICENSE, поэтому открытая лицензия не предоставлена.
