# Установка raster-2-vector

Полная обновлённая инструкция с командами для Linux, macOS, Windows, Docker и разных агентов: [docs/INSTALL.md](docs/INSTALL.md). Русское введение: [README_RU.md](README_RU.md).

Навык для AI-агентов:

```bash
npx skills add shubinlab/raster-2-vector --skill raster-2-vector --agent '*' -g -y
```

На машине должен быть Node.js 22.20+, чтобы запустить установщик `npx skills`; саму векторизацию выполняет **отдельный Python-движок**.

Универсальный движок через Docker:

```bash
git clone https://github.com/shubinlab/raster-2-vector.git
cd raster-2-vector
docker build -t raster-2-vector .
docker run --rm raster-2-vector doctor
```

При наличии системных Cairo/Potrace на Linux/macOS: `python -m pip install -e .`, затем `raster-2-vector doctor`. Для Windows без WSL2 рекомендуется Docker.

Проверка результата возвращает SVG, PNG и PNG-наложение на исходный растр. Не следует объявлять «совместимо с любой ОС» только по факту установки SKILL.md.
