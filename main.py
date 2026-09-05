# ============================================================
# UNIVERSAL POS / KASIR ANDROID
# ============================================================
# Stable Android version
# Based on repository:
# https://github.com/lilsoki666/pos-kasir-android-v01
#
# Main improvements:
# - Database initialized BEFORE UI
# - Safe SQLite handling
# - Safer transaction processing
# - Payment validation
# - Transaction snapshot before clearing cart
# - Android-safe database path
# - No external image/Pillow dependency
# ============================================================

import os
import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import platform


# ============================================================
# CONSTANTS
# ============================================================

APP_NAME = "UniversalPOS"

PRIMARY = (0.15, 0.65, 0.60, 1)
PRIMARY_DARK = (0.10, 0.48, 0.45, 1)

WHITE = (1, 1, 1, 1)
TEXT = (0.15, 0.16, 0.18, 1)
TEXT_LIGHT = (0.50, 0.52, 0.55, 1)

BG = (0.94, 0.95, 0.97, 1)
CARD = (1, 1, 1, 1)
SOFT = (0.85, 0.87, 0.90, 1)

DANGER = (0.88, 0.25, 0.25, 1)
WARNING = (0.95, 0.60, 0.15, 1)

CATEGORIES = [
    "Semua",
    "Makanan",
    "Minuman",
    "Snack",
    "Lainnya",
]

PAYMENT_METHODS = [
    "TUNAI",
    "QRIS",
    "DEBIT",
    "KREDIT",
    "TRANSFER",
    "E-WALLET",
]


# ============================================================
# DATABASE
# ============================================================

def get_db():
    """
    Return SQLite connection.

    Android:
        /data/user/0/<package>/files/pos_kasir.db

    Desktop:
        current directory / pos_kasir.db
    """

    app = App.get_running_app()

    if app is not None and hasattr(app, "user_data_dir"):
        db_dir = app.user_data_dir
    else:
        db_dir = os.path.abspath(".")

    os.makedirs(db_dir, exist_ok=True)

    db_path = os.path.join(
        db_dir,
        "pos_kasir.db"
    )

    conn = sqlite3.connect(
        db_path,
        timeout=10
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_db():
    """
    Create all required database tables.

    This MUST run before KasirScreen is created.
    """

    conn = get_db()

    try:

        cursor = conn.cursor()

        # ----------------------------------------------------
        # MENU / PRODUCTS
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                kategori TEXT NOT NULL DEFAULT 'Lainnya',
                harga INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        # ----------------------------------------------------
        # TRANSACTIONS
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                faktur TEXT NOT NULL UNIQUE,
                tanggal TEXT NOT NULL,
                total INTEGER NOT NULL DEFAULT 0,
                bayar INTEGER NOT NULL DEFAULT 0,
                kembali INTEGER NOT NULL DEFAULT 0,
                pembayaran TEXT NOT NULL DEFAULT 'TUNAI',
                catatan TEXT DEFAULT ''
            )
            """
        )

        # ----------------------------------------------------
        # TRANSACTION DETAILS
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS detail_transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                faktur TEXT NOT NULL,
                menu_id INTEGER NOT NULL,
                nama TEXT NOT NULL,
                harga INTEGER NOT NULL DEFAULT 0,
                jumlah INTEGER NOT NULL DEFAULT 1,
                subtotal INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        # ----------------------------------------------------
        # DATABASE MIGRATION
        # ----------------------------------------------------

        cursor.execute(
            "PRAGMA table_info(transaksi)"
        )

        columns = [
            row[1]
            for row in cursor.fetchall()
        ]

        if "pembayaran" not in columns:

            cursor.execute(
                """
                ALTER TABLE transaksi
                ADD COLUMN pembayaran
                TEXT DEFAULT 'TUNAI'
                """
            )

        if "catatan" not in columns:

            cursor.execute(
                """
                ALTER TABLE transaksi
                ADD COLUMN catatan
                TEXT DEFAULT ''
                """
            )

        # ----------------------------------------------------
        # SAMPLE PRODUCTS
        # ----------------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) FROM menu"
        )

        total_products = cursor.fetchone()[0]

        if total_products == 0:

            sample_menu = [
                (
                    "Kopi Hitam",
                    "Minuman",
                    10000
                ),
                (
                    "Es Teh Manis",
                    "Minuman",
                    5000
                ),
                (
                    "Nasi Goreng",
                    "Makanan",
                    15000
                ),
                (
                    "Mie Goreng",
                    "Makanan",
                    12000
                ),
                (
                    "Roti Bakar",
                    "Snack",
                    10000
                ),
                (
                    "Kentang Goreng",
                    "Snack",
                    12000
                ),
            ]

            cursor.executemany(
                """
                INSERT INTO menu
                (nama, kategori, harga)
                VALUES (?, ?, ?)
                """,
                sample_menu
            )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


# ============================================================
# HELPERS
# ============================================================

def format_rupiah(value):
    try:
        value = int(value)
    except Exception:
        value = 0

    return "Rp {:,}".format(value).replace(",", ".")


def safe_int(value, default=0):

    try:
        return int(value)

    except (
        ValueError,
        TypeError
    ):
        return default


def make_invoice_number():

    now = datetime.now()

    return (
        "TRX-"
        + now.strftime("%Y%m%d%H%M%S")
        + "-"
        + now.strftime("%f")[:4]
    )


# ============================================================
# ROUNDED BUTTON
# ============================================================

class RoundedButton(Button):

    def __init__(
        self,
        bg_color=PRIMARY,
        radius=10,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.bg_color = bg_color
        self.radius = radius

        self.background_color = (
            0,
            0,
            0,
            0
        )

        self.bind(
            pos=self.update_canvas,
            size=self.update_canvas
        )

    def update_canvas(
        self,
        *args
    ):

        self.canvas.before.clear()

        with self.canvas.before:

            Color(
                *self.bg_color
            )

            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[
                    dp(self.radius)
                ]
            )


# ============================================================
# ROUNDED BOX
# ============================================================

class RoundedBox(BoxLayout):

    def __init__(
        self,
        bg_color=CARD,
        radius=10,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.bg_color = bg_color
        self.radius = radius

        self.bind(
            pos=self.update_canvas,
            size=self.update_canvas
        )

    def update_canvas(
        self,
        *args
    ):

        self.canvas.before.clear()

        with self.canvas.before:

            Color(
                *self.bg_color
            )

            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[
                    dp(self.radius)
                ]
            )


# ============================================================
# POPUP
# ============================================================

class CustomPopup(Popup):

    def __init__(
        self,
        title_text,
        content_widget,
        size_hint=(0.88, 0.82),
        **kwargs
    ):

        super().__init__(
            **kwargs
        )

        self.title = ""

        self.separator_height = 0

        self.size_hint = size_hint

        self.background = ""

        self.background_color = (
            0,
            0,
            0,
            0
        )

        main_box = RoundedBox(
            orientation="vertical",
            bg_color=BG,
            radius=15,
            padding=dp(12),
            spacing=dp(8)
        )

        header = RoundedBox(
            size_hint_y=None,
            height=dp(45),
            bg_color=PRIMARY,
            radius=10,
            padding=[
                dp(12),
                0
            ]
        )

        title_label = Label(
            text=title_text,
            font_size=dp(16),
            bold=True,
            color=WHITE,
            halign="left",
            valign="middle"
        )

        title_label.bind(
            size=title_label.setter(
                "text_size"
            )
        )

        header.add_widget(
            title_label
        )

        close_btn = Button(
            text="×",
            size_hint=(
                None,
                None
            ),
            size=(
                dp(35),
                dp(35)
            ),
            background_color=(
                0,
                0,
                0,
                0
            ),
            color=WHITE,
            font_size=dp(20),
            bold=True,
            pos_hint={
                "center_y": 0.5
            }
        )

        close_btn.bind(
            on_release=self.dismiss
        )

        header.add_widget(
            close_btn
        )

        main_box.add_widget(
            header
        )

        main_box.add_widget(
            content_widget
        )

        self.content = main_box


# ============================================================
# MESSAGE POPUP
# ============================================================

def show_message(
    title,
    message
):

    content = BoxLayout(
        orientation="vertical",
        spacing=dp(10),
        padding=dp(10)
    )

    label = Label(
        text=message,
        color=TEXT,
        halign="center",
        valign="middle"
    )

    label.bind(
        size=label.setter(
            "text_size"
        )
    )

    content.add_widget(
        label
    )

    button = RoundedButton(
        text="OK",
        size_hint_y=None,
        height=dp(42),
        bg_color=PRIMARY,
        color=WHITE
    )

    content.add_widget(
        button
    )

    popup = CustomPopup(
        title,
        content,
        size_hint=(
            0.80,
            0.45
        )
    )

    button.bind(
        on_release=popup.dismiss
    )

    popup.open()


# ============================================================
# MENU MANAGEMENT
# ============================================================

class MenuManagementWidget(
    BoxLayout
):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(
            **kwargs
        )

        self.orientation = "vertical"

        self.spacing = dp(8)

        self.selected_kategori = "Makanan"

        # ----------------------------------------------------
        # FORM
        # ----------------------------------------------------

        form = RoundedBox(
            orientation="vertical",
            spacing=dp(7),
            size_hint_y=None,
            height=dp(190),
            bg_color=CARD,
            radius=10,
            padding=dp(10)
        )

        self.txt_nama = TextInput(
            hint_text="Nama Produk",
            multiline=False,
            size_hint_y=None,
            height=dp(38)
        )

        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        category_box = BoxLayout(
            size_hint_y=None,
            height=dp(38),
            spacing=dp(5)
        )

        self.btn_category = RoundedButton(
            text="Kategori: Makanan",
            bg_color=SOFT,
            color=TEXT,
            radius=6
        )

        self.dropdown = DropDown()

        for category in CATEGORIES[1:]:

            btn = Button(
                text=category,
                size_hint_y=None,
                height=dp(38),
                background_normal="",
                background_color=SOFT,
                color=TEXT
            )

            btn.bind(
                on_release=lambda button,
                value=category:
                self.select_category(
                    value
                )
            )

            self.dropdown.add_widget(
                btn
            )

        self.btn_category.bind(
            on_release=self.dropdown.open
        )

        category_box.add_widget(
            self.btn_category
        )

        # ----------------------------------------------------
        # PRICE
        # ----------------------------------------------------

        self.txt_harga = TextInput(
            hint_text="Harga (Rp)",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(38)
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        save_button = RoundedButton(
            text="Tambah Produk",
            size_hint_y=None,
            height=dp(40),
            bg_color=PRIMARY,
            color=WHITE,
            bold=True
        )

        save_button.bind(
            on_release=self.tambah_menu
        )

        form.add_widget(
            self.txt_nama
        )

        form.add_widget(
            category_box
        )

        form.add_widget(
            self.txt_harga
        )

        form.add_widget(
            save_button
        )

        self.add_widget(
            form
        )

        # ----------------------------------------------------
        # PRODUCT LIST
        # ----------------------------------------------------

        scroll = ScrollView()

        self.grid_menu = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=[
                0,
                dp(5)
            ]
        )

        self.grid_menu.bind(
            minimum_height=
            self.grid_menu.setter(
                "height"
            )
        )

        scroll.add_widget(
            self.grid_menu
        )

        self.add_widget(
            scroll
        )

        self.load_menu_list()

    def select_category(
        self,
        category
    ):

        self.selected_kategori = category

        self.btn_category.text = (
            "Kategori: "
            + category
        )

        self.dropdown.dismiss()

    def tambah_menu(
        self,
        instance
    ):

        nama = (
            self.txt_nama.text
            .strip()
        )

        harga_text = (
            self.txt_harga.text
            .strip()
        )

        if not nama:

            show_message(
                "Produk",
                "Nama produk belum diisi."
            )

            return

        if not harga_text:

            show_message(
                "Produk",
                "Harga produk belum diisi."
            )

            return

        harga = safe_int(
            harga_text
        )

        if harga <= 0:

            show_message(
                "Produk",
                "Harga harus lebih besar dari 0."
            )

            return

        conn = None

        try:

            conn = get_db()

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO menu
                (nama, kategori, harga)
                VALUES (?, ?, ?)
                """,
                (
                    nama,
                    self.selected_kategori,
                    harga
                )
            )

            conn.commit()

        except Exception as error:

            if conn:
                conn.rollback()

            show_message(
                "Database",
                "Gagal menyimpan produk:\n"
                + str(error)
            )

            return

        finally:

            if conn:
                conn.close()

        self.txt_nama.text = ""

        self.txt_harga.text = ""

        self.load_menu_list()

        app = App.get_running_app()

        if hasattr(
            app,
            "kasir_screen"
        ):

            app.kasir_screen.load_menu()

    def load_menu_list(
        self
    ):

        self.grid_menu.clear_widgets()

        conn = get_db()

        try:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM menu
                ORDER BY id DESC
                """
            )

            products = cursor.fetchall()

        finally:

            conn.close()

        for product in products:

            row = RoundedBox(
                size_hint_y=None,
                height=dp(55),
                bg_color=CARD,
                radius=8,
                padding=dp(8),
                spacing=dp(5)
            )

            info = BoxLayout(
                orientation="vertical"
            )

            name = Label(
                text="[b]"
                + str(product["nama"])
                + "[/b]",
                markup=True,
                color=TEXT,
                font_size=dp(13),
                halign="left",
                valign="middle"
            )

            name.bind(
                size=name.setter(
                    "text_size"
                )
            )

            detail = Label(
                text=(
                    str(product["kategori"])
                    + " • "
                    + format_rupiah(
                        product["harga"]
                    )
                ),
                color=TEXT_LIGHT,
                font_size=dp(10),
                halign="left",
                valign="middle"
            )

            detail.bind(
                size=detail.setter(
                    "text_size"
                )
            )

            info.add_widget(
                name
            )

            info.add_widget(
                detail
            )

            delete_button = RoundedButton(
                text="Hapus",
                size_hint=(
                    None,
                    None
                ),
                size=(
                    dp(60),
                    dp(34)
                ),
                bg_color=DANGER,
                color=WHITE,
                font_size=dp(10),
                pos_hint={
                    "center_y": 0.5
                }
            )

            delete_button.bind(
                on_release=lambda button,
                product_id=product["id"]:
                self.hapus_menu(
                    product_id
                )
            )

            row.add_widget(
                info
            )

            row.add_widget(
                delete_button
            )

            self.grid_menu.add_widget(
                row
            )

    def hapus_menu(
        self,
        menu_id
    ):

        conn = get_db()

        try:

            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM menu
                WHERE id = ?
                """,
                (
                    menu_id,
                )
            )

            conn.commit()

        finally:

            conn.close()

        self.load_menu_list()

        app = App.get_running_app()

        if hasattr(
            app,
            "kasir_screen"
        ):

            app.kasir_screen.load_menu()


# ============================================================
# HISTORY
# ============================================================

class RiwayatWidget(
    BoxLayout
):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(
            **kwargs
        )

        self.orientation = "vertical"

        scroll = ScrollView()

        self.grid = GridLayout(
            cols=1,
            spacing=dp(7),
            size_hint_y=None,
            padding=[
                0,
                dp(5)
            ]
        )

        self.grid.bind(
            minimum_height=
            self.grid.setter(
                "height"
            )
        )

        scroll.add_widget(
            self.grid
        )

        self.add_widget(
            scroll
        )

        self.load_history()

    def load_history(
        self
    ):

        self.grid.clear_widgets()

        conn = get_db()

        try:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM transaksi
                ORDER BY id DESC
                """
            )

            transactions = cursor.fetchall()

        finally:

            conn.close()

        for transaction in transactions:

            row = RoundedBox(
                orientation="vertical",
                size_hint_y=None,
                height=dp(72),
                bg_color=CARD,
                radius=8,
                padding=dp(8),
                spacing=dp(2)
            )

            top = BoxLayout()

            invoice = Label(
                text=(
                    "[b]"
                    + str(
                        transaction["faktur"]
                    )
                    + "[/b]"
                ),
                markup=True,
                color=TEXT,
                halign="left"
            )

            invoice.bind(
                size=invoice.setter(
                    "text_size"
                )
            )

            total = Label(
                text=format_rupiah(
                    transaction["total"]
                ),
                color=PRIMARY,
                bold=True,
                halign="right"
            )

            total.bind(
                size=total.setter(
                    "text_size"
                )
            )

            top.add_widget(
                invoice
            )

            top.add_widget(
                total
            )

            bottom = BoxLayout()

            method = (
                transaction["pembayaran"]
                or "TUNAI"
            )

            detail = Label(
                text=(
                    str(
                        transaction["tanggal"]
                    )
                    + " • "
                    + str(method)
                ),
                color=TEXT_LIGHT,
                font_size=dp(10),
                halign="left"
            )

            detail.bind(
                size=detail.setter(
                    "text_size"
                )
            )

            detail_button = RoundedButton(
                text="Detail",
                size_hint=(
                    None,
                    None
                ),
                size=(
                    dp(60),
                    dp(28)
                ),
                bg_color=SOFT,
                color=TEXT,
                font_size=dp(10)
            )

            detail_button.bind(
                on_release=lambda button,
                invoice_number=transaction[
                    "faktur"
                ]:
                self.show_detail(
                    invoice_number
                )
            )

            bottom.add_widget(
                detail
            )

            bottom.add_widget(
                detail_button
            )

            row.add_widget(
                top
            )

            row.add_widget(
                bottom
            )

            self.grid.add_widget(
                row
            )

    def show_detail(
        self,
        faktur
    ):

        conn = get_db()

        try:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM transaksi
                WHERE faktur = ?
                """,
                (
                    faktur,
                )
            )

            transaction = cursor.fetchone()

            cursor.execute(
                """
                SELECT *
                FROM detail_transaksi
                WHERE faktur = ?
                ORDER BY id
                """,
                (
                    faktur,
                )
            )

            details = cursor.fetchall()

        finally:

            conn.close()

        if not transaction:

            return

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(7)
        )

        info = (
            "Faktur: "
            + str(transaction["faktur"])
            + "\n"
            + "Tanggal: "
            + str(transaction["tanggal"])
            + "\n"
            + "Metode: "
            + str(transaction["pembayaran"])
        )

        if transaction["catatan"]:

            info += (
                "\nCatatan: "
                + str(
                    transaction["catatan"]
                )
            )

        info_label = Label(
            text=info,
            color=TEXT,
            size_hint_y=None,
            height=dp(65),
            halign="left",
            valign="top"
        )

        info_label.bind(
            size=info_label.setter(
                "text_size"
            )
        )

        content.add_widget(
            info_label
        )

        scroll = ScrollView()

        grid = GridLayout(
            cols=1,
            spacing=dp(4),
            size_hint_y=None
        )

        grid.bind(
            minimum_height=
            grid.setter(
                "height"
            )
        )

        for item in details:

            row = BoxLayout(
                size_hint_y=None,
                height=dp(28)
            )

            left = Label(
                text=(
                    str(item["nama"])
                    + " x"
                    + str(item["jumlah"])
                ),
                color=TEXT,
                halign="left"
            )

            right = Label(
                text=format_rupiah(
                    item["subtotal"]
                ),
                color=TEXT,
                halign="right"
            )

            left.bind(
                size=left.setter(
                    "text_size"
                )
            )

            right.bind(
                size=right.setter(
                    "text_size"
                )
            )

            row.add_widget(
                left
            )

            row.add_widget(
                right
            )

            grid.add_widget(
                row
            )

        scroll.add_widget(
            grid
        )

        content.add_widget(
            scroll
        )

        summary = (
            "Total: "
            + format_rupiah(
                transaction["total"]
            )
            + "\n"
            + "Bayar: "
            + format_rupiah(
                transaction["bayar"]
            )
            + "\n"
            + "Kembali: "
            + format_rupiah(
                transaction["kembali"]
            )
        )

        summary_label = Label(
            text=summary,
            color=PRIMARY,
            bold=True,
            size_hint_y=None,
            height=dp(65),
            halign="right"
        )

        summary_label.bind(
            size=summary_label.setter(
                "text_size"
            )
        )

        content.add_widget(
            summary_label
        )

        popup = CustomPopup(
            "Detail Transaksi",
            content,
            size_hint=(
                0.90,
                0.80
            )
        )

        popup.open()


# ============================================================
# REPORT
# ============================================================

class LaporanWidget(
    BoxLayout
):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(
            **kwargs
        )

        self.orientation = "vertical"

        self.spacing = dp(8)

        self.summary = Label(
            text="Memuat laporan...",
            markup=True,
            color=TEXT,
            size_hint_y=None,
            height=dp(120),
            halign="left",
            valign="top"
        )

        self.summary.bind(
            size=self.summary.setter(
                "text_size"
            )
        )

        summary_box = RoundedBox(
            orientation="vertical",
            bg_color=CARD,
            radius=10,
            padding=dp(10),
            size_hint_y=None,
            height=dp(130)
        )

        summary_box.add_widget(
            self.summary
        )

        self.add_widget(
            summary_box
        )

        title = Label(
            text="[b]Produk Terlaris[/b]",
            markup=True,
            color=TEXT,
            size_hint_y=None,
            height=dp(28),
            halign="left"
        )

        title.bind(
            size=title.setter(
                "text_size"
            )
        )

        self.add_widget(
            title
        )

        scroll = ScrollView()

        self.grid = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None
        )

        self.grid.bind(
            minimum_height=
            self.grid.setter(
                "height"
            )
        )

        scroll.add_widget(
            self.grid
        )

        self.add_widget(
            scroll
        )

        self.load_report()

    def load_report(
        self
    ):

        conn = get_db()

        try:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    COUNT(*),
                    COALESCE(SUM(total), 0)
                FROM transaksi
                """
            )

            overall = cursor.fetchone()

            total_transactions = (
                overall[0] or 0
            )

            total_sales = (
                overall[1] or 0
            )

            today = datetime.now().strftime(
                "%Y-%m-%d"
            )

            cursor.execute(
                """
                SELECT
                    COUNT(*),
                    COALESCE(SUM(total), 0)
                FROM transaksi
                WHERE tanggal LIKE ?
                """,
                (
                    today + "%",
                )
            )

            today_data = cursor.fetchone()

            today_transactions = (
                today_data[0] or 0
            )

            today_sales = (
                today_data[1] or 0
            )

            cursor.execute(
                """
                SELECT
                    nama,
                    SUM(jumlah) AS qty,
                    SUM(subtotal) AS total
                FROM detail_transaksi
                GROUP BY nama
                ORDER BY qty DESC
                LIMIT 10
                """
            )

            best_sellers = cursor.fetchall()

        finally:

            conn.close()

        self.summary.text = (
            "[b]Hari Ini[/b]\n"
            + "Transaksi: "
            + str(today_transactions)
            + "\n"
            + "Omset: "
            + format_rupiah(
                today_sales
            )
            + "\n\n"
            + "[b]Keseluruhan[/b]\n"
            + "Transaksi: "
            + str(total_transactions)
            + "\n"
            + "Omset: "
            + format_rupiah(
                total_sales
            )
        )

        self.grid.clear_widgets()

        for index, item in enumerate(
            best_sellers,
            start=1
        ):

            row = RoundedBox(
                size_hint_y=None,
                height=dp(42),
                bg_color=CARD,
                radius=8,
                padding=dp(8)
            )

            name = Label(
                text=(
                    str(index)
                    + ". "
                    + str(item["nama"])
                ),
                color=TEXT,
                halign="left"
            )

            name.bind(
                size=name.setter(
                    "text_size"
                )
            )

            value = Label(
                text=(
                    str(item["qty"])
                    + " item • "
                    + format_rupiah(
                        item["total"]
                    )
                ),
                color=PRIMARY,
                bold=True,
                halign="right"
            )

            value.bind(
                size=value.setter(
                    "text_size"
                )
            )

            row.add_widget(
                name
            )

            row.add_widget(
                value
            )

            self.grid.add_widget(
                row
            )


# ============================================================
# CASHIER SCREEN
# ============================================================

class KasirScreen(
    Screen
):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(
            **kwargs
        )

        self.cart = {}

        self.kategori_aktif = "Semua"

        self.build_ui()

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def build_ui(
        self
    ):

        main = BoxLayout(
            orientation="vertical"
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = RoundedBox(
            size_hint_y=None,
            height=dp(55),
            bg_color=PRIMARY,
            radius=0,
            padding=[
                dp(10),
                0
            ],
            spacing=dp(5)
        )

        title = Label(
            text="UniversalPOS",
            color=WHITE,
            bold=True,
            font_size=dp(17),
            halign="left",
            valign="middle"
        )

        title.bind(
            size=title.setter(
                "text_size"
            )
        )

        header.add_widget(
            title
        )

        menu_button = RoundedButton(
            text="Produk",
            size_hint=(
                None,
                None
            ),
            size=(
                dp(68),
                dp(32)
            ),
            bg_color=PRIMARY_DARK,
            color=WHITE,
            font_size=dp(10)
        )

        menu_button.bind(
            on_release=
            self.open_menu_management
        )

        header.add_widget(
            menu_button
        )

        history_button = RoundedButton(
            text="Riwayat",
            size_hint=(
                None,
                None
            ),
            size=(
                dp(65),
                dp(32)
            ),
            bg_color=PRIMARY_DARK,
            color=WHITE,
            font_size=dp(10)
        )

        history_button.bind(
            on_release=
            self.open_riwayat
        )

        header.add_widget(
            history_button
        )

        report_button = RoundedButton(
            text="Laporan",
            size_hint=(
                None,
                None
            ),
            size=(
                dp(68),
                dp(32)
            ),
            bg_color=PRIMARY_DARK,
            color=WHITE,
            font_size=dp(10)
        )

        report_button.bind(
            on_release=
            self.open_laporan
        )

        header.add_widget(
            report_button
        )

        main.add_widget(
            header
        )

        # ----------------------------------------------------
        # CONTENT
        # ----------------------------------------------------

        content = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            padding=dp(8)
        )

        # ----------------------------------------------------
        # PRODUCTS
        # ----------------------------------------------------

        left = BoxLayout(
            orientation="vertical",
            spacing=dp(7)
        )

        category_bar = BoxLayout(
            size_hint_y=None,
            height=dp(38),
            spacing=dp(4)
        )

        self.category_buttons = {}

        for category in CATEGORIES:

            button = RoundedButton(
                text=category,
                bg_color=(
                    PRIMARY
                    if category == "Semua"
                    else SOFT
                ),
                color=(
                    WHITE
                    if category == "Semua"
                    else TEXT
                ),
                font_size=dp(10),
                radius=7
            )

            button.bind(
                on_release=lambda instance,
                value=category:
                self.filter_category(
                    value
                )
            )

            self.category_buttons[
                category
            ] = button

            category_bar.add_widget(
                button
            )

        left.add_widget(
            category_bar
        )

        product_scroll = ScrollView()

        self.grid_products = GridLayout(
            cols=2,
            spacing=dp(7),
            size_hint_y=None
        )

        self.grid_products.bind(
            minimum_height=
            self.grid_products.setter(
                "height"
            )
        )

        product_scroll.add_widget(
            self.grid_products
        )

        left.add_widget(
            product_scroll
        )

        # ----------------------------------------------------
        # CART
        # ----------------------------------------------------

        right = RoundedBox(
            orientation="vertical",
            bg_color=CARD,
            radius=12,
            padding=dp(8),
            spacing=dp(7),
            size_hint_x=0.45
        )

        cart_title = Label(
            text="[b]Pesanan[/b]",
            markup=True,
            color=TEXT,
            size_hint_y=None,
            height=dp(28),
            halign="left"
        )

        cart_title.bind(
            size=cart_title.setter(
                "text_size"
            )
        )

        right.add_widget(
            cart_title
        )

        cart_scroll = ScrollView()

        self.grid_cart = GridLayout(
            cols=1,
            spacing=dp(4),
            size_hint_y=None
        )

        self.grid_cart.bind(
            minimum_height=
            self.grid_cart.setter(
                "height"
            )
        )

        cart_scroll.add_widget(
            self.grid_cart
        )

        right.add_widget(
            cart_scroll
        )

        total_box = BoxLayout(
            size_hint_y=None,
            height=dp(35)
        )

        total_label = Label(
            text="TOTAL",
            color=TEXT,
            bold=True,
            halign="left"
        )

        total_label.bind(
            size=total_label.setter(
                "text_size"
            )
        )

        self.total_value = Label(
            text="Rp 0",
            color=PRIMARY,
            bold=True,
            font_size=dp(15),
            halign="right"
        )

        self.total_value.bind(
            size=self.total_value.setter(
                "text_size"
            )
        )

        total_box.add_widget(
            total_label
        )

        total_box.add_widget(
            self.total_value
        )

        right.add_widget(
            total_box
        )

        pay_button = RoundedButton(
            text="BAYAR",
            size_hint_y=None,
            height=dp(44),
            bg_color=PRIMARY,
            color=WHITE,
            bold=True,
            font_size=dp(14)
        )

        pay_button.bind(
            on_release=
            self.open_payment
        )

        right.add_widget(
            pay_button
        )

        content.add_widget(
            left
        )

        content.add_widget(
            right
        )

        main.add_widget(
            content
        )

        self.add_widget(
            main
        )

    # --------------------------------------------------------
    # SCREEN ENTER
    # --------------------------------------------------------

    def on_enter(
        self
    ):

        self.load_menu()

        self.update_cart_ui()

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    def filter_category(
        self,
        category
    ):

        self.kategori_aktif = category

        for name, button in (
            self.category_buttons.items()
        ):

            if name == category:

                button.bg_color = PRIMARY
                button.color = WHITE

            else:

                button.bg_color = SOFT
                button.color = TEXT

            button.update_canvas()

        self.load_menu()

    # --------------------------------------------------------
    # LOAD PRODUCTS
    # --------------------------------------------------------

    def load_menu(
        self
    ):

        self.grid_products.clear_widgets()

        conn = get_db()

        try:

            cursor = conn.cursor()

            if self.kategori_aktif == "Semua":

                cursor.execute(
                    """
                    SELECT *
                    FROM menu
                    ORDER BY nama
                    """
                )

            else:

                cursor.execute(
                    """
                    SELECT *
                    FROM menu
                    WHERE kategori = ?
                    ORDER BY nama
                    """,
                    (
                        self.kategori_aktif,
                    )
                )

            products = cursor.fetchall()

        finally:

            conn.close()

        for product in products:

            card = RoundedBox(
                orientation="vertical",
                size_hint_y=None,
                height=dp(72),
                bg_color=CARD,
                radius=9,
                padding=dp(7),
                spacing=dp(2)
            )

            name = Label(
                text=(
                    "[b]"
                    + str(product["nama"])
                    + "[/b]"
                ),
                markup=True,
                color=TEXT,
                font_size=dp(11),
                halign="left",
                valign="top"
            )

            name.bind(
                size=name.setter(
                    "text_size"
                )
            )

            price = Label(
                text=format_rupiah(
                    product["harga"]
                ),
                color=PRIMARY,
                bold=True,
                font_size=dp(11),
                halign="left",
                valign="bottom"
            )

            price.bind(
                size=price.setter(
                    "text_size"
                )
            )

            card.add_widget(
                name
            )

            card.add_widget(
                price
            )

            card.bind(
                on_touch_down=lambda instance,
                touch,
                item=product:
                self.product_touch(
                    instance,
                    touch,
                    item
                )
            )

            self.grid_products.add_widget(
                card
            )

    def product_touch(
        self,
        instance,
        touch,
        item
    ):

        if instance.collide_point(
            *touch.pos
        ):

            self.add_to_cart(
                item
            )

            return True

        return False

    # --------------------------------------------------------
    # CART
    # --------------------------------------------------------

    def add_to_cart(
        self,
        item
    ):

        item_id = item["id"]

        if item_id in self.cart:

            self.cart[item_id][
                "jumlah"
            ] += 1

        else:

            self.cart[item_id] = {
                "nama": item["nama"],
                "harga": item["harga"],
                "jumlah": 1
            }

        self.update_cart_ui()

    def change_qty(
        self,
        item_id,
        delta
    ):

        if item_id not in self.cart:

            return

        self.cart[item_id][
            "jumlah"
        ] += delta

        if self.cart[item_id][
            "jumlah"
        ] <= 0:

            del self.cart[
                item_id
            ]

        self.update_cart_ui()

    def get_total(
        self
    ):

        return sum(
            item["harga"]
            * item["jumlah"]
            for item in self.cart.values()
        )

    def update_cart_ui(
        self
    ):

        self.grid_cart.clear_widgets()

        total = 0

        for item_id, item in (
            self.cart.items()
        ):

            subtotal = (
                item["harga"]
                * item["jumlah"]
            )

            total += subtotal

            row = BoxLayout(
                size_hint_y=None,
                height=dp(40),
                spacing=dp(3)
            )

            info = BoxLayout(
                orientation="vertical"
            )

            name = Label(
                text=str(
                    item["nama"]
                ),
                color=TEXT,
                font_size=dp(10),
                halign="left"
            )

            name.bind(
                size=name.setter(
                    "text_size"
                )
            )

            subtotal_label = Label(
                text=format_rupiah(
                    subtotal
                ),
                color=TEXT_LIGHT,
                font_size=dp(9),
                halign="left"
            )

            subtotal_label.bind(
                size=subtotal_label.setter(
                    "text_size"
                )
            )

            info.add_widget(
                name
            )

            info.add_widget(
                subtotal_label
            )

            quantity = BoxLayout(
                size_hint_x=None,
                width=dp(75),
                spacing=dp(2)
            )

            minus = RoundedButton(
                text="-",
                bg_color=SOFT,
                color=TEXT,
                radius=4
            )

            minus.bind(
                on_release=lambda instance,
                item_id=item_id:
                self.change_qty(
                    item_id,
                    -1
                )
            )

            quantity_label = Label(
                text=str(
                    item["jumlah"]
                ),
                color=TEXT
            )

            plus = RoundedButton(
                text="+",
                bg_color=SOFT,
                color=TEXT,
                radius=4
            )

            plus.bind(
                on_release=lambda instance,
                item_id=item_id:
                self.change_qty(
                    item_id,
                    1
                )
            )

            quantity.add_widget(
                minus
            )

            quantity.add_widget(
                quantity_label
            )

            quantity.add_widget(
                plus
            )

            row.add_widget(
                info
            )

            row.add_widget(
                quantity
            )

            self.grid_cart.add_widget(
                row
            )

        self.total_value.text = (
            format_rupiah(
                total
            )
        )

    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

    def open_payment(
        self,
        instance
    ):

        if not self.cart:

            show_message(
                "Pembayaran",
                "Keranjang masih kosong."
            )

            return

        total = self.get_total()

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(8)
        )

        total_label = Label(
            text=(
                "[b]Total: "
                + format_rupiah(total)
                + "[/b]"
            ),
            markup=True,
            color=PRIMARY,
            font_size=dp(16),
            size_hint_y=None,
            height=dp(35)
        )

        content.add_widget(
            total_label
        )

        method_label = Label(
            text="Metode Pembayaran",
            color=TEXT,
            size_hint_y=None,
            height=dp(22),
            halign="left"
        )

        method_label.bind(
            size=method_label.setter(
                "text_size"
            )
        )

        content.add_widget(
            method_label
        )

        self.selected_method = "TUNAI"

        method_scroll = ScrollView(
            size_hint_y=None,
            height=dp(42),
            do_scroll_y=False
        )

        method_box = BoxLayout(
            size_hint_x=None,
            width=dp(
                90
                * len(
                    PAYMENT_METHODS
                )
            ),
            spacing=dp(4)
        )

        self.payment_buttons = {}

        for method in PAYMENT_METHODS:

            button = RoundedButton(
                text=method,
                size_hint_x=None,
                width=dp(85),
                bg_color=(
                    PRIMARY
                    if method == "TUNAI"
                    else SOFT
                ),
                color=(
                    WHITE
                    if method == "TUNAI"
                    else TEXT
                ),
                font_size=dp(9),
                radius=6
            )

            button.bind(
                on_release=lambda instance,
                value=method:
                self.select_payment(
                    value
                )
            )

            self.payment_buttons[
                method
            ] = button

            method_box.add_widget(
                button
            )

        method_scroll.add_widget(
            method_box
        )

        content.add_widget(
            method_scroll
        )

        self.txt_bayar = TextInput(
            hint_text="Nominal pembayaran",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(40)
        )

        content.add_widget(
            self.txt_bayar
        )

        quick = BoxLayout(
            size_hint_y=None,
            height=dp(35),
            spacing=dp(4)
        )

        quick_values = [
            (
                "Uang Pas",
                total
            ),
            (
                "50.000",
                50000
            ),
            (
                "100.000",
                100000
            )
        ]

        for label, value in quick_values:

            button = RoundedButton(
                text=label,
                bg_color=SOFT,
                color=TEXT,
                font_size=dp(9),
                radius=5
            )

            button.bind(
                on_release=lambda instance,
                amount=value:
                self.set_payment_amount(
                    amount
                )
            )

            quick.add_widget(
                button
            )

        content.add_widget(
            quick
        )

        self.txt_catatan = TextInput(
            hint_text="Catatan transaksi (opsional)",
            multiline=False,
            size_hint_y=None,
            height=dp(38)
        )

        content.add_widget(
            self.txt_catatan
        )

        process_button = RoundedButton(
            text="PROSES TRANSAKSI",
            size_hint_y=None,
            height=dp(44),
            bg_color=PRIMARY,
            color=WHITE,
            bold=True
        )

        process_button.bind(
            on_release=
            self.process_transaction
        )

        content.add_widget(
            process_button
        )

        self.payment_popup = CustomPopup(
            "Pembayaran",
            content,
            size_hint=(
                0.92,
                0.80
            )
        )

        self.payment_popup.open()

    def select_payment(
        self,
        method
    ):

        self.selected_method = method

        for name, button in (
            self.payment_buttons.items()
        ):

            if name == method:

                button.bg_color = PRIMARY
                button.color = WHITE

            else:

                button.bg_color = SOFT
                button.color = TEXT

            button.update_canvas()

    def set_payment_amount(
        self,
        amount
    ):

        self.txt_bayar.text = str(
            amount
        )

    # --------------------------------------------------------
    # PROCESS TRANSACTION
    # --------------------------------------------------------

    def process_transaction(
        self,
        instance
    ):

        total = self.get_total()

        if total <= 0:

            return

        payment_text = (
            self.txt_bayar.text
            .strip()
        )

        if not payment_text:

            show_message(
                "Pembayaran",
                "Masukkan nominal pembayaran."
            )

            return

        payment = safe_int(
            payment_text
        )

        if payment < total:

            show_message(
                "Pembayaran",
                "Nominal pembayaran kurang "
                + format_rupiah(
                    total - payment
                )
            )

            return

        change = (
            payment - total
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # Create transaction snapshot BEFORE clearing cart.
        # ----------------------------------------------------

        cart_snapshot = []

        for item_id, item in (
            self.cart.items()
        ):

            cart_snapshot.append(
                {
                    "id": item_id,
                    "nama": item["nama"],
                    "harga": item["harga"],
                    "jumlah": item["jumlah"],
                    "subtotal": (
                        item["harga"]
                        * item["jumlah"]
                    )
                }
            )

        invoice = make_invoice_number()

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        note = (
            self.txt_catatan.text
            .strip()
        )

        conn = None

        try:

            conn = get_db()

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO transaksi
                (
                    faktur,
                    tanggal,
                    total,
                    bayar,
                    kembali,
                    pembayaran,
                    catatan
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice,
                    timestamp,
                    total,
                    payment,
                    change,
                    self.selected_method,
                    note
                )
            )

            for item in cart_snapshot:

                cursor.execute(
                    """
                    INSERT INTO detail_transaksi
                    (
                        faktur,
                        menu_id,
                        nama,
                        harga,
                        jumlah,
                        subtotal
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        invoice,
                        item["id"],
                        item["nama"],
                        item["harga"],
                        item["jumlah"],
                        item["subtotal"]
                    )
                )

            conn.commit()

        except Exception as error:

            if conn:

                conn.rollback()

            show_message(
                "Transaksi Gagal",
                str(error)
            )

            return

        finally:

            if conn:

                conn.close()

        if hasattr(
            self,
            "payment_popup"
        ):

            self.payment_popup.dismiss()

        # ----------------------------------------------------
        # Clear cart AFTER successful database transaction.
        # ----------------------------------------------------

        self.cart.clear()

        self.update_cart_ui()

        self.show_receipt(
            invoice,
            timestamp,
            total,
            payment,
            change,
            self.selected_method,
            note,
            cart_snapshot
        )

    # --------------------------------------------------------
    # RECEIPT
    # --------------------------------------------------------

    def show_receipt(
        self,
        invoice,
        timestamp,
        total,
        payment,
        change,
        method,
        note,
        items
    ):

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(8)
        )

        receipt = (
            "[b]UNIVERSAL POS[/b]\n"
            "--------------------------------\n"
            "Faktur: "
            + invoice
            + "\n"
            + "Tanggal: "
            + timestamp
            + "\n"
            + "Metode: "
            + method
            + "\n"
            + "--------------------------------\n"
        )

        for item in items:

            receipt += (
                str(item["nama"])
                + "\n"
                + str(item["jumlah"])
                + " x "
                + format_rupiah(
                    item["harga"]
                )
                + " = "
                + format_rupiah(
                    item["subtotal"]
                )
                + "\n"
            )

        receipt += (
            "--------------------------------\n"
            "TOTAL  : "
            + format_rupiah(total)
            + "\n"
            "BAYAR  : "
            + format_rupiah(payment)
            + "\n"
            "KEMBALI: "
            + format_rupiah(change)
            + "\n"
        )

        if note:

            receipt += (
                "Catatan: "
                + note
                + "\n"
            )

        receipt += (
            "--------------------------------\n"
            "Terima kasih telah berbelanja."
        )

        scroll = ScrollView()

        receipt_label = Label(
            text=receipt,
            markup=True,
            color=TEXT,
            font_size=dp(11),
            size_hint_y=None,
            halign="left",
            valign="top"
        )

        receipt_label.bind(
            texture_size=lambda instance,
            value:
            setattr(
                instance,
                "height",
                value[1]
            )
        )

        scroll.add_widget(
            receipt_label
        )

        content.add_widget(
            scroll
        )

        close = RoundedButton(
            text="SELESAI",
            size_hint_y=None,
            height=dp(42),
            bg_color=PRIMARY,
            color=WHITE,
            bold=True
        )

        content.add_widget(
            close
        )

        popup = CustomPopup(
            "Struk Transaksi",
            content,
            size_hint=(
                0.90,
                0.82
            )
        )

        close.bind(
            on_release=popup.dismiss
        )

        popup.open()

    # --------------------------------------------------------
    # POPUPS
    # --------------------------------------------------------

    def open_menu_management(
        self,
        instance
    ):

        widget = MenuManagementWidget()

        popup = CustomPopup(
            "Kelola Produk",
            widget,
            size_hint=(
                0.92,
                0.88
            )
        )

        popup.open()

    def open_riwayat(
        self,
        instance
    ):

        widget = RiwayatWidget()

        popup = CustomPopup(
            "Riwayat Transaksi",
            widget,
            size_hint=(
                0.92,
                0.85
            )
        )

        popup.open()

    def open_laporan(
        self,
        instance
    ):

        widget = LaporanWidget()

        popup = CustomPopup(
            "Laporan Penjualan",
            widget,
            size_hint=(
                0.92,
                0.85
            )
        )

        popup.open()


# ============================================================
# APPLICATION
# ============================================================

class KasirApp(
    App
):

    def build(
        self
    ):

        # ====================================================
        # CRITICAL FIX
        # ====================================================
        # Database is initialized BEFORE KasirScreen.
        #
        # In the old source:
        #
        # build()
        #   -> KasirScreen()
        #   -> on_enter()
        #   -> load_menu()
        #   -> SELECT FROM menu
        #
        # while init_db() was only called later in on_start().
        #
        # This version fixes that order.
        # ====================================================

        try:

            init_db()

            print(
                "DATABASE INITIALIZATION SUCCESS"
            )

        except Exception as error:

            print(
                "DATABASE INITIALIZATION ERROR:",
                repr(error)
            )

            # Show a minimal UI instead of silently
            # failing during application startup.

            error_screen = Screen(
                name="error"
            )

            layout = BoxLayout(
                orientation="vertical",
                padding=dp(20),
                spacing=dp(15)
            )

            title = Label(
                text="UniversalPOS",
                font_size=dp(22),
                bold=True,
                color=PRIMARY,
                size_hint_y=None,
                height=dp(45)
            )

            message = Label(
                text=(
                    "Database gagal diinisialisasi.\n\n"
                    + str(error)
                ),
                color=TEXT,
                halign="center",
                valign="middle"
            )

            message.bind(
                size=message.setter(
                    "text_size"
                )
            )

            layout.add_widget(
                title
            )

            layout.add_widget(
                message
            )

            error_screen.add_widget(
                layout
            )

            manager = ScreenManager()

            manager.add_widget(
                error_screen
            )

            return manager

        # ====================================================
        # CREATE MAIN SCREEN
        # ====================================================

        manager = ScreenManager()

        self.kasir_screen = KasirScreen(
            name="kasir"
        )

        manager.add_widget(
            self.kasir_screen
        )

        return manager

    def on_start(
        self
    ):

        # ====================================================
        # IMPORTANT:
        # Database initialization is NO LONGER done here.
        #
        # It is already completed in build().
        #
        # This prevents the old startup ordering problem.
        # ====================================================

        if platform == "android":

            try:

                from android.permissions import (
                    Permission,
                    request_permissions
                )

                permissions = []

                # Do NOT request storage permissions
                # for SQLite database.
                #
                # SQLite is stored inside user_data_dir.
                #
                # These are kept only for future compatibility
                # with Android versions where they exist.

                if hasattr(
                    Permission,
                    "BLUETOOTH_CONNECT"
                ):

                    permissions.append(
                        Permission.BLUETOOTH_CONNECT
                    )

                if hasattr(
                    Permission,
                    "BLUETOOTH_SCAN"
                ):

                    permissions.append(
                        Permission.BLUETOOTH_SCAN
                    )

                if permissions:

                    request_permissions(
                        permissions
                    )

            except Exception as error:

                print(
                    "ANDROID PERMISSION WARNING:",
                    repr(error)
                )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    KasirApp().run()
