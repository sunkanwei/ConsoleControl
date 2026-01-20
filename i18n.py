# 多语言支持，根据Blender语言设置自动切换

import bpy

TRANSLATIONS = {
    "zh_HANS": {
        "Toggle Console": "切换控制台",
        "Reset to Default": "重置为默认",
        "Keymap": "快捷键",
        "Width": "宽度",
        "Height": "高度",
        "Always On Top": "置顶",
        "Auto Open On Startup": "启动时自动打开",
        "Opacity": "不透明度",
        "Language": "语言",
    },
    "en": {
        "Toggle Console": "Toggle Console",
        "Reset to Default": "Reset to Default",
        "Keymap": "Keymap",
        "Width": "Width",
        "Height": "Height",
        "Always On Top": "Always On Top",
        "Auto Open On Startup": "Auto Open On Startup",
        "Opacity": "Opacity",
        "Language": "Language",
    },
    "zh_HANT": {
        "Toggle Console": "切換控制台",
        "Reset to Default": "重設為預設",
        "Keymap": "快捷鍵",
        "Width": "寬度",
        "Height": "高度",
        "Always On Top": "置頂",
        "Auto Open On Startup": "啟動時自動開啟",
        "Opacity": "不透明度",
        "Language": "語言",
    },
    "ja_JP": {
        "Toggle Console": "コンソール切替",
        "Reset to Default": "デフォルトにリセット",
        "Keymap": "キーマップ",
        "Width": "幅",
        "Height": "高さ",
        "Always On Top": "常に最前面",
        "Auto Open On Startup": "起動時に自動で開く",
        "Opacity": "不透明度",
        "Language": "言語",
    },
    "ko_KR": {
        "Toggle Console": "콘솔 전환",
        "Reset to Default": "기본값으로 재설정",
        "Keymap": "단축키",
        "Width": "너비",
        "Height": "높이",
        "Always On Top": "항상 위에",
        "Auto Open On Startup": "시작 시 자동 열기",
        "Opacity": "불투명도",
        "Language": "언어",
    },
    "fr_FR": {
        "Toggle Console": "Basculer la console",
        "Reset to Default": "Réinitialiser par défaut",
        "Keymap": "Raccourcis",
        "Width": "Largeur",
        "Height": "Hauteur",
        "Always On Top": "Toujours au premier plan",
        "Auto Open On Startup": "Ouvrir automatiquement au démarrage",
        "Opacity": "Opacité",
        "Language": "Langue",
    },
    "de_DE": {
        "Toggle Console": "Konsole umschalten",
        "Reset to Default": "Auf Standard zurücksetzen",
        "Keymap": "Tastenkürzel",
        "Width": "Breite",
        "Height": "Höhe",
        "Always On Top": "Immer im Vordergrund",
        "Auto Open On Startup": "Beim Start automatisch öffnen",
        "Opacity": "Deckkraft",
        "Language": "Sprache",
    },
    "es": {
        "Toggle Console": "Alternar consola",
        "Reset to Default": "Restablecer valores predeterminados",
        "Keymap": "Atajos de teclado",
        "Width": "Ancho",
        "Height": "Alto",
        "Always On Top": "Siempre visible",
        "Auto Open On Startup": "Abrir automáticamente al iniciar",
        "Opacity": "Opacidad",
        "Language": "Idioma",
    },
    "pt_BR": {
        "Toggle Console": "Alternar console",
        "Reset to Default": "Redefinir para padrão",
        "Keymap": "Atalhos",
        "Width": "Largura",
        "Height": "Altura",
        "Always On Top": "Sempre no topo",
        "Auto Open On Startup": "Abrir automaticamente ao iniciar",
        "Opacity": "Opacidade",
        "Language": "Idioma",
    },
    "ru_RU": {
        "Toggle Console": "Переключить консоль",
        "Reset to Default": "Сбросить по умолчанию",
        "Keymap": "Горячие клавиши",
        "Width": "Ширина",
        "Height": "Высота",
        "Always On Top": "Поверх всех окон",
        "Auto Open On Startup": "Открывать при запуске",
        "Opacity": "Непрозрачность",
        "Language": "Язык",
    },
    "it_IT": {
        "Toggle Console": "Attiva/Disattiva console",
        "Reset to Default": "Ripristina predefiniti",
        "Keymap": "Scorciatoie",
        "Width": "Larghezza",
        "Height": "Altezza",
        "Always On Top": "Sempre in primo piano",
        "Auto Open On Startup": "Apri automaticamente all'avvio",
        "Opacity": "Opacità",
        "Language": "Lingua",
    },
    "nl_NL": {
        "Toggle Console": "Console wisselen",
        "Reset to Default": "Standaardwaarden herstellen",
        "Keymap": "Sneltoetsen",
        "Width": "Breedte",
        "Height": "Hoogte",
        "Always On Top": "Altijd bovenaan",
        "Auto Open On Startup": "Automatisch openen bij opstarten",
        "Opacity": "Dekking",
        "Language": "Taal",
    },
    "pl_PL": {
        "Toggle Console": "Przełącz konsolę",
        "Reset to Default": "Przywróć domyślne",
        "Keymap": "Skróty klawiszowe",
        "Width": "Szerokość",
        "Height": "Wysokość",
        "Always On Top": "Zawsze na wierzchu",
        "Auto Open On Startup": "Otwórz automatycznie przy starcie",
        "Opacity": "Krycie",
        "Language": "Język",
    },
    "tr_TR": {
        "Toggle Console": "Konsolu Aç/Kapat",
        "Reset to Default": "Varsayılana Sıfırla",
        "Keymap": "Kısayol Tuşları",
        "Width": "Genişlik",
        "Height": "Yükseklik",
        "Always On Top": "Her Zaman Üstte",
        "Auto Open On Startup": "Başlangıçta Otomatik Aç",
        "Opacity": "Opaklık",
        "Language": "Dil",
    },
    "ar_AR": {
        "Toggle Console": "تبديل وحدة التحكم",
        "Reset to Default": "إعادة التعيين إلى الافتراضي",
        "Keymap": "اختصارات لوحة المفاتيح",
        "Width": "العرض",
        "Height": "الارتفاع",
        "Always On Top": "دائماً في المقدمة",
        "Auto Open On Startup": "فتح تلقائي عند بدء التشغيل",
        "Opacity": "الشفافية",
        "Language": "اللغة",
    },
    "uk_UA": {
        "Toggle Console": "Перемкнути консоль",
        "Reset to Default": "Скинути до стандартних",
        "Keymap": "Гарячі клавіші",
        "Width": "Ширина",
        "Height": "Висота",
        "Always On Top": "Завжди зверху",
        "Auto Open On Startup": "Відкривати при запуску",
        "Opacity": "Непрозорість",
        "Language": "Мова",
    },
    "vi_VN": {
        "Toggle Console": "Bật/Tắt bảng điều khiển",
        "Reset to Default": "Đặt lại mặc định",
        "Keymap": "Phím tắt",
        "Width": "Chiều rộng",
        "Height": "Chiều cao",
        "Always On Top": "Luôn ở trên cùng",
        "Auto Open On Startup": "Tự động mở khi khởi động",
        "Opacity": "Độ mờ",
        "Language": "Ngôn ngữ",
    },
    "id_ID": {
        "Toggle Console": "Beralih Konsol",
        "Reset to Default": "Atur Ulang ke Default",
        "Keymap": "Pintasan Keyboard",
        "Width": "Lebar",
        "Height": "Tinggi",
        "Always On Top": "Selalu di Atas",
        "Auto Open On Startup": "Buka Otomatis Saat Memulai",
        "Opacity": "Opasitas",
        "Language": "Bahasa",
    },
}

_LANG_DISPLAY_NAMES = {
    "AUTO": "Auto",
    "zh_HANS": "简体中文",
    "en": "English",
    "zh_HANT": "繁體中文",
    "ja_JP": "日本語",
    "ko_KR": "한국어",
    "fr_FR": "Français",
    "de_DE": "Deutsch",
    "es": "Español",
    "pt_BR": "Português (Brasil)",
    "ru_RU": "Русский",
    "it_IT": "Italiano",
    "nl_NL": "Nederlands",
    "pl_PL": "Polski",
    "tr_TR": "Türkçe",
    "ar_AR": "العربية",
    "uk_UA": "Українська",
    "vi_VN": "Tiếng Việt",
    "id_ID": "Bahasa Indonesia",
}


# 从Blender偏好获取系统语言
def _get_system_language():
    lang = bpy.context.preferences.view.language
    if lang.startswith("zh_CN") or lang.startswith("zh_HANS"):
        return "zh_HANS"
    if lang.startswith("zh_TW") or lang.startswith("zh_HANT"):
        return "zh_HANT"
    if lang.startswith("ja"):
        return "ja_JP"
    if lang.startswith("ko"):
        return "ko_KR"
    if lang.startswith("fr"):
        return "fr_FR"
    if lang.startswith("de"):
        return "de_DE"
    if lang.startswith("es"):
        return "es"
    if lang.startswith("pt"):
        return "pt_BR"
    if lang.startswith("ru"):
        return "ru_RU"
    if lang.startswith("it"):
        return "it_IT"
    if lang.startswith("nl"):
        return "nl_NL"
    if lang.startswith("pl"):
        return "pl_PL"
    if lang.startswith("tr"):
        return "tr_TR"
    if lang.startswith("ar"):
        return "ar_AR"
    if lang.startswith("uk"):
        return "uk_UA"
    if lang.startswith("vi"):
        return "vi_VN"
    if lang.startswith("id"):
        return "id_ID"
    return "en"


def _get_current_language():
    try:
        prefs = bpy.context.preferences.addons[__package__].preferences
        lang = getattr(prefs, "language", "AUTO")
        if lang == "AUTO":
            return _get_system_language()
        return lang
    except (KeyError, AttributeError):
        return _get_system_language()


def get_text(key: str) -> str:
    lang = _get_current_language()
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


def get_language_items(self, context):
    return [(code, name, "") for code, name in _LANG_DISPLAY_NAMES.items()]
