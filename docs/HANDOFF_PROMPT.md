# Protez Universal Deobfuscator — промпт-хендофф (скопировать целиком в новый чат)

Ты продолжаешь работу над **Protez Universal Deobfuscator** — инструментом, который снимает
обфускацию с Lua/Luau-скриптов (Roblox-экосистема) и отдаёт читаемый исходник.
Репо: `/home/user/Protez`, ветка **`arena/898b5636-protez`** (работай только в ней).
Ориентир по времени: текущая вершина ветки — `1288c36`.

---

## 0. Главная цель

**Универсальная корректность по всем семействам и всем версиям Luraph.** Не «одна фикстура
глубоко», а широта: любой скрипт из списка ниже должен (а) читаемо восстанавливаться и
(б) *работать в рантайме не хуже, чем работал его вход*.

Формулировка пользователя: «нафиг нам 14.6, мы делаем на все версии luraph, как и на другие
обфускаторы, не зря Protez Universal Deobfuscator» и «продолжай…до совершенства».
Обязательный охват: Luraph (v14.6, v14.7, v15.0, v15.1), WeAreDevs 2.4, Wynfuscate v5,
IronBrew3 (и IronBrew1/2), Prometheus, Moonsec v2/v3, PSU 1.0/4.0.A, Nexus 2.0.

**Определение готовности (метрика):** для каждой фикстуры из `samples/real/` вывод
прогоняется в том же эмуляторе и получает статус **не хуже входа**; в идеале — `completed`
и с захваченным выводом payload'а. Плюс: полный список семейств/версий, никаких заглушек в
девиртуализаторе, читаемость сохраняется.

---

## 1. С чего начать (5 минут)

```bash
cd /home/user/Protez
git log --oneline -1                      # ожидается 1288c36 или новее
/home/user/pyenv/bin/python -m pytest tests/ -q     # ожидается 265 passed, 1 skipped
```

Если `git log` показывает старое (например `03e4f44`) — **песочница откатила репозиторий**
(такое бывает посреди хода). Рабочая процедура восстановления:

```bash
cd /home/user/Protez
git fetch origin
git reset --mixed origin/arena/898b5636-protez     # работа уже запушена, терять нечего
bash dev/bootstrap_env.sh                          # venv /home/user/pyenv + Luau toolchain (~3 мин)
/home/user/pyenv/bin/python -m pytest tests/ -q
```

`dev/bootstrap_env.sh` пересобирает: venv `/home/user/pyenv` (py3.11 + lupa + zstandard +
pytest + tkinterdnd2), нативный Luau (пин tag 0.740) и кладёт `luau-ast`, `luau-compile`,
`protez-native-host` в `tools/`. Всё это gitignored намеренно — после сброса просто
перезапускай скрипт. **Пушить часто** (`git push origin arena/898b5636-protez`): только
запушенное переживает сброс.

---

## 2. Карта кода

| Файл | Роль |
|---|---|
| `core/pipeline.py` | `DeobfuscationPipeline` — оркестратор. `MAX_PIPELINE_SECONDS = 90` (главный бюджетирующий рычаг). Здесь же `_deliverable_source` (проверка доставки) и `_write_engine_result` (отчёт + запись `destroyed_N.lua`). |
| `core/engine.py` | `RecoveryEngine.recover()` — слои, детект семейства, эмуляция, форматирование; `RecoveryResult` (source, family, partial, layers, emulator, notes). |
| `core/emulator.py` | Портативный бэкенд Lua 5.1 (lupa) с полным executor-API. `LuaEmulator`, `run_bounded` (форк + wall-clock kill + спул наблюдений), `outcome_rank(status)` = completed(0) < limit(1) < error(2). `MAX_INSTRUCTIONS = 80_000_000 // HOOK_STEP`. |
| `core/deobfuscator.py` | Статический проход: константы/строки. Ключевое: `_fold_fits_context`, `_matching_paren_is`, `_concrete`, `_prepare_replacement`, `_ExpressionParser`, `_PRECEDENCE`. |
| `core/output.py` | Политика одного артефакта: `next_output_path` → `destroyed_N.lua`, `clean_result_header`, `collapse_to_one_line`, `single_line_chunk_document`. |
| `core/families.py` | 14 хендлеров + `detect_families`. `WeAreDevsHandler` (confidence 0.5 на `_looks_like_numeric_loader`), `PrometheusHandler`, `LuraphHandler` и т.д. |
| `core/injector_env.py` | `build_lua_prelude()` — «Real» executor surface, `get_profile`. |
| `core/vm_dump.py` | Снятие таблиц VM прямо из работающего лоадера (`debug.getinfo(level,'fS')` — это **наш** дампер, не payload). |
| `core/vm_recover.py` | `render_analysis`, `summary_line` — поверхность VM для отчёта. |
| `core/luraph_devirtualizer.py` | Обёртка над vendored-лифтером, `LuraphDevirtualizationError`, `_install_analysis_deadline`. |
| `third_party/protez_luraph_v15/` | Вендоренный лифтер Luraph. `core/obfuscators/luraph_v15/driver.py` — цикл раундов; `core/backend.py` (`hoist_function_level_temps` → `scope_locals`); `core/variables.py` — скоупинг локалов. |
| `core/moonsec_devirtualizer.py`, `core/luraph_static.py`, `core/bytecode_decompiler.py`, `core/formatter.py`, `core/sandbox.py`, `core/tracer.py` | Остальные маршруты. |
| `gui/app.py` | Пиксельный GUI (Tkinter). `main.py` — точка входа. |
| `tests/` | 24 файла, `pytest` (unittest-стиль). |

### Инструменты разработчика (все в `dev/`, все нужны)

```bash
# свуп всех фикстур: отчёты в logs/fixture-sweep/reports, выводы в logs/fixture-sweep/output
/home/user/pyenv/bin/python dev/fixture_sweep.py --mode pipeline --limit 120

# рантайм-матрица: прогоняет каждый свежий результат и сравнивает с его же входом
/home/user/pyenv/bin/python dev/check_runtime.py --wall 25

# один файл в эмуляторе (главный отладочный инструмент)
/home/user/pyenv/bin/python dev/emulate_file.py <файл.lua> --wall 15 [--chunks]

# бисект статических правок: какой фолд ломает рантайм
/home/user/pyenv/bin/python dev/bisect_fold.py samples/real/wearedevs/0122989.lua

# лифт Luraph вне пайплайна, со своим бюджетом
/home/user/pyenv/bin/python dev/luraph_lift_probe.py samples/luraph_v14_7_HEHE.lua 900 out=/tmp/lift.lua
```

Отчёт свупа (`logs/fixture-sweep/reports/report_*.json`) — источник истины: `source_name`,
`family`, `partial`, `output_path`, `emulator.status/error`, `delivery`, `vm`, `notes`,
`native_runs`.

### Диагностические env-хуки (использовать, а не угадывать)

`PROTEZ_EMU_CALL_LOG=<path>` + `PROTEZ_EMU_CALL_LOG_MAX=<n>` — журнал вызовов окружения;
`PROTEZ_EMU_DIAGNOSE=1` — какие глобалы читались и не были определены (с местом);
`PROTEZ_EMU_TB=1`, `PROTEZ_EMU_TRACEBACK=1` — трейсбэки; `PROTEZ_EMU_POSITIONS`,
`PROTEZ_EMU_NO_VM_DUMP`; `PROTEZ_DUMP_HARNESS`, `DEVIRT_FULL_ROUNDS`, `DEVIRT_REQS`,
`DEVIRT_TIMING` — лифтер Luraph; `PROTEZ_ANALYSIS_DEADLINE`, `PROTEZ_LURAPH_TIME_BUDGET`,
`PROTEZ_LURAPH_SPIN_CHECKS`, `DEOB_SPIN_LATE`.

---

## 3. Что уже сделано (не переделывать, но можно улучшать)

Коммиты в ветке (сверху вниз), все проверены запуском:

1. **`9142aa0`** — исправлены две **неверные свёртки** статики:
   - `m = m and A or B` (A,B — константы): сканер начинал в середине цепочки, сворачивал
     `A or B` в `A`; при ложном `m` получался `nil` вместо `B`. Лечение — `_fold_fits_context`:
     после токена-оператора (`_PRECEDENCE` по **тексту**, не по kind!) сворачивать только
     одиночный токен или полное `( … )`.
   - `T = not k` (k — регистр лоадера): унарные свёртки вычисляли *символические* узлы
     (`_Path`), `not k` → литерал `false` → ветка state-machine уходила не туда.
     Лечение — `_concrete()` нормализует `_Path/_Namespace/_Function/_Receiver/_Game` в
     `_UNKNOWN` **до** любой свёртки (и унарной, и бинарной).
2. **`9bfa55e`** — доставка с рантайм-проверкой. Открытие: **WeAreDevs и Prometheus
   сравнивают `linedefined == lastlinedefined` своего чанка** и поднимают «Tamper Detected»,
   если их файл занимает больше одной строки, — то есть любой красиво отформатированный
   вывод для них мёртв. Решение: `_deliverable_source` прогоняет результат в эмуляторе; если
   читаемая форма сломана, тот же текст отдаётся документом с **однострочным чанком** в
   конце (`single_line_chunk_document`), а читаемая копия остаётся блок-комментарием.
   Форма пишется в отчёт (`delivery`). Плюс `collapse_to_one_line` собирает строку
   **через токенизатор** (перенос строки завершает `--`-комментарий, длинные строки
   чувствительны к переносам), и `run()` бэкенда больше не падает в `UnboundLocalError`.
3. **`c85aeca`** — проверка доставки выполняется и когда **вход сам упал** (пропускается
   только wall-clock-зависание), и однострочный вариант пробуется только если результат
   *сломан* (error), а не «limit» — иначе это лишние прогоны.
4. **`55a6fff`** — лифтер Luraph: если дедлайн обрывает **второй** раунд (добор констант),
   отдаётся листинг последнего **законченного** раунда, а не поведенческий трейс.
5. **`1288c36`** — предупреждение о том, что лифт ограничен `max_pipeline_seconds`.
6. Ранее: `6b65391` (скоупинг/подъём временных в Luraph v14, `_capture_rank`, fresh-frame в
   host.cpp), `0ad1f9f` (`dev/bootstrap_env.sh` + `dev/luraph_lift_probe.py`).

### Текущие измерения (перепроверяй сам, они меняются)

**Свуп 13 фикстур** (`samples/real/`, `--limit 120`): 10 `complete`, 3 `partial`.
Читаемы все. Быстрые: ironbrew3 ×2 (0.1 с), psu (1.6 с), wearedevs (0.6 с),
prometheus-medium (0.8 с), prometheus-wrd-v8 (3.6 с), ironbrew1 (5.8 с).
Дорогие: luraph v14.6 (52 с / 52 190 строк, partial — 5 546 недекодированных констант),
luraph v15.0 (24 с, partial — 5 удалённых payload'ов), moonsec v3 (partial — поднят
интерпретатор, программа внутри VM), aztupbrew (37 с), wynfuscate (15 с), moonsec v2 (17 с).

**Рантайм-матрица** (`dev/check_runtime.py --wall 25`): **0 из 10 хуже входа.**
- `completed`: ironbrew3 ×2, psu, wearedevs, prometheus-wrd-v8.
- `limit` и у входа, и у вывода (это фидельность, **не** дефект): aztupbrew (wall-clock),
  moonsec v2 и wynfuscate (instruction budget).
- `error` и у входа, и у вывода, но с разной причиной: ironbrew1, prometheus-medium.

**Важное открытие про детект:** обе фикстуры `samples/real/prometheus/*` — это на самом деле
вывод **WeAreDevs** (в файлах есть `--[[ v1.0.0 https://wearedevs.net/obfuscator ]]` и хвост
`…getfenv()or _ENV,unpack or table[…],newproxy,setmetatable,getmetatable,select,{...}`).
Мисдетекта нет; prometheus-medium можно считать отдельным вариантом WeAreDevs-лоадера.

**Luraph v14.7** (`samples/luraph_v14_7_HEHE.lua`): раунд 1 лифта **успешен** — 59 функций,
0 нелифтнутых блоков, ~476 с; второй раунд (добор 10 «ленивых» констант) требует ещё
одного полного лифта и не влезает в бюджет. Теперь отдаётся листинг раунда 1:
`/tmp/lift_147_partial.lua` — **14 762 строки**, `partial_reasons`: 10 нерешённых запросов
констант, 75 недекодированных констант, 5 маркеров, 5 `nil`. По умолчанию в пайплайне
(90 с) он не успевает вообще — см. задачу №1.

---

## 4. Что делать дальше (по приоритету)

### 1) Бюджет времени как параметр (главный блокер покрытия Luraph)
`MAX_PIPELINE_SECONDS = 90` в `core/pipeline.py`. v14.7 при таком бюджете не лифтится,
v14.6 едва влезает. Нужно: прокинуть бюджет в GUI (`gui/app.py` создаёт пайплайн на строке
~602 без `max_pipeline_seconds`) и в CLI, и поднимать его автоматически, когда вход
распознан как Luraph большого размера. Проверка: `dev/luraph_lift_probe.py <sample> 900` уже
даёт частичный листинг — значит дело только в бюджете, а не в алгоритме.
Учти: длинные прогоны нельзя держать в блокирующем вызове пользователя — прогресс идёт через
`progress_callback`.

### 2) Хендшейк prometheus-medium и ironbrew1 (их входы падают и без нас)
`PROTEZ_EMU_DIAGNOSE=1 dev/emulate_file.py samples/real/prometheus/medium-005c846f519dedbb.lua`
показывает: лоадер **читает 25 раз** глобал `eu4iROfVfImT` (плюс `aBcxyKpZHt2yog`, `plugin`)
и падает на `attempt to index local 'r' (a nil value)` — похоже на фрагмент, которому нужен
внешний хендшейк/обвязка. Их отчёт `input=error`, сравнение идёт по сигнатуре ошибки, так что
пока это «differs». Для ironbrew1 вход падает на `attempt to index local 'ch' (a nil value)`
(`:3` во входе, `:1216` в выводе). Задача: определить, что именно недополучает лоадер, и
ответить на это в executor-поверхности (`core/injector_env.py`) или в обвязке запуска.

### 3) IronBrew3: карта опкодов
Сейчас `notes`: «the VM ran inside the portable backend, so its tables were read; lifting its
opcodes to source needs a per-family opcode map». VM запускается, таблицы снимаются — нет
карты опкодов. Есть открытый референс `Gork3m/IronBrew2-Deobfuscator`; сверить, что общего
у IB2/IB3, и завести карту в `core/families.py`/девиртуализаторе. Проверка: вывод
`completed` и содержит осмысленный код, а не таблицы.

### 4) Отложенные партиалы (после 1–3)
- **luraph v14.6**: 5 546 недекодированных констант (`logs/fixture-sweep/reports/report_*v14.6*`).
  Инструментирование прошлого захода было потеряно при сбросе — восстанавливать с нуля,
  если возьмёшься.
- **luraph v15.0**: 5 удалённых payload'ов; сеть в сэндбоксе есть (`allow_network`), но
  payload'ы нужно именно догрузить и разобрать — не выполняя на хосте (см. `core/sandbox.py`).
- **moonsec v3**: поднят интерпретатор целиком (`route=moonsec-v3-vm-lifter`), программа
  внутри его VM. Нужен разбор самого интерпретатора (или его таблиц).
- **Nexus 2.0**: в `samples/real/` нет ни одной фикстуры. Без сэмпла заявлять покрытие
  нельзя. Спроси у пользователя сэмпл; в репо есть только хендлер.
- **PSU**: покрыт 4.0.A (файл `aztupbrew/sample.lua` — тоже PSU 4.0.A, не AztupBrew),
  а в требованиях PSU 1.0 — нужен сэмпл.

### 5) Тесты на поведение доставки
Правило «читаемое побеждает, пока не сломано; сломано → однострочный чанк» закреплено только
юнит-тестами `tests/test_output_policy.py` (OneLineChunkTests). Добавь интеграционный тест на
`_deliverable_source` с фейковым `_verify_runtime`: (а) readable ok → не меняем;
(б) readable error, wrapped completed → отдаём обёртку и `delivery.form`;
(в) вход wall-clock → проверка вообще не запускается.

---

## 5. Методология, которая здесь работает (соблюдай её)

1. **Истина — рантайм, а не глаза.** Любая правка проверяется прогоном: `dev/emulate_file.py`
   на входе и на выходе. «Красиво и компилируется» ничего не доказывает (`luau-compile` rc=0
   ≠ верный скоупинг: используй `luau-analyze`, он ловит `unknown global`).
2. **Докажи эквивалентность, а не похожесть.** Чтобы убедиться, что форматирование не
   изменило программу, сравнивай потоки токенов (`core.formatter.tokenize`), а не текст:
   в одном баге так и вышло, что потоки совпали, а падало всё из-за переносов строк.
3. **Бисект только по подмножествам.** `dev/bisect_fold.py`: ddmin по множеству правок.
   Префиксный бисект врёт («первое расхождение» может быть не причиной).
4. **Синтетический эксперимент вместо форензики.** Когда «Tamper Detected» не находился в
   исходнике, я: (а) заменил все переносы на пробелы и воспроизвёл ровно исходный файл
   позже — бисектом по переносам нашёл критичные; (б) обернул тело в `loadstring` одной
   строкой и получил `completed`. Это заняло минуты против часов чтения обфусцированного кода.
   **Но:** мой первый бисект ловил синтаксические ошибки склейки и врал — предикат должен быть
   точным (я искал именно «Tamper Detected»).
5. **Никогда не гейтить по `kind == "symbol"`.** В этом лексере ключевые слова (`and`, `or`,
   `not`, `end`) — `identifier`. Проверяй текст токена.
6. **Эмулятор — это fork с wall-clock kill.** `run_bounded` кладёт наблюдения в спул и
   возвращает частичный результат после убийства ребёнка. `EmulatorResult.request_calls`,
   `downloaded_payloads`, `written_captures`, `source_chunks` — **свойства-кортежи**,
   вызывать их `()` нельзя.
7. **Не удлинять блокирующие прогоны.** Длинное — в фон (`start_process`) и хвостом лога;
   пользователь недоволен «зависаниями на команде».
8. **Коммить и пушить после каждого законченного шага** — ход может прерваться сбросом.

---

## 6. Жёсткие требования пользователя (нарушать нельзя)

- GUI: пиксельный, красивый, компактный, современный.
- **Ровно один** файл результата за запуск: `destroyed_N.lua`, без лишних артефактов
  (отчёты/дампы — в `logs/`).
- Читаемый исходник открывается автоматически и отформатирован.
- Деобфускатор не падает на executor/injector-пробах (детект по строкам, проверки
  доступности функций).
- Скрипты из приватных/платных библиотек (`api.luarmor`) добываются **запуском лоадера** —
  этот путь обязан работать.
- Сначала искать существующие open-source деобфускаторы, свой код — только там, где нет
  готового.
- Executor представляется как **Real** (вымышленный), все инжектор-команды существуют и
  ведут себя правдоподобно, включая файловый API (`writefile`, `readfile`, `appendfile`,
  `listfiles`, `isfile`, `isfolder`, `makefolder`, `delfile`, `delfolder`).
- «API защита» — это **не** обфускация: получается запуском в executor-space, и этот путь
  должен работать.
- Пиксельные захваты файлов переживают не-UTF-8 payload'ы (placeholder'ы).
- Девиртуализатор — без заглушек и поверхностной работы.
- Гигиена репо — отдельная задача.
- Сэмплы пользователя запускать можно только из `samples/real/**` (они авторизованы);
  реальные пользовательские скрипты — только с разрешения.

---

## 7. Тупики и ловушки (не повторять)

- **Префиксный бисект** — врёт; только ddmin по подмножествам.
- **`luau-compile` rc=0** — не признак корректности.
- **Фолды «очевидно верных» выражений** — уже дважды ломали лоадер: `X and A or B` и
  `not <символ>`. Любая новая свёртка проверяется рантаймом.
- **Прямая склейка строк регуляркой** для однострочной формы — меняет программу
  (`--` комментарий съедает код, длинные строки ломаются). Только через токенизатор.
- **`_MISS_LOG`/`_missing` (+`import os`) из прошлого захода** — не искать, потеряны сбросом.
- **`apt-get`/root недоступны.**
- **Длинный глубокий spin/budget-raise** в эмуляторе — тупик (живой abort настоящий).
- **Никогда не ослаблять `instruction_score`.**
- **Строки статического отчёта не переписывать** без обновления их тестов.
- Помни: `EmulatorResult.*` — свойства, а не методы.

---

## 8. Критерии «совершенства» (по ним отчитываться)

1. `dev/check_runtime.py --wall 25` → **0 фикстур хуже входа**; целевое — все `completed`
   (сейчас 5/10; `limit` у aztupbrew/moonsec-v2/wynfuscate совпадает у входа и выхода).
2. `dev/fixture_sweep.py --mode pipeline --limit 120` → все 13 `complete` (сейчас 10/3),
   читаемые — 13/13 (выполнено).
3. Покрытие семейств/версий из §0 — каждая строка списка хотя бы с одной фикстурой и с
   прогоном не хуже входа (сейчас нет сэмплов Nexus 2.0 и PSU 1.0 — запросить у пользователя).
4. Девиртуализация Luraph v14.7 и v15.x — листинг отдаётся в рамках **штатного** бюджета GUI,
   без ручных флагов (`partial` допустим и обязан быть явно описан в отчёте).
5. Тесты зелёные, `git log` не содержит временного/отладочного кода.

Отчитывайся коротко: что сделал → чем доказал (команда + результат) → что дальше.
