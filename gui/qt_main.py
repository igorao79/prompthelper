from PySide6 import QtWidgets, QtGui, QtCore
from pathlib import Path

from shared.settings_manager import SettingsManager, get_desktop_path
from core.version import VERSION
from shared.helpers import validate_domain, get_language_by_country, get_language_display_name, check_directory_exists, ensure_empty_zip_for_landing
from shared.city_generator import CityGenerator
from shared.data import COUNTRIES_DATA
from core.cursor_manager import CursorManager
from generators.prompt_generator import create_landing_prompt
from core.update_checker import UpdateChecker


class QtMainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Генератор Лендингов v2.0 — Qt")
		self.resize(1100, 780)
		self.setMinimumSize(980, 720)

		self.settings = SettingsManager()
		self.cursor_manager = CursorManager()
		self.city_generator = CityGenerator()

		self.country = ""
		self.city = ""
		self.theme = ""
		self.domain = ""

		self._bg_threads = []
		self.max_parallel = 5
		self._active_builds = 0
		self._build_queue = []  # list of params dicts
		self._active_jobs = []  # running params
		self._job_seq = 1
		self._last_city_by_country = {}
		# Сопоставление кодов языков для человеко-читаемого отображения
		self._language_code_to_display = {
			"en": "английский",
			"ru": "русский",
			"uk": "украинский",
			"be": "белорусский",
			"kk": "казахский",
			"de": "немецкий",
			"fr": "французский",
			"it": "итальянский",
			"es": "испанский",
			"pl": "польский",
			"cs": "чешский",
			"tr": "турецкий",
			"zh": "китайский",
			"ja": "японский",
			"ko": "корейский",
			"hi": "хинди",
			"pt": "португальский",
		}
		self._build_ui()
		self._apply_modern_style()
		self._load_initial_state()
		self._init_city()
 
		# Отключено: не предлагать обновления при старте
		# восстанавливаем кастомный промпт, если был сохранён ранее
		try:
			prev_prompt = self.settings.get_prompt()
			if prev_prompt:
				self._custom_prompt = prev_prompt
		except Exception:
			pass

	def _build_ui(self):
		central = QtWidgets.QWidget()
		self.setCentralWidget(central)

		main = QtWidgets.QVBoxLayout(central)
		main.setContentsMargins(12, 12, 12, 12)
		main.setSpacing(10)

		# Header actions
		header = QtWidgets.QHBoxLayout()
		header.setSpacing(8)
		self.edit_prompt_btn = QtWidgets.QPushButton("✏️ Настроить промпт")
		self.reset_prompt_btn = QtWidgets.QPushButton("🔄 Сбросить")
		self.update_btn = QtWidgets.QPushButton("⬇️ Обновить")
		self.settings_btn = QtWidgets.QPushButton("⚙️ Настройки")
		self.grid_btn = QtWidgets.QPushButton("🧩 Режим сетки")
		self.create_btn = QtWidgets.QPushButton("🚀 СОЗДАТЬ ЛЕНДИНГ ✨")
		self.create_btn.setObjectName("PrimaryButton")
		header.addWidget(self.edit_prompt_btn)
		header.addWidget(self.reset_prompt_btn)
		header.addWidget(self.update_btn)
		header.addWidget(self.settings_btn)
		header.addWidget(self.grid_btn)
		self.version_label = QtWidgets.QLabel(f"Версия: {VERSION}")
		self.version_label.setStyleSheet("color:#94a3b8;font-size:12px;")
		header.addStretch(1)
		header.addWidget(self.version_label)
		header.addWidget(self.create_btn)
		main.addLayout(header)

		# Form grid (compact)
		form = QtWidgets.QGridLayout()
		form.setHorizontalSpacing(10)
		form.setVerticalSpacing(8)
		row = 0

		# Save path
		self.path_edit = QtWidgets.QLineEdit(self.settings.get_save_path())
		browse_btn = QtWidgets.QPushButton("📁 Выбрать")
		browse_btn.clicked.connect(self._browse_path)
		desk_btn = QtWidgets.QPushButton("🏠 Рабочий стол")
		desk_btn.clicked.connect(self._reset_to_desktop)
		form.addWidget(QtWidgets.QLabel("Папка для создания проектов"), row, 0)
		form.addWidget(self.path_edit, row, 1)
		btns = QtWidgets.QHBoxLayout()
		btns.addWidget(desk_btn)
		btns.addWidget(browse_btn)
		w_btns = QtWidgets.QWidget()
		w_btns.setLayout(btns)
		form.addWidget(w_btns, row, 2)
		row += 1

		# Theme (history)
		self.theme_combo = QtWidgets.QComboBox()
		self.theme_combo.setEditable(True)
		self.theme_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
		self.theme_combo.setPlaceholderText("Примеры: Продажа недвижимости, Строительство домов…")
		form.addWidget(QtWidgets.QLabel("Тематика лендинга"), row, 0)
		form.addWidget(self.theme_combo, row, 1, 1, 2)
		row += 1

		# Country + favorites + City
		self.country_combo = QtWidgets.QComboBox()
		self.country_combo.setEditable(True)
		self.country_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
		self.country_combo.currentTextChanged.connect(self._on_country_change)
		self.fav_btn = QtWidgets.QPushButton("☆")
		self.fav_btn.setFixedSize(32, 32)
		self.fav_btn.setToolTip("Добавить/убрать из избранного")
		self.fav_btn.setStyleSheet("QPushButton{font-size:18px; padding:0;}")
		self.fav_btn.clicked.connect(self._toggle_favorite_country)
		self.city_btn = QtWidgets.QPushButton("🎲 Сгенерировать город")
		self.city_btn.clicked.connect(self._generate_city)
		form.addWidget(QtWidgets.QLabel("Страна"), row, 0)
		cc = QtWidgets.QHBoxLayout()
		cc.setContentsMargins(0, 0, 0, 0)
		cc.setSpacing(6)
		cc_container = QtWidgets.QWidget()
		cc_container.setLayout(cc)
		cc.addWidget(self.country_combo, 1)
		cc.addWidget(self.fav_btn, 0)
		form.addWidget(cc_container, row, 1)
		form.addWidget(self.city_btn, row, 2, alignment=QtCore.Qt.AlignTop)
		row += 1

		# Language override (checkbox + combobox)
		self.custom_lang_cb = QtWidgets.QCheckBox("Нестандартный язык")
		self.custom_lang_combo = QtWidgets.QComboBox()
		self.custom_lang_combo.addItems(["en","ru","uk","be","kk","de","fr","it","es","pl","cs","tr","zh","ja","ko","hi","pt"])
		self.custom_lang_combo.setEnabled(False)
		self.custom_lang_cb.toggled.connect(self._on_custom_lang_toggle)
		self.custom_lang_combo.currentTextChanged.connect(self._on_custom_lang_changed)
		form.addWidget(self.custom_lang_cb, row, 0)
		form.addWidget(self.custom_lang_combo, row, 1)
		row += 1

		# Domain
		self.domain_edit = QtWidgets.QLineEdit()
		form.addWidget(QtWidgets.QLabel("Домен"), row, 0)
		form.addWidget(self.domain_edit, row, 1)
		self.no_images_checkbox = QtWidgets.QCheckBox("Без изображений")
		self.no_images_checkbox.setToolTip("Создать только папки и открыть Cursor с промптом")
		form.addWidget(self.no_images_checkbox, row, 2)
		row += 1

		# Правая колонка (форма + статус + инструменты)
		right_v = QtWidgets.QVBoxLayout()
		right_v.setSpacing(10)
		right_v.addLayout(form)

		# Status bar (custom)
		self.status_label = QtWidgets.QLabel("✅ Готов к работе")
		self.status_label.setObjectName("StatusLabel")
		right_v.addWidget(self.status_label)
		# Mini queue panel
		queue_group = QtWidgets.QGroupBox("Очередь задач")
		ql = QtWidgets.QVBoxLayout(queue_group)
		self.queue_list = QtWidgets.QListWidget()
		self.queue_list.setMaximumHeight(120)
		ql.addWidget(self.queue_list)
		self.queue_label = QtWidgets.QLabel("Очередь: 0")
		self.queue_label.setStyleSheet("color:#94a3b8; font-size:12px;")
		ql.addWidget(self.queue_label)
		right_v.addWidget(queue_group)

		# Image generation settings (model selection)
		model_group = QtWidgets.QGroupBox("Параметры генерации изображений")
		model_layout = QtWidgets.QHBoxLayout(model_group)
		model_layout.addWidget(QtWidgets.QLabel("Модель Ideogram:"))
		self.model_combo = QtWidgets.QComboBox()
		self.model_combo.addItems(["3.0 Turbo"]) 
		current_model = self.settings.settings.get("ideogram_model", "3.0 Turbo")
		idx = self.model_combo.findText(current_model)
		self.model_combo.setCurrentIndex(idx if idx >= 0 else 0)
		self.model_combo.currentTextChanged.connect(self._on_model_change)
		model_layout.addWidget(self.model_combo)
		right_v.addWidget(model_group)

		# Левая колонка — Избранные страны + История лендингов
		left_group = QtWidgets.QGroupBox("Быстрый доступ")
		left_layout = QtWidgets.QVBoxLayout(left_group)
		self.last_country_label = QtWidgets.QLabel("")
		self.last_country_label.setStyleSheet("color:#94a3b8; font-size:12px;")
		left_layout.addWidget(self.last_country_label)
		# Избранные страны (компактнее)
		fav_title = QtWidgets.QLabel("Избранные страны")
		fav_title.setStyleSheet("color:#cbd5e1; font-size:12px;")
		left_layout.addWidget(fav_title)
		self.fav_list = QtWidgets.QListWidget()
		self.fav_list.setMaximumHeight(180)
		self.fav_list.itemClicked.connect(self._on_favorite_clicked)
		self.fav_list.itemDoubleClicked.connect(self._on_favorite_double_clicked)
		left_layout.addWidget(self.fav_list)
		# История последних лендингов
		hist_title = QtWidgets.QLabel("Последние 10 лендингов")
		hist_title.setStyleSheet("color:#cbd5e1; font-size:12px; margin-top:6px;")
		left_layout.addWidget(hist_title)
		self.hist_list = QtWidgets.QListWidget()
		self.hist_list.setToolTip("Клик — скопировать промпт в буфер обмена")
		self.hist_list.itemClicked.connect(self._on_history_clicked)
		left_layout.addWidget(self.hist_list)

		# Укладываем две колонки рядом
		right_widget = QtWidgets.QWidget()
		right_widget.setLayout(right_v)
		content = QtWidgets.QHBoxLayout()
		content.setSpacing(12)
		content.addWidget(left_group, 1)
		content.addWidget(right_widget, 3)
		main.addLayout(content)

		# Signals
		self.create_btn.clicked.connect(self._on_create)
		self.reset_prompt_btn.clicked.connect(self._reset_prompt)
		self.edit_prompt_btn.clicked.connect(self._edit_prompt)
		self.update_btn.clicked.connect(self._download_latest_program)
		self.settings_btn.clicked.connect(self._open_settings_dialog)
		self.grid_btn.clicked.connect(self._open_grid_dialog)

		# Применяем ограничения по наличию API ключа
		self._refresh_no_images_state()

	def _download_latest_program(self):
		"""Скачивает готовый LandGen.exe с релиза latest на Рабочий стол."""
		try:
			from pathlib import Path
			import requests
			self.status_label.setText("⬇️ Скачивание LandGen.exe...")
			# Добавляем заголовки, чтобы избежать кешей, и cache-busting параметр
			base = "https://github.com/igorao79/prompthelper/releases/latest/download/LandGen.exe"
			import time
			url = f"{base}?t={int(time.time())}"
			dest_dir = Path(str(get_desktop_path()))
			dest_dir.mkdir(parents=True, exist_ok=True)
			dest = dest_dir / "LandGen.exe"
			def _bg_download():
				try:
					r = requests.get(url, stream=True, timeout=60, headers={"Cache-Control":"no-cache","Pragma":"no-cache","User-Agent":"LandGen-Client"})
					if r.status_code != 200:
						raise RuntimeError(f"HTTP {r.status_code}")
					length = int(r.headers.get("Content-Length", "0") or 0)
					written = 0
					with open(dest, "wb") as f:
						for chunk in r.iter_content(chunk_size=1024 * 64):
							if not chunk:
								continue
							f.write(chunk)
							written += len(chunk)
							if length:
								pct = int(written * 100 / length)
								QtCore.QMetaObject.invokeMethod(
									self.status_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"⬇️ Скачивание LandGen.exe... {pct}%")
								)
					QtCore.QMetaObject.invokeMethod(
						self.status_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, "✅ LandGen.exe сохранён на Рабочем столе")
					)
					QtWidgets.QMessageBox.information(self, "Скачано", f"Файл сохранён: {dest}")
				except Exception as e:
					QtCore.QMetaObject.invokeMethod(
						self.status_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, "⚠️ Ошибка скачивания EXE")
					)
					QtWidgets.QMessageBox.critical(self, "Скачивание", f"Не удалось скачать EXE: {e}")
			worker = QtCore.QThread(self)
			worker.run = _bg_download  # type: ignore
			self._bg_threads.append(worker)
			worker.finished.connect(lambda: self._bg_threads.remove(worker) if worker in self._bg_threads else None)
			worker.start()
		except Exception as e:
			QtWidgets.QMessageBox.critical(self, "Скачивание", f"Не удалось скачать EXE: {e}")
			self.status_label.setText("⚠️ Ошибка скачивания EXE")

	def _on_model_change(self, text: str):
		try:
			self.settings.settings["ideogram_model"] = text.strip()
			self.settings.save_settings()
			self.status_label.setText(f"✅ Модель Ideogram: {text}")
		except Exception:
			pass

	def _init_city(self):
		# Инициализация города при старте
		try:
			country = self.country_combo.currentText().strip()
			if country:
				self._generate_city()
		except Exception:
			pass

	def _check_updates_on_start(self):
		try:
			checker = UpdateChecker(self.settings)
			info = checker.check()
			if info.available:
				res = QtWidgets.QMessageBox.question(
					self,
					"Обновление доступно",
					"Найдены изменения в ветке linux репозитория igorao79/prompthelper. Обновить сейчас?",
					QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
					QtWidgets.QMessageBox.Yes
				)
				if res == QtWidgets.QMessageBox.Yes:
					self._download_and_apply_update(info.latest_sha, info.zip_url)
		except Exception:
			pass

	def _download_and_apply_update(self, latest_sha: str, zip_url: str, binary_url: str | None = None):
		try:
			self.status_label.setText("⬇️ Загружаем последнюю сборку...")
			import requests, io, zipfile
			# Скачиваем готовый EXE с релиза latest, если есть
			try:
				binary = binary_url or f"https://github.com/igorao79/prompthelper/releases/latest/download/LandGen.exe"
				r = requests.get(binary, timeout=60)
				if r.status_code == 200 and r.headers.get('content-type','').lower().find('application') >= 0:
					with open("LandGen.exe", 'wb') as f:
						f.write(r.content)
					self.status_label.setText("✅ Скачан LandGen.exe в папку программы")
					QtWidgets.QMessageBox.information(self, "Скачано", "Скачан LandGen.exe рядом с программой. Откройте папку и запустите.")
					return
			except Exception:
				pass
			else:
				r = requests.get(zip_url, timeout=60)
				r.raise_for_status()
				zf = zipfile.ZipFile(io.BytesIO(r.content))
				root_name = zf.namelist()[0].split('/')[0]
				for n in zf.namelist():
					if not n.endswith('/'):
						rel = n[len(root_name)+1:] if n.startswith(root_name + '/') else n
						if not rel:
							continue
						out_path = Path(rel)
						out_path.parent.mkdir(parents=True, exist_ok=True)
						with zf.open(n) as src, open(out_path, 'wb') as dst:
							dst.write(src.read())
			self.settings.set_last_update_sha(latest_sha)
			QtWidgets.QMessageBox.information(self, "Обновление", "Файлы исходников обновлены. Для EXE используйте кнопку 'Скачать EXE'.")
			self.status_label.setText("✅ Обновление установлено")
		except Exception as e:
			QtWidgets.QMessageBox.critical(self, "Обновление", f"Не удалось обновить: {e}")
			self.status_label.setText("⚠️ Ошибка обновления")

	def _manual_check_updates(self):
		try:
			checker = UpdateChecker(self.settings)
			info = checker.check()
			if info.available:
				self._download_and_apply_update(info.latest_sha, info.zip_url, getattr(info, 'binary_url', None))
			else:
				msg = "Обновлений нет" if not getattr(info, 'message', '') else f"Обновлений нет. {info.message}"
				QtWidgets.QMessageBox.information(self, "Проверка обновлений", msg)
		except Exception as e:
			QtWidgets.QMessageBox.warning(self, "Проверка обновлений", f"Не удалось выполнить проверку: {e}")

	# удалены методы перегенерации изображений

	def _load_initial_state(self):
		# История тематик
		self.theme_combo.clear()
		history = self.settings.get_theme_history()
		if history:
			self.theme_combo.addItems(history)
		# Страны (избранные сверху)
		self._rebuild_country_items()
		# Последняя страна
		last_country = self.settings.get_last_selected_country()
		if last_country and last_country in COUNTRIES_DATA:
			idx = self.country_combo.findText(last_country)
			if idx >= 0:
				self.country_combo.setCurrentIndex(idx)
		self._update_fav_button()
		self._rebuild_favorites_list()
		self._update_last_country_label()

	def _rebuild_favorites_list(self):
		self.fav_list.clear()
		for c in self.settings.get_favorite_countries():
			item = QtWidgets.QListWidgetItem(c)
			if c == self.settings.get_last_selected_country():
				item.setData(QtCore.Qt.UserRole, "last")
				item.setForeground(QtGui.QColor("#22c55e"))
				font = item.font()
				font.setBold(True)
				item.setFont(font)
			self.fav_list.addItem(item)
		# История лендингов
		self.hist_list.clear()
		for e in self.settings.get_landing_history():
			text = e.get("domain", "")
			item = QtWidgets.QListWidgetItem(text)
			item.setData(QtCore.Qt.UserRole, e)
			self.hist_list.addItem(item)

	def _update_last_country_label(self):
		last = self.settings.get_last_selected_country()
		self.last_country_label.setText(f"Последняя страна: {last}" if last else "")

	def _on_favorite_clicked(self, item):
		country = item.text()
		idx = self.country_combo.findText(country)
		if idx >= 0:
			self.country_combo.setCurrentIndex(idx)

	def _on_favorite_double_clicked(self, item):
		self._on_favorite_clicked(item)
		self._generate_city()

	def _on_history_clicked(self, item):
		data = item.data(QtCore.Qt.UserRole)
		prompt = (data or {}).get("prompt", "")
		if not prompt:
			QtWidgets.QMessageBox.information(self, "История", "Промпт недоступен")
			return
		try:
			QtWidgets.QApplication.clipboard().setText(prompt)
			QtWidgets.QMessageBox.information(self, "История", "Промпт скопирован в буфер обмена")
		except Exception:
			QtWidgets.QMessageBox.warning(self, "История", "Не удалось скопировать промпт")

	def _apply_modern_style(self):
		self.setStyleSheet(
			"""
			QWidget { background: #0b1220; color: #f8fafc; font-size: 14px; }
			QLabel { color: #cbd5e1; }
			/* Инпуты более видимые: контрастная рамка и подсветка в фокусе (без box-shadow) */
			QLineEdit, QComboBox, QPlainTextEdit { background: #0b1526; border: 2px solid #1e293b; padding: 10px 12px; border-radius: 10px; color: #f8fafc; }
			QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus { border: 2px solid #2563eb; background: #0d1b2e; }
			QPushButton { background: #475569; border: 0px; padding: 10px 16px; border-radius: 10px; color: #f8fafc; }
			QPushButton:hover { background: #334155; }
			QPushButton#PrimaryButton { background: #2563eb; }
			QPushButton#PrimaryButton:hover { background: #1d4ed8; }
			#StatusLabel { color: #10b981; padding: 8px 6px; }
			/* Подписи к полям ярче */
			QGroupBox { border: 1px solid #1e293b; border-radius: 10px; margin-top: 8px; }
			QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; color: #e2e8f0; }
			"""
		)

	def _refresh_no_images_state(self):
		try:
			has_key = bool(self.settings.get_ideogram_api_key())
			if not has_key:
				self.no_images_checkbox.setChecked(True)
				self.no_images_checkbox.setEnabled(False)
			else:
				self.no_images_checkbox.setEnabled(True)
		except Exception:
			pass

	def _open_settings_dialog(self):
		try:
			dlg = QtWidgets.QDialog(self)
			dlg.setWindowTitle("Настройки")
			layout = QtWidgets.QVBoxLayout(dlg)
			# Ideogram API
			grp_api = QtWidgets.QGroupBox("Ideogram API")
			api_layout = QtWidgets.QHBoxLayout(grp_api)
			api_layout.addWidget(QtWidgets.QLabel("API ключ:"))
			api_edit = QtWidgets.QLineEdit(self.settings.get_ideogram_api_key())
			api_layout.addWidget(api_edit)
			btn_save_api = QtWidgets.QPushButton("Сохранить ключ")
			api_layout.addWidget(btn_save_api)
			layout.addWidget(grp_api)

			# Файл настроек — выбор папки
			grp_file = QtWidgets.QGroupBox("Файл настроек")
			file_layout = QtWidgets.QHBoxLayout(grp_file)
			path_label = QtWidgets.QLineEdit(str(self.settings.settings_file))
			path_label.setReadOnly(True)
			btn_choose = QtWidgets.QPushButton("Выбрать папку")
			file_layout.addWidget(path_label, 1)
			file_layout.addWidget(btn_choose)
			layout.addWidget(grp_file)

			# Cursor поведение
			grp_cursor = QtWidgets.QGroupBox("Cursor")
			cursor_layout = QtWidgets.QVBoxLayout(grp_cursor)
			auto_paste_cb = QtWidgets.QCheckBox("Автоматически вставлять промпт в Cursor")
			auto_paste_cb.setChecked(bool(self.settings.get_auto_paste_prompt()))
			cursor_layout.addWidget(auto_paste_cb)
			layout.addWidget(grp_cursor)

			btns = QtWidgets.QHBoxLayout()
			btn_ok = QtWidgets.QPushButton("Закрыть")
			btns.addStretch(1)
			btns.addWidget(btn_ok)
			layout.addLayout(btns)

			def _save_api():
				self.settings.set_ideogram_api_key(api_edit.text().strip())
				self.status_label.setText("✅ API ключ Ideogram сохранён")
				self._refresh_no_images_state()
			btn_save_api.clicked.connect(_save_api)

			def _choose_dir():
				folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку", str(Path(self.settings.settings_file).parent))
				if folder:
					ok = self.settings.relocate_settings_file(folder)
					if ok:
						path_label.setText(str(self.settings.settings_file))
						self.status_label.setText("✅ Путь к файлу настроек обновлён")
					else:
						QtWidgets.QMessageBox.critical(self, "Ошибка", "Не удалось перенести файл настроек")
			btn_choose.clicked.connect(_choose_dir)

			def _toggle_auto_paste(checked: bool):
				self.settings.set_auto_paste_prompt(bool(checked))
			auto_paste_cb.toggled.connect(_toggle_auto_paste)

			btn_ok.clicked.connect(dlg.accept)
			dlg.exec()
		except Exception as e:
			QtWidgets.QMessageBox.critical(self, "Настройки", f"Не удалось открыть окно настроек: {e}")

	def _browse_path(self):
		path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку", self.path_edit.text())
		if path:
			self.path_edit.setText(path)
			self.settings.set_save_path(path)

	def _reset_to_desktop(self):
		desktop = str(get_desktop_path())
		self.path_edit.setText(desktop)
		self.settings.set_save_path(desktop)

	def _generate_city(self):
		try:
			country = self.country_combo.currentText()
			if not country:
				QtWidgets.QMessageBox.warning(self, "Предупреждение", "Сначала выберите страну!")
				return
			self.city = self.city_generator.get_random_city(country)
			self.status_label.setText(f"🏙️ Город: {self.city}")
		except Exception as e:
			QtWidgets.QMessageBox.warning(self, "Предупреждение", f"Не удалось сгенерировать город: {e}")

	def _on_country_change(self, text):
		self.country = text
		if text:
			self.status_label.setText(f"🌐 Язык: {self._get_effective_language_display(text)}")
			self._generate_city()
			self.settings.set_last_selected_country(text)
		self._update_fav_button()
		self._rebuild_favorites_list()
		self._update_last_country_label()

	def _toggle_favorite_country(self):
		country = self.country_combo.currentText().strip()
		if not country:
			return
		favs = set(self.settings.get_favorite_countries())
		if country in favs:
			self.settings.remove_favorite_country(country)
		else:
			self.settings.add_favorite_country(country)
		self._rebuild_country_items()
		self._update_fav_button()
		self._rebuild_favorites_list()

	def _rebuild_country_items(self):
		current = self.country_combo.currentText()
		favs = self.settings.get_favorite_countries()
		all_countries = list(COUNTRIES_DATA.keys())
		ordered = [c for c in favs if c in all_countries] + [c for c in sorted(all_countries) if c not in favs]
		self.country_combo.blockSignals(True)
		self.country_combo.clear()
		self.country_combo.addItems(ordered)
		self.country_combo.blockSignals(False)
		if current:
			idx = self.country_combo.findText(current)
			if idx >= 0:
				self.country_combo.setCurrentIndex(idx)

	def _update_fav_button(self):
		country = self.country_combo.currentText().strip()
		favs = set(self.settings.get_favorite_countries())
		self.fav_btn.setText("⭐" if country in favs else "☆")

	def _edit_prompt(self):
		country = self.country_combo.currentText().strip()
		theme = self.theme_combo.currentText().strip()
		domain = self.domain_edit.text().strip()
		city = self.city
		if not theme or not country or not domain or not city:
			QtWidgets.QMessageBox.warning(self, "Предупреждение", "Заполните тематику, страну, домен и сгенерируйте город")
			return
		language = self._get_effective_language_code(country)
		prompt = create_landing_prompt(country, city, language, domain, theme)
		text, ok = QtWidgets.QInputDialog.getMultiLineText(self, "Редактирование промпта", "Промпт:", prompt)
		if ok:
			self._custom_prompt = text
			self.settings.save_prompt(text)
			QtWidgets.QMessageBox.information(self, "Готово", "Промпт сохранён")

	def _reset_prompt(self):
		self._custom_prompt = None
		self.settings.save_prompt("")
		QtWidgets.QMessageBox.information(self, "Готово", "Промпт сброшен")

	def _validate(self):
		theme = self.theme_combo.currentText().strip()
		if not theme:
			return False, "Введите тематику"
		country = self.country_combo.currentText().strip()
		if not country:
			return False, "Выберите страну"
		domain = self.domain_edit.text().strip()
		is_valid, error_msg, fixed = validate_domain(domain)
		if not is_valid:
			return False, error_msg
		if fixed != domain:
			self.domain_edit.setText(fixed)
		self.theme = theme
		self.country = country
		self.domain = fixed
		return True, ""

	def _on_create(self):
		ok, msg = self._validate()
		if not ok:
			QtWidgets.QMessageBox.critical(self, "Ошибка", msg)
			return
		# Если нет API ключа — не разрешаем снимать "без изображений"
		try:
			if not self.settings.get_ideogram_api_key() and not self.no_images_checkbox.isChecked():
				QtWidgets.QMessageBox.warning(self, "Требуется API ключ", "Введите Ideogram API ключ в настройках или включите режим 'Без изображений'.")
				return
		except Exception:
			pass
		language_display = self._get_effective_language_display(self.country) if self.country else ""
		res = QtWidgets.QMessageBox.question(
			self,
			"Подтверждение",
			f"Создать лендинг?\n\nТематика: {self.theme}\nСтрана: {self.country}\nГород: {self.city}\nЯзык: {language_display}\nДомен: {self.domain}\nПапка: {self.path_edit.text()}\n\nИзображения будут сгенерированы автоматически, если включено и задан API ключ."
		)
		if res != QtWidgets.QMessageBox.Yes:
			return
		# Добавляем задачу в очередь; обработчик сам подхватит до 5 параллельно
		self._enqueue_build()

	def _create_landing(self):
		# Создание в фоне через очередь, чтобы ограничить параллелизм
		self._start_build_task()

	def _enqueue_build(self):
		params = {
			"save_path": self.path_edit.text(),
			"country": self.country,
			"theme": self.theme,
			"domain": self.domain,
			"city": self._pick_next_city(self.country),
			"custom_prompt": getattr(self, "_custom_prompt", None),
			"no_images": self.no_images_checkbox.isChecked(),
			"language": self._get_effective_language_code(self.country) if self.country else get_language_by_country(self.country),
			"id": self._job_seq,
			"auto_paste": bool(self.settings.get_auto_paste_prompt()),
		}
		self._job_seq += 1
		self._build_queue.append(params)
		self._refresh_queue_ui()
		self._start_build_task()

		# Обновляем счётчик очереди
		self._update_queue_label()

	def _pick_next_city(self, country: str) -> str:
		# Выбираем город, избегая повторения подряд для одной страны
		try:
			last = self._last_city_by_country.get(country, "")
			city = self.city_generator.get_random_city(country)
			# если совпал — пробуем ещё раз 1-2 попытки
			for _ in range(2):
				if city != last and city:
					break
				city = self.city_generator.get_random_city(country)
			self._last_city_by_country[country] = city
			return city
		except Exception:
			return self.city or ""

	def _start_build_task(self):
		if self._active_builds >= self.max_parallel:
			return
		if not self._build_queue:
			return
		params = self._build_queue.pop(0)
		self._active_builds += 1
		self._active_jobs.append(params)
		self.status_label.setText("🚧 Создание проекта и изображений...")

		def task():
			try:
				zip_path = ensure_empty_zip_for_landing(params["save_path"], params["country"], params["theme"])
				if zip_path:
					print(f"ZIP создан: {zip_path}")
				def progress_cb(text: str):
					QtCore.QMetaObject.invokeMethod(
						self.status_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, text)
					)
				# Генерация изображений возможна только при наличии API ключа
				should_gen_images = (not params.get("no_images", False)) and bool(self.settings.get_ideogram_api_key())
				# Папка проекта может отличаться от домена, если в сетке указаны дубли доменов
				project_folder = params.get("folder_name", params["domain"])
				project_path, media_path = self.cursor_manager.create_project_structure(
					project_folder, params["save_path"], params["theme"], progress_cb, generate_images=should_gen_images
				)
				# Виджет пути перегенерации был удалён; больше не обновляем
				language = params.get("language") or get_language_by_country(params["country"]) 
				prompt = params.get("custom_prompt") or create_landing_prompt(params["country"], params["city"], language, params["domain"], params["theme"])
				# Для грид-режима ничего не вставляем и не копируем; признак origin == 'grid'
				origin = params.get("origin", "single")
				do_copy = origin != "grid"
				do_auto_paste = bool(params.get("auto_paste", False)) and origin != "grid"
				if do_copy:
					try:
						QtWidgets.QApplication.clipboard().setText(prompt)
					except Exception:
						pass
				success, message = self.cursor_manager.open_project_and_paste_prompt(
					project_path, prompt, None, auto_paste=do_auto_paste
				)
				QtCore.QMetaObject.invokeMethod(
					self, "_show_create_done", QtCore.Qt.QueuedConnection,
					QtCore.Q_ARG(str, f"Проект: {project_path}\nMedia: {media_path}\n{message}"),
					QtCore.Q_ARG(str, prompt),
					QtCore.Q_ARG(str, params["domain"]),
					QtCore.Q_ARG(str, params["theme"]) 
				)
			except Exception as e:
				QtCore.QMetaObject.invokeMethod(
					self, "_show_create_error", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, str(e))
				)
			finally:
				QtCore.QMetaObject.invokeMethod(self, "_on_build_finished", QtCore.Qt.QueuedConnection)

		worker = QtCore.QThread(self)
		worker.run = task  # type: ignore
		self._bg_threads.append(worker)
		worker.finished.connect(lambda: self._bg_threads.remove(worker) if worker in self._bg_threads else None)
		worker.start()

	@QtCore.Slot()
	def _on_build_finished(self):
		self._active_builds = max(0, self._active_builds - 1)
		if self._active_jobs:
			self._active_jobs.pop(0)
		self._refresh_queue_ui()
		self._update_queue_label()
		if self._build_queue:
			self._start_build_task()

	def _refresh_queue_ui(self):
		items = []
		for p in self._active_jobs:
			items.append(f"▶ {p['id']}: {p['domain']} [{p['theme']}] {'(без изображений)' if p.get('no_images') else ''}")
		for p in self._build_queue:
			items.append(f"⏳ {p['id']}: {p['domain']} [{p['theme']}] {'(без изображений)' if p.get('no_images') else ''}")
		self.queue_list.clear()
		self.queue_list.addItems(items)

	def _update_queue_label(self):
		try:
			q_total = len(self._active_jobs) + len(self._build_queue)
			self.queue_label.setText(f"Очередь: {q_total}")
		except Exception:
			pass

	def _open_grid_dialog(self):
		try:
			dlg = QtWidgets.QDialog(self)
			dlg.setWindowTitle("Режим генерации сетки (5)")
			# Делаем окно немодальным, чтобы главное окно можно было перемещать
			dlg.setWindowModality(QtCore.Qt.NonModal)
			dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
			v = QtWidgets.QVBoxLayout(dlg)
			# Выбор страны в диалоге
			country_row = QtWidgets.QHBoxLayout()
			label_country = QtWidgets.QLabel("Страна:")
			label_country.setStyleSheet("color:#e2e8f0;font-weight:600;")
			country_row.addWidget(label_country)
			country_combo = QtWidgets.QComboBox()
			# Избранные страны приоритетно сверху
			favs = self.settings.get_favorite_countries()
			all_countries = list(COUNTRIES_DATA.keys())
			favorites = [c for c in favs if c in all_countries]
			others = [c for c in sorted(all_countries) if c not in favs]
			country_combo.addItem("— выберите страну —")
			if favorites:
				country_combo.addItem("— Избранные —")
				for c in favorites:
					country_combo.addItem(f"★ {c}")
				country_combo.insertSeparator(country_combo.count())
			country_combo.addItem("— Все страны —")
			for c in others:
				country_combo.addItem(c)
			# Стили для визуального отделения
			country_combo.setStyleSheet("QComboBox{font-weight:600;} QAbstractItemView::item{padding:6px;} ")
			# Не выбираем автоматически. Если ранее пользователь уже выбирал — восстановим
			if hasattr(self, "_grid_last_country") and self._grid_last_country:
				idx = country_combo.findText(self._grid_last_country)
				if idx >= 0:
					country_combo.setCurrentIndex(idx)
			country_row.addWidget(country_combo, 1)
			v.addLayout(country_row)
			# Две многострочные области: тематики и домены
			inputs = QtWidgets.QHBoxLayout()
			left_box = QtWidgets.QGroupBox("Тематики (каждая с новой строки)")
			left_v = QtWidgets.QVBoxLayout(left_box)
			themes_text = QtWidgets.QPlainTextEdit()
			# Длинные тематики визуально переносятся, но логически остаются одной строкой
			themes_text.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
			themes_text.setPlaceholderText("Автомойка\nПолировка и детейлинг авто\nАвтосервис и ремонт машин\nШиномонтаж\nЗамена масла")
			left_v.addWidget(themes_text)
			right_box = QtWidgets.QGroupBox("Домены (каждый с новой строки)")
			right_v = QtWidgets.QVBoxLayout(right_box)
			domains_text = QtWidgets.QPlainTextEdit()
			domains_text.setPlaceholderText("familykedx.org\nfrankjgoh.org\npuccinyomf.org\ncuekuth.org\nblockbzore.org")
			right_v.addWidget(domains_text)
			inputs.addWidget(left_box, 1)
			inputs.addWidget(right_box, 1)
			v.addLayout(inputs)
			# Низ: опции
			bottom = QtWidgets.QHBoxLayout()
			custom_lang_cb = QtWidgets.QCheckBox("Нестандартный язык")
			custom_lang_cb.setChecked(self.custom_lang_cb.isChecked())
			lang_combo = QtWidgets.QComboBox()
			lang_combo.addItems(["en","ru","uk","be","kk","de","fr","it","es","pl","cs","tr","zh","ja","ko","hi","pt"])
			lang_combo.setCurrentText(self.custom_lang_combo.currentText())
			no_images_cb = QtWidgets.QCheckBox("Без изображений")
			no_images_cb.setChecked(self.no_images_checkbox.isChecked() or not bool(self.settings.get_ideogram_api_key()))
			if not self.settings.get_ideogram_api_key():
				no_images_cb.setEnabled(False)
			bottom.addWidget(custom_lang_cb)
			bottom.addWidget(lang_combo)
			bottom.addStretch(1)
			bottom.addWidget(no_images_cb)
			v.addLayout(bottom)

			btns = QtWidgets.QHBoxLayout()
			start_btn = QtWidgets.QPushButton("Запустить очередь")
			btns.addStretch(1)
			btns.addWidget(start_btn)
			v.addLayout(btns)

			def _start():
				country = country_combo.currentText().strip()
				if not country:
					QtWidgets.QMessageBox.warning(self, "Предупреждение", "Выберите страну")
					return
				# Сохраняем выбранную страну для следующих запусков диалога
				self._grid_last_country = country
				save_path = self.path_edit.text().strip()
				# Разбираем списки
				themes = [s.strip() for s in themes_text.toPlainText().splitlines() if s.strip()]
				domains = [s.strip() for s in domains_text.toPlainText().splitlines() if s.strip()]
				# Поддержка одной тематики на несколько доменов (и наоборот)
				pairs = []
				if len(themes) == 1 and len(domains) > 1:
					base_theme = themes[0]
					# Если домены совпадают (дубликаты) — создаём разные папки с индексами
					counts = {}
					for d in domains:
						key = d
						counts[key] = counts.get(key, 0) + 1
						folder = d if counts[key] == 1 else f"{d}_{counts[key]}"
						pairs.append((base_theme, d, folder))
				elif len(domains) == 1 and len(themes) > 1:
					base_domain = domains[0]
					for idx, t in enumerate(themes, start=1):
						folder = f"{base_domain}_{idx}"
						pairs.append((t, base_domain, folder))
				else:
					for t, d in zip(themes, domains):
						pairs.append((t, d, d))
				if not pairs:
					QtWidgets.QMessageBox.warning(self, "Режим сетки", "Заполните тематики и домены")
					return
				for theme, domain, folder_name in pairs:
					ok, err, fixed = validate_domain(domain)
					if not ok:
						self.status_label.setText(f"⚠️ Пропуск '{domain}': {err}")
						continue
					params = {
						"save_path": save_path,
						"country": country,
						"theme": theme,
						"domain": fixed,
						"folder_name": folder_name,
						"city": self._pick_next_city(country),
						"custom_prompt": getattr(self, "_custom_prompt", None),
						"no_images": bool(no_images_cb.isChecked()),
						"language": (lang_combo.currentText().strip() if custom_lang_cb.isChecked() else self._get_effective_language_code(country)),
						"id": self._job_seq,
						"auto_paste": False,
						"origin": "grid"
					}
					self._job_seq += 1
					self._build_queue.append(params)
				self._refresh_queue_ui()
				self._start_build_task()
				self._update_queue_label()
				dlg.accept()

			start_btn.clicked.connect(_start)
			# Храним ссылку, чтобы диалог не был уничтожен сборщиком мусора
			self._grid_dialog = dlg
			dlg.show()
		except Exception as e:
			QtWidgets.QMessageBox.critical(self, "Режим сетки", f"Не удалось открыть окно: {e}")

	def _on_custom_lang_toggle(self, checked: bool):
		try:
			self.custom_lang_combo.setEnabled(bool(checked))
			country = self.country_combo.currentText().strip()
			if country:
				self.status_label.setText(f"🌐 Язык: {self._get_effective_language_display(country)}")
		except Exception:
			pass

	def _on_custom_lang_changed(self, text: str):
		try:
			country = self.country_combo.currentText().strip()
			if country:
				self.status_label.setText(f"🌐 Язык: {self._get_effective_language_display(country)}")
		except Exception:
			pass

	def _get_effective_language_code(self, country: str) -> str:
		try:
			if hasattr(self, 'custom_lang_cb') and self.custom_lang_cb.isChecked():
				code = (self.custom_lang_combo.currentText() or 'en').strip()
				return code
			return get_language_by_country(country)
		except Exception:
			return get_language_by_country(country)

	def _get_effective_language_display(self, country: str) -> str:
		code = self._get_effective_language_code(country)
		name = self._language_code_to_display.get(code, code)
		return name if not (hasattr(self, 'custom_lang_cb') and self.custom_lang_cb.isChecked()) else f"{name} (переопределён)"

	@QtCore.Slot(str, str, str, str)
	def _show_create_done(self, message: str, prompt: str, domain: str, theme: str):
		QtWidgets.QMessageBox.information(self, "Готово", message)
		# сохранение истории — для многопоточности фиксируем текущее состояние домена/темы
		try:
			self.settings.add_theme_to_history(theme)
			self.settings.add_landing_to_history(domain, prompt)
		except Exception:
			pass
		self._load_initial_state()
		self.status_label.setText("✅ Готов к работе")

	@QtCore.Slot(str)
	def _show_create_error(self, message: str):
		QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось создать проект: {message}")
		self.status_label.setText("⚠️ Ошибка создания проекта")


def run_qt():
	app = QtWidgets.QApplication([])
	# Splash (лаунчер)
	pix = QtGui.QPixmap(480, 240)
	pix.fill(QtGui.QColor("#0b1220"))
	splash = QtWidgets.QSplashScreen(pix)
	splash.showMessage("Загрузка PromptHelper...", QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom, QtGui.QColor("#f8fafc"))
	splash.show()
	app.processEvents()

	w = QtMainWindow()

	def _finish():
		w.show()
		splash.finish(w)

	QtCore.QTimer.singleShot(700, _finish)
	app.exec()
