from PySide6 import QtWidgets, QtGui, QtCore
from pathlib import Path

from shared.settings_manager import SettingsManager, get_desktop_path
from shared.helpers import validate_domain, get_language_by_country, get_language_display_name, check_directory_exists, ensure_empty_zip_for_landing
from shared.city_generator import CityGenerator
from shared.data import COUNTRIES_DATA
from core.cursor_manager import CursorManager
from generators.prompt_generator import create_landing_prompt


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
		self._build_ui()
		self._apply_modern_style()
		self._load_initial_state()
		self._init_city()
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
		self.create_btn = QtWidgets.QPushButton("🚀 СОЗДАТЬ ЛЕНДИНГ ✨")
		self.create_btn.setObjectName("PrimaryButton")
		header.addWidget(self.edit_prompt_btn)
		header.addWidget(self.reset_prompt_btn)
		header.addStretch(1)
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

		# Domain
		self.domain_edit = QtWidgets.QLineEdit()
		form.addWidget(QtWidgets.QLabel("Домен"), row, 0)
		form.addWidget(self.domain_edit, row, 1, 1, 2)
		row += 1

		# Правая колонка (форма + статус + инструменты)
		right_v = QtWidgets.QVBoxLayout()
		right_v.setSpacing(10)
		right_v.addLayout(form)

		# Status bar (custom)
		self.status_label = QtWidgets.QLabel("✅ Готов к работе")
		self.status_label.setObjectName("StatusLabel")
		right_v.addWidget(self.status_label)

		# Image regeneration (compact tools)
		regen_group = QtWidgets.QGroupBox("Перегенерация изображений")
		regen_layout = QtWidgets.QVBoxLayout(regen_group)
		path_row = QtWidgets.QHBoxLayout()
		self.regen_path_edit = QtWidgets.QLineEdit(self.settings.get_save_path())
		self.regen_path_edit.setPlaceholderText("Укажите папку проекта или media")
		self.regen_browse_btn = QtWidgets.QPushButton("📂 Выбрать папку")
		self.regen_browse_btn.clicked.connect(self._browse_regen_path)
		path_row.addWidget(self.regen_path_edit)
		path_row.addWidget(self.regen_browse_btn)
		regen_layout.addLayout(path_row)

		btn_row = QtWidgets.QHBoxLayout()
		self.regen_all_btn = QtWidgets.QPushButton("🔁 Перегенерировать все (8)")
		self.regen_all_btn.clicked.connect(self._regenerate_all_images)
		btn_row.addWidget(self.regen_all_btn)
		regen_layout.addLayout(btn_row)

		grid = QtWidgets.QGridLayout()
		image_names = [
			("main", "Main"), ("about1", "About 1"), ("about2", "About 2"), ("about3", "About 3"),
			("review1", "Review 1"), ("review2", "Review 2"), ("review3", "Review 3"), ("favicon", "Favicon")
		]
		self._image_buttons = {}
		for i, (iname, label) in enumerate(image_names):
			btn = QtWidgets.QPushButton(label)
			btn.clicked.connect(lambda _, n=iname: self._regenerate_single_image(n))
			self._image_buttons[iname] = btn
			grid.addWidget(btn, i // 4, i % 4)
		regen_layout.addLayout(grid)

		right_v.addWidget(regen_group)

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

	def _browse_regen_path(self):
		path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку проекта или media", self.path_edit.text())
		if path:
			self.regen_path_edit.setText(path)

	def _init_city(self):
		# Инициализация города при старте
		try:
			country = self.country_combo.currentText().strip()
			if country:
				self._generate_city()
		except Exception:
			pass

	def _resolve_media_path(self):
		p = self.regen_path_edit.text().strip()
		if not p:
			return None
		pp = Path(p)
		if pp.is_dir() and pp.name.lower() == 'media':
			return pp
		if pp.is_dir():
			# если это папка проекта — используем project/media
			cand = pp / 'media'
			return cand if cand.exists() else None
		return None

	def _regenerate_all_images(self):
		media = self._resolve_media_path()
		if not media:
			QtWidgets.QMessageBox.warning(self, "Перегенерация", "Укажите корректную папку проекта или media")
			return
		# Запускаем в фоне, UI не блокируется
		self.status_label.setText("🚧 Перегенерация: подготовка...")
		def task():
			try:
				from generators.image_generator import ImageGenerator
				gen = ImageGenerator(silent_mode=False, fast_mode=False, max_workers=2)
				def cb(text):
					QtCore.QMetaObject.invokeMethod(
						self.status_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, text)
					)
				count = gen.generate_thematic_set(self.theme_combo.currentText().strip() or self.theme, str(media), progress_callback=cb)
				QtCore.QMetaObject.invokeMethod(
					self, "_show_regen_result", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"Готово: {count}/8")
				)
			except Exception as e:
				QtCore.QMetaObject.invokeMethod(
					self, "_show_regen_error", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, str(e))
				)
		worker = QtCore.QThread(self)
		worker.run = task  # type: ignore
		self._bg_threads.append(worker)
		worker.finished.connect(lambda: self._bg_threads.remove(worker) if worker in self._bg_threads else None)
		worker.start()

	def _regenerate_single_image(self, image_name):
		media = self._resolve_media_path()
		if not media:
			QtWidgets.QMessageBox.warning(self, "Перегенерация", "Укажите корректную папку проекта или media")
			return
		# В фоне, без блокировки UI
		self.status_label.setText(f"🚧 Перегенерация: {image_name}...")
		def task():
			try:
				from generators.image_generator import ImageGenerator
				gen = ImageGenerator(silent_mode=False, fast_mode=False, max_workers=1)
				prompt_map, _ = gen._generate_prompts(self.theme_combo.currentText().strip() or self.theme)
				from time import perf_counter
				start = perf_counter()
				res = gen._generate_image_pollinations_aggressive(prompt_map.get(image_name, ''), image_name, str(media))
				elapsed = perf_counter() - start
				msg = f"{image_name}: готово за {elapsed:.1f}s" if res else f"{image_name}: не удалось"
				QtCore.QMetaObject.invokeMethod(
					self, "_show_regen_result", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, msg)
				)
			except Exception as e:
				QtCore.QMetaObject.invokeMethod(
					self, "_show_regen_error", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, str(e))
				)
		worker = QtCore.QThread(self)
		worker.run = task  # type: ignore
		self._bg_threads.append(worker)
		worker.finished.connect(lambda: self._bg_threads.remove(worker) if worker in self._bg_threads else None)
		worker.start()

	@QtCore.Slot(str)
	def _show_regen_result(self, msg: str):
		QtWidgets.QMessageBox.information(self, "Перегенерация", msg)

	@QtCore.Slot(str)
	def _show_regen_error(self, msg: str):
		QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось перегенерировать: {msg}")

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
			QLineEdit, QComboBox { background: #0b1526; border: 0px; padding: 10px 12px; border-radius: 8px; color: #f8fafc; }
			QPushButton { background: #475569; border: 0px; padding: 10px 16px; border-radius: 8px; color: #f8fafc; }
			QPushButton:hover { background: #334155; }
			QPushButton#PrimaryButton { background: #2563eb; }
			QPushButton#PrimaryButton:hover { background: #1d4ed8; }
			#StatusLabel { color: #10b981; padding: 8px 6px; }
			"""
		)

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
			self.status_label.setText(f"🌐 Язык: {get_language_display_name(text)}")
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
		language = get_language_by_country(country)
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
		res = QtWidgets.QMessageBox.question(
			self,
			"Подтверждение",
			f"Создать лендинг?\n\nТематика: {self.theme}\nСтрана: {self.country}\nГород: {self.city}\nДомен: {self.domain}\nПапка: {self.path_edit.text()}\n\nИзображения будут сгенерированы автоматически."
		)
		if res != QtWidgets.QMessageBox.Yes:
			return
		self._create_landing()

	def _create_landing(self):
		# Создание в фоне, чтобы UI не зависал
		self.status_label.setText("🚧 Создание проекта и изображений...")
		def task():
			try:
				zip_path = ensure_empty_zip_for_landing(self.path_edit.text(), self.country, self.theme)
				if zip_path:
					print(f"ZIP создан: {zip_path}")
				def progress_cb(text: str):
					QtCore.QMetaObject.invokeMethod(
						self.status_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, text)
					)
				project_path, media_path = self.cursor_manager.create_project_structure(
					self.domain, self.path_edit.text(), self.theme, progress_cb, generate_images=True
				)
				# автоподстановка пути проекта для перегенерации
				QtCore.QMetaObject.invokeMethod(
					self.regen_path_edit, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, str(project_path))
				)
				language = get_language_by_country(self.country)
				prompt = getattr(self, "_custom_prompt", None) or create_landing_prompt(self.country, self.city, language, self.domain, self.theme)
				try:
					QtWidgets.QApplication.clipboard().setText(prompt)
				except Exception:
					pass
				success, message = self.cursor_manager.open_project_and_paste_prompt(project_path, prompt, None, auto_paste=False)
				QtCore.QMetaObject.invokeMethod(
					self, "_show_create_done", QtCore.Qt.QueuedConnection,
					QtCore.Q_ARG(str, f"Проект: {project_path}\nMedia: {media_path}\n{message}"),
					QtCore.Q_ARG(str, prompt)
				)
			except Exception as e:
				QtCore.QMetaObject.invokeMethod(
					self, "_show_create_error", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, str(e))
				)
		worker = QtCore.QThread(self)
		worker.run = task  # type: ignore
		self._bg_threads.append(worker)
		worker.finished.connect(lambda: self._bg_threads.remove(worker) if worker in self._bg_threads else None)
		worker.start()

	@QtCore.Slot(str, str)
	def _show_create_done(self, message: str, prompt: str):
		QtWidgets.QMessageBox.information(self, "Готово", message)
		# сохранение истории
		self.settings.add_theme_to_history(self.theme)
		self.settings.add_landing_to_history(self.domain, prompt)
		self._load_initial_state()
		self.status_label.setText("✅ Готов к работе")

	@QtCore.Slot(str)
	def _show_create_error(self, message: str):
		QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось создать проект: {message}")
		self.status_label.setText("⚠️ Ошибка создания проекта")


def run_qt():
	app = QtWidgets.QApplication([])
	w = QtMainWindow()
	w.show()
	app.exec()
