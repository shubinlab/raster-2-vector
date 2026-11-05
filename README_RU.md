# raster-2-vector

Типографическая векторизация логотипов и букв. [Репозиторий](https://github.com/shubinlab/raster-2-vector).

## Установка навыка для AI-агентов

Для [skills CLI](https://github.com/vercel-labs/skills) нужен Node.js 22.20+:

```bash
npx skills add shubinlab/raster-2-vector --skill raster-2-vector --agent '*' -g -y
```

Это устанавливает **инструкции агента**. Сам Python-движок с библиотеками Cairo/Potrace устанавливается **отдельно**. Для восьми распространённых агентов предусмотрен автономный установщик:

```bash
python scripts/install.py --platform all --scope user
```

## Движок для Windows, macOS и Linux

Самый переносимый вариант — Docker:

```bash
git clone https://github.com/shubinlab/raster-2-vector.git
cd raster-2-vector
docker build -t raster-2-vector .
docker run --rm raster-2-vector doctor
```

Для Linux/macOS можно после системной установки Cairo и Potrace выполнить `python -m pip install -e .` и `raster-2-vector doctor`. Native Windows ещё не проверен полностью: Docker или WSL2 предпочтительнее.

[Инструкция для всех ОС](docs/INSTALL.md) · [Матрица совместимости](docs/COMPATIBILITY.md) · [Обзор 31 GitHub-репозитория](docs/GITHUB_RESEARCH.md)

## Контроль качества

Результат всегда состоит из трёх файлов: **SVG**, PNG-предпросмотр и PNG-наложение на исходный растр. По умолчанию требуется IoU ≥95%, но при явно согласованных эстетических изменениях возможны отклонения. Геометрия букв, прямые штрихи и сопряжения кривых контролируются отдельно.

**Лицензия на исходный код пока не выбрана.** Публичный GitHub-репозиторий не означает разрешение на копирование и распространение.
