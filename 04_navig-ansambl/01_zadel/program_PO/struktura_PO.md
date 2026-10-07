# СТРУКТУРА ПРОГРАММЫ
## «НавигАнсамбль»

```
nav_ensemble/
├── package.xml
├── CMakeLists.txt
├── setup.py
├── nav_ensemble/
│   ├── __init__.py
│   ├── ensemble_node.py      # ROS2-узел
│   ├── arima_model.py         # Уровень 1: ARIMA
│   ├── rf_model.py            # Уровень 2: Random Forest
│   ├── gbm_model.py           # Уровень 3: Gradient Boosting
│   ├── meta_model.py          # Уровень 4: Мета-модель
│   ├── preprocessor.py        # Предобработка данных
│   ├── config.py              # Конфигурация
│   └── utils.py               # Утилиты
├── models/
│   ├── arima_weights.pkl
│   ├── rf_model.pkl
│   ├── gbm_model.pkl
│   └── meta_weights.pkl
├── launch/
│   └── ensemble.launch.py
├── test/
│   ├── test_ensemble.py
│   └── test_models.py
├── config/
│   └── params.yaml
└── README.md
```

*Структура подготовлена: октябрь 2026 г.*
