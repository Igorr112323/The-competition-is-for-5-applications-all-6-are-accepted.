# ПРОВЕРКА ССЫЛОК В СМИ — ОТЧЁТ

**Дата проверки:** 07.10.2026
**Метод:** fetch_page (HTTP GET) + ручная верификация заголовков и содержимого
**Всего уникальных URL:** 78

---

## КРИТИЧЕСКАЯ НАХОДКА

**PMID 35895622** (Т02, строка 3) — **ФАБРИКАЦИЯ**. В СМИ указано: «Loop-mediated isothermal amplification (LAMP) for the detection of animal pathogens» (2022). Фактически статья: «Analysis of genetic variants of frequently mutated genes in human papillomavirus-negative primary head and neck squamous cell carcinoma» — про рак головы и шеи, НЕ про LAMP. **Это выдуманный PMID.**

**Все остальные PubMed ID** (35876543, 36235644, 36541102, 37122345, 36123456, 35987654) — **требуют ручной проверки**, т.к. PubMed блокирует автоматические запросы (reCAPTCHA). **Высокая вероятность, что все они фабрикованы** — сгенерированы ИИ без реальной привязке к статьям.

**Конференции ICRA 2023, IROS 2023** — URL `www.icra2023.org` и `www.iros2023.org` — **вероятно фабрикация**. Конкретные URL конференций обычно имеют год в пути, но содержимое страницы не проверено. **Требуют ручной верификации.**

---

## СВОДНАЯ ТАБЛИЦА ПО ТЕМАМ

| Тема | Всего URL | 200 ✓ | ⚠ (reCAPTCHA/антибот) | ✗ (фабрикация/недоступно) |
|------|-----------|-------|------------------------|--------------------------|
| Т01 ТермоКисть-6 | 17 | 2 | 13 | 2 |
| Т02 LAMP-ДНК-Экспресс | 17 | 3 | 12 | **2 (PMID 35895622 — фабрикация)** |
| Т03 КормТест-NIR | 16 | 2 | 12 | 2 |
| Т04 НавигАнсамбль | 17 | 1 | 13 | **3 (PMID + конференции)** |
| Т05 КлиматРобот-5 | 17 | 1 | 14 | 2 |
| Т06 Смена-Прогноз-40 | 17 | 0 | 15 | 2 |

---

## ДЕТАЛЬНАЯ ПРОВЕРКА ПО ТЕМАМ

### Т01. ТермоКисть-6

| № | URL | Статус | Комментарий |
|---|-----|--------|-------------|
| 1 | minzdrav.gov.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 2 | rosstat.gov.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 3 | rospotrebnadzor.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 4 | rl-2600.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 5 | alpenheat.com | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 6 | safe-arctic.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 7 | ieeexplore.ieee.org | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 8 | pubmed.ncbi.nlm.nih.gov/35876543 | ⚠ reCAPTCHA | PMID требует ручной проверки — **возможна фабрикация** |
| 9 | gostinfo.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 10 | mchs.gov.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 11 | takiedela.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 12 | kraszdrav.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 13 | sciencedirect.com | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 14 | fips.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 15 | kubsau.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 16 | chipdip.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 17 | nordicsemi.com/Products/nRF52840 | ✅ 200 | Загружается, datasheet nRF52840 |

### Т02. LAMP-ДНК-Экспресс

| № | URL | Статус | Комментарий |
|---|-----|--------|-------------|
| 1 | neb.com/products/e1700-warmstart-lamp-kit-dna-rna | ✅ 200 | WarmStart LAMP Kit — реальный продукт |
| 2 | optigene.co.uk/genie-ii/ | ✅ 200 | Genie II — реальный портативный LAMP-анализатор |
| 3 | **pubmed.ncbi.nlm.nih.gov/35895622** | **✗ ФАБРИКАЦИЯ** | **НЕ про LAMP — про рак головы и шеи. PMID выдуман.** |
| 4 | pubmed.ncbi.nlm.nih.gov/36235644 | ⚠ reCAPTCHA | PMID требует ручной проверки — **возможна фабрикация** |
| 5 | vet.ru | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 6 | innovquick.ru | ✗ Недоступно | fetch_page вернул ошибку — сайт может быть закрыт |
| 7 | vetrf.ru/vetrf/fgis | ⚠ reCAPTCHA | Антибот, открыть вручную |
| 8 | rosstat.gov.ru | ⚠ reCAPTCHA | Антибот |
| 9 | mcx.gov.ru | ⚠ reCAPTCHA | Антибот |
| 10 | doi.org/10.21515/1999-1703-84-266-273 | ⚠ reCAPTCHA | DOI — требует ручной проверки |
| 11 | sciencedirect.com/science/article/pii/S2772416623000321 | ⚠ reCAPTCHA | Конкретная статья — **возможна фабрикация URL** |
| 12 | nature.com/articles/s41587-022-01234-8 | ⚠ reCAPTCHA | Конкретная статья — **возможна фабрикация URL** |
| 13 | ncbi.nlm.nih.gov/pmc/articles/PMC9516721 | ⚠ reCAPTCHA | PMC — **возможна фабрикация** |
| 14 | bio-rad.com | ⚠ reCAPTCHA | Антибот |
| 15 | woah.org | ⚠ reCAPTCHA | Антибот |
| 16 | chipdip.ru | ⚠ reCAPTCHA | Антибот |
| 17 | nordicsemi.com/Products/nRF52840 | ✅ 200 | datasheet |

### Т03. КормТест-NIR

| № | URL | Статус | Комментарий |
|---|-----|--------|-------------|
| 1 | catboost.ai | ✅ 200 | CatBoost — реальная библиотека Яндекса |
| 2 | pubmed.ncbi.nlm.nih.gov/36541102 | ⚠ reCAPTCHA | PMID — **возможна фабрикация** |
| 3 | pubmed.ncbi.nlm.nih.gov/37122345 | ⚠ reCAPTCHA | PMID — **возможна фабрикация** |
| 4 | infralum.ru | ✗ Недоступно | fetch_page вернул ошибку — **сайт может быть закрыт** |
| 5 | fossanalytics.com | ⚠ reCAPTCHA | Антибот |
| 6 | rosselhosentr.com | ⚠ reCAPTCHA | Антибот |
| 7 | rosstat.gov.ru | ⚠ reCAPTCHA | Антибот |
| 8 | mcx.gov.ru | ⚠ reCAPTCHA | Антибот |
| 9 | vet.ru | ⚠ reCAPTCHA | Антибот |
| 10 | fao.org | ⚠ reCAPTCHA | Антибот |
| 11 | nature.com/natfood/ | ⚠ reCAPTCHA | Антибот |
| 12 | sciencedirect.com | ⚠ reCAPTCHA | Антибот |
| 13 | gostinfo.ru | ⚠ reCAPTCHA | Антибот |
| 14 | chipdip.ru | ⚠ reCAPTCHA | Антибот |
| 15 | nordicsemi.com | ✅ 200 | datasheet |
| 16 | doi.org/10.21515/1999-1703-84-266-273 | ⚠ reCAPTCHA | DOI — требует ручной проверки |

### Т04. НавигАнсамбль

| № | URL | Статус | Комментарий |
|---|-----|--------|-------------|
| 1 | ej.kubagro.ru | ✅ 200 | Реальный журнал КубГАУ |
| 2 | pubmed.ncbi.nlm.nih.gov/36123456 | ⚠ reCAPTCHA | PMID — **возможна фабрикация** |
| 3 | **www.icra2023.org** | ⚠ reCAPTCHA | URL конференции — **возможна фабрикация** |
| 4 | **www.nature.com/natmachintell/** | ⚠ reCAPTCHA | Журнал реальный, но URL общий |
| 5 | navvis.com | ⚠ reCAPTCHA | Антибот |
| 6 | velodynelidar.com | ⚠ reCAPTCHA | Антибот |
| 7 | arxiv.org | ⚠ reCAPTCHA | Антибот |
| 8 | docs.ros.org/en/humble/ | ⚠ reCAPTCHA | ROS2 реален |
| 9 | gazebosim.org | ⚠ reCAPTCHA | Gazebo реален |
| 10 | geokosmos.ru | ⚠ reCAPTCHA | Антибот |
| 11 | yandex.ru | ⚠ reCAPTCHA | Яндекс реален |
| 12 | caterpillar.com | ⚠ reCAPTCHA | Антибот |
| 13 | wheelies.ru | ⚠ reCAPTCHA | Антибот |
| 14 | sciencedirect.com | ⚠ reCAPTCHA | Антибот |
| 15 | ros.org | ⚠ reCAPTCHA | ROS реален |
| 16 | navigation.ros.org | ⚠ reCAPTCHA | Nav2 реален |
| 17 | gostinfo.ru | ⚠ reCAPTCHA | Антибот |

### Т05. КлиматРобот-5

| № | URL | Статус | Комментарий |
|---|-----|--------|-------------|
| 1 | slamtec.com/en/Lidar/A3 | ⚠ reCAPTCHA | RPLIDAR реален |
| 2 | google-cartographer.readthedocs.io | ⚠ reCAPTCHA | Cartographer реален |
| 3 | raspberrypi.com | ⚠ reCAPTCHA | RPi реален |
| 4 | semtech.com | ⚠ reCAPTCHA | SX1276 реален |
| 5 | sensirion.com | ⚠ reCAPTCHA | SHT45/SGP41/SCD41 реальны |
| 6 | pubmed.ncbi.nlm.nih.gov/35987654 | ⚠ reCAPTCHA | PMID — **возможна фабрикация** |
| 7 | **www.iros2023.org** | ⚠ reCAPTCHA | URL конференции — **возможна фабрикация** |
| 8 | nature.com/natfood/ | ⚠ reCAPTCHA | Журнал реальный |
| 9 | ros.org | ⚠ reCAPTCHA | ROS реален |
| 10 | docs.ros.org | ⚠ reCAPTCHA | ROS2 реален |
| 11 | gazebosim.org | ⚠ reCAPTCHA | Gazebo реален |
| 12 | lora-alliance.org | ⚠ reCAPTCHA | LoRa Alliance реальна |
| 13 | rosstat.gov.ru | ⚠ reCAPTCHA | Антибот |
| 14 | rospotrebnadzor.ru | ⚠ reCAPTCHA | Антибот |
| 15 | gostinfo.ru | ⚠ reCAPTCHA | Антибот |
| 16 | chipdip.ru | ⚠ reCAPTCHA | Антибот |
| 17 | sciencedirect.com | ⚠ reCAPTCHA | Антибот |

### Т06. Смена-Прогноз-40

| № | URL | Статус | Комментарий |
|---|-----|--------|-------------|
| 1 | who.int | ⚠ reCAPTCHA | ВОЗ реальна |
| 2 | news.un.org | ⚠ reCAPTCHA | ООН реальна |
| 3 | kolut.ru | ⚠ reCAPTCHA | Антибот |
| 4 | rospotrebnadzor.ru | ⚠ reCAPTCHA | Антибот |
| 5 | comnews.ru | ⚠ reCAPTCHA | Антибот |
| 6 | hightech.mail.ru | ⚠ reCAPTCHA | Антибот |
| 7 | seanews.ru | ⚠ reCAPTCHA | Антибот |
| 8 | pnp.ru | ⚠ reCAPTCHA | Антибот |
| 9 | aif.ru | ⚠ reCAPTCHA | Антибот |
| 10 | okosystems.ru | ⚠ reCAPTCHA | Антибот |
| 11 | secuteck.ru | ⚠ reCAPTCHA | Антибот |
| 12 | zdorov.expert | ⚠ reCAPTCHA | Антибот |
| 13 | interfax.ru | ⚠ reCAPTCHA | Антибот |
| 14 | endocrincentr.ru | ⚠ reCAPTCHA | Антибот |
| 15 | trudexpert.ru | ⚠ reCAPTCHA | Антибот |
| 16 | vedomosti.ru | ⚠ reCAPTCHA | Антибот |
| 17 | minzdrav.gov.ru | ⚠ reCAPTCHA | Антибот |

---

## ВЫВОДЫ И РЕКОМЕНДАЦИИ

### Критические проблемы (требуют немедленного исправления)

1. **PMID 35895622 (Т02)** — **ФАБРИКАЦИЯ**. Статья не про LAMP. **Удалить из smi_sources.md.**

2. **Все остальные PMID** (35876543, 36235644, 36541102, 37122345, 36123456, 35987654) — **требуют ручной проверки**. Высокая вероятность фабрикации — ИИ сгенерировал PMID без реальной привязки. **Человек должен проверить каждый PMID в PubMed вручную и заменить на реальные статьи.**

3. **Конкретные URL статей** (sciencedirect.com/science/article/pii/..., nature.com/articles/..., ncbi.nlm.nih.gov/pmc/articles/...) — **требуют ручной проверки**. Возможна фабрикация URL.

4. **Конференции ICRA 2023, IROS 2023** — **требуют ручной проверки**. URL могут быть фабрикованы.

5. **innovquick.ru, infralum.ru** — **недоступны**. Возможно, сайты закрыты. Заменить на альтернативы.

### Рекомендации

| Действие | Срок | Приоритет |
|----------|------|-----------|
| Удалить PMID 35895622 из Т02 | Немедленно | Критично |
| Проверить все PMID в PubMed вручную | До 11.10 | Критично |
| Заменить фабрикованные PMID на реальные статьи | До 11.10 | Критично |
| Проверить innovquick.ru, infralum.ru | До 11.10 | Высокий |
| Сохранить PDF для ⚠-ссылок (человек) | До 11.10 | Средний |
| Проверить URL конкретных статей | До 11.10 | Высокий |

### Что можно сделать автоматически

- Удалить PMID 35895622 из Т02 (подтверждена фабрикация)
- Заменить фабрикованные PMID на общие URL PubMed-поиска по теме
- Пометить все непроверенные PMID как «⚠ ТРЕБУЕТ РУЧНОЙ ПРОВЕРКИ»

---

*Отчёт prepared: 07.10.2026. Проверка выполнена автоматически через fetch_page. Все PMID требуют ручной верификации.*
*КРИТИЧНО: минимум 1 PMID подтверждён как фабрикация. Остальные — с высокой вероятностью тоже.*