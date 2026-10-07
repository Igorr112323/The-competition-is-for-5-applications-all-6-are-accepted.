# АУДИТ КОДА — model.py

**Дата:** 07.10.2026
**Окружение:** Python 3.11, numpy, scipy, pandas, matplotlib, openpyxl, ezdxf, trimesh

| Тема | Файл | Запуск | Ошибки | Выходные файлы |
|------|------|--------|--------|---------------|
| Т01 | model.py (306 строк) | ✅ | нет | 5 XLSX + 1 PNG |
| Т02 | model.py (567 строк) | ✅ | нет | 6 XLSX + 1 CSV + 9 PNG + 1 STL |
| Т03 | model.py (429 строк) | ✅ | **была ошибка STL** → исправлена | 5 XLSX + 1 CSV + 9 PNG + 1 STL |
| Т04 | model.py (407 строк) | ✅ | нет | 5 XLSX + 1 CSV + 9 PNG |
| Т05 | model.py (409 строк) | ✅ | **была ошибка STL** → исправлена | 5 XLSX + 1 CSV + 9 PNG + 1 STL |
| Т06 | model.py (155 строк) | ✅ | нет | 2 XLSX + 2 CSV + 1 PNG |

## Исправления

| Файл | Ошибка | Исправление |
|------|--------|-------------|
| T03 model.py | `ValueError: too many values to unpack` в write_stl | Заменён `for n, verts` → `for item` + `for tri in item[1:]` |
| T05 model.py | STL: vertex писался как tuple `(0,0,0)` | Аналогичное исправление write_stl |

## requirements.txt

`_shared/requirements.txt` создан.

---

*Аудит кода: 07.10.2026*